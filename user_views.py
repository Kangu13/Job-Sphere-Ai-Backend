import json
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods

from job_analysis.models import CustomUser

from job_analysis.utils import jwt_encode, jwt_decode, auth_user

from django.forms.models import model_to_dict
from django.conf import settings
import random
from job_analysis.models import OTP
from django.core.mail import send_mail


# =============================== #
# ========== User API's ========== #
# =============================== #
@csrf_exempt
@require_http_methods(["POST"])
def user_register(request):
    try:
        data = json.loads(request.body)
        required_fields = ['email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return JsonResponse(
                {'status': 'failed', 'message': f'Missing mandatory fields: {", ".join(missing_fields)}.'},
                status=400
            )
      
        
        email = data.get('email').strip()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse(
                {'status': 'failed', 'message': 'User already exists!'},
                status=409
            )

        username = email.split('@')[0]

        hashed_password = make_password(password)
        encoded_token = jwt_encode(email)
        CustomUser.objects.create(email=email, password=hashed_password, first_name=first_name,
                            last_name=last_name, username=username, phone_number=phone_number,
                            profile_picture='profile_pictures/default_male_image.png')

        subject = 'Thank you for registering!'
        message = '<div style="display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 20px; border: 1px solid #ccc; border-radius: 10px;">' \
                  '<h1 style="color: #333; font-weight: 600; font-size: 24px; margin-bottom: 10px;">Thank you for registering!</h1>' \
                  '<p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 20px;">We are excited to have you on board.</p>' \
                  '</div>'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=message
        )

        return JsonResponse(
            {'status': 'success',
             'message': 'User registered successfully',
             'token': str(encoded_token)},
            status=201
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'status': 'failed', 'message': 'Invalid JSON in request body.'},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'failed', 'message': f'Error: {str(e)}'},
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    try:
        data = json.loads(request.body)

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse(
                {'status': 'failed', 'message': 'Missing email or password.'},
                status=400
            )

        email = email.strip()
        password = password.strip()

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            token = jwt_encode(email)
            subject = 'Login successful!'
            message = '<p>You have successfully logged in to our platform.</p>' \
                      '<p>Thanks for using our service.</p>' \
                      '<p>Best regards,</p>' \
                      '<p>The Team</p>'
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=message
            )
            return JsonResponse(
                {'status': 'success', 'message': 'Login successful.', 'token': str(token)},
                status=200
            )
        else:
            return JsonResponse(
                {'status': 'failed', 'message': 'Invalid login credentials.'},
                status=401
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {'status': 'failed', 'message': 'Invalid JSON in request body.'},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'failed', 'message': f'Error: {str(e)}'},
            status=500
        )

@csrf_exempt
@require_http_methods(["GET"])
def get_user_details(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'status': 'failed', 'message': 'Authentication header is required.'}, status=401)

    token = bearer.split()[1]

    if not auth_user(token):
        return JsonResponse({'status': 'failed', 'message': 'Invalid token data.'}, status=401)

    decoded_token = jwt_decode(token)
    email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'User not found.'}, status=404)

    user_data = model_to_dict(user)
    user_data['profile_picture'] = user.profile_picture.url if user.profile_picture else None

    return JsonResponse({'status': 'success', 'message': 'User details retrieved successfully.', 'user': user_data}, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def edit_user_details_view(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)

    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)

    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    data = request.POST
    if data.get('first_name'):
        user.first_name = data.get('first_name')
    if data.get('last_name'):
        user.last_name = data.get('last_name')
    if data.get('username'):
        user.username = data.get('username')
    if data.get('phone_number'):
        user.phone_number = data.get('phone_number')

    user.save()

    user_details = model_to_dict(user, exclude=['password'])
    user_details['profile_picture'] = str(user.profile_picture.url)

    send_mail(
        'User details edited successfully!',
        'Your user details have been successfully edited.',
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )

    return JsonResponse({"success": True, "message": "User details edited successfully.", "user_details": user_details}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def edit_profile_picture_view(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)

    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)

    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    uploaded_image = request.FILES.get('profile_picture')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    if not uploaded_image:
        return JsonResponse({'success': False, 'message': 'No profile picture uploaded.'}, status=400)

    try:
        user.profile_picture.save(uploaded_image.name, uploaded_image)
        user.save()
        user_details = model_to_dict(user, exclude=['password'])
        user_details['profile_picture'] = str(user.profile_picture.url)
        send_mail(
            'Profile picture edited successfully!',
            'Your profile picture has been successfully edited.',
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=False,
        )
        return JsonResponse({"success": True, "message": "Profile picture edited successfully.", "user_details": user_details}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error saving profile picture: {str(e)}'}, status=500)

@csrf_exempt
def forgot_password_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request, USE POST.'}, status=405)
    try:
        user_email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

        otp = request.POST.get('otp')

        if not otp:
            OTP.objects.filter(user=user).delete()
            code = str(random.randint(0, 9999)).zfill(4)
            OTP.objects.create(user=user, code=code)
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'OTP sent to your email.'}, status=200)

        otp = OTP.objects.filter(user=user, code=otp).first()
        if not otp:
            return JsonResponse({'success': False, 'message': 'Invalid OTP.'}, status=401)
        if otp.is_expired(expiry_minutes=5):
            otp.delete()
            return JsonResponse({'success': False, 'message': 'OTP has expired.'}, status=401)

        new_password = request.POST.get('new_password', '').strip()
        if not new_password:
            return JsonResponse({'success': True, 'message': 'OTP verified successfully.'}, status=200)

        user.set_password(new_password)
        user.save()
        otp.delete()
        send_mail(
            'Password Reset Successful!',
            'Your password has been successfully reset.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'Password reset successfully.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@csrf_exempt
def change_password(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)

    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)

    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')
    
    try:
        data = json.loads(request.body)
        current_password = data.get('current')
        new_password = data.get('new')
        confirm_password = data.get('confirm')

        if not all([current_password, new_password, confirm_password]):
            return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)

        if new_password != confirm_password:
            return JsonResponse({'success': False, 'message': 'New passwords do not match.'}, status=400)

        try:
            user = CustomUser.objects.get(email=user_email)
            if not user.check_password(current_password):
                return JsonResponse({'success': False, 'message': 'Current password is incorrect.'}, status=400)

            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Password updated successfully.'})
            
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def change_email_view(request):
    try:
        data = json.loads(request.body)
        current_email = data.get('current_email')
        new_email = data.get('new_email')

        if not current_email or not new_email:
            return JsonResponse({'success': False, 'message': 'Both current and new email are required.'}, status=400)

        if current_email == new_email:
            return JsonResponse({'success': False, 'message': 'New email must be different from the current email.'}, status=400)

        try:
            user = CustomUser.objects.get(email=current_email)
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User with the current email does not exist.'}, status=404)

        if CustomUser.objects.filter(email=new_email).exists():
            return JsonResponse({'success': False, 'message': 'New email is already in use by another user.'}, status=409)

        user.email = new_email
        user.save()

        return JsonResponse({'success': True, 'message': 'Email updated successfully.'}, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)