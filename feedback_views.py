# feedback/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db.models import Avg, Count

from job_analysis.models import CustomUser, Feedback
from job_analysis.utils import jwt_decode, auth_user

# =============================== #
# ======== Feedback API's ======= #
# =============================== #
@csrf_exempt
@require_http_methods(["POST"])
def add_feedback_view(request):
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

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    comment = data.get('comment', '').strip()
    rating = data.get('rating')

    if not comment or len(comment) < 10:
        return JsonResponse({'success': False, 'message': 'Comment must be at least 10 characters.'}, status=400)

    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return JsonResponse({'success': False, 'message': 'Rating must be between 1 and 5.'}, status=400)

    try:
        feedback = Feedback.objects.create(
            user=user,
            comment=comment,
            rating=rating
        )
        feedback_data = {
            "id": feedback.id,
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "username": user.username,
            },
            "comment": feedback.comment,
            "rating": feedback.rating,
            "publish": feedback.publish,
            "created_at": feedback.created_at,
        }
        return JsonResponse({
            "success": True, 
            "message": "Feedback added successfully.", 
            "feedback": feedback_data
        }, status=201)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error adding feedback: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def toggle_publish_feedback_view(request):
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

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    feedback_id = data.get('feedback_id')

    if not feedback_id:
        return JsonResponse({'success': False, 'message': 'Feedback id is required.'}, status=400)

    try:
        feedback = Feedback.objects.get(id=feedback_id, user=user)
        feedback.publish = not feedback.publish
        feedback.save()
        return JsonResponse({
            "success": True, 
            "message": "Feedback publish status toggled successfully.", 
            "publish": feedback.publish
        }, status=200)
    except Feedback.DoesNotExist:
        return JsonResponse({"success": False, "message": "Feedback not found."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_all_feedbacks_view(request):
    try:
        feedbacks = Feedback.objects.all().order_by('-created_at')
        feedbacks_data = []
        for f in feedbacks:
            feedbacks_data.append({
                "id": f.id,
                "user": {
                    "email": f.user.email,
                    "first_name": f.user.first_name,
                    "username": f.user.username,
                },
                "comment": f.comment,
                "rating": f.rating,
                "publish": f.publish,
                "created_at": f.created_at,
            })
        return JsonResponse({
            "success": True, 
            "message": "All feedbacks fetched successfully.", 
            "feedbacks": feedbacks_data
        })
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@require_http_methods(["GET"])
def get_feedbacks_view(request):
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
        feedbacks = Feedback.objects.filter(user=user).order_by('-created_at')
        feedbacks_data = []
        for f in feedbacks:
            feedbacks_data.append({
                "id": f.id,
                "comment": f.comment,
                "rating": f.rating,
                "publish": f.publish,
                "created_at": f.created_at,
            })
        return JsonResponse({
            "success": True, 
            "message": "Feedbacks fetched successfully.", 
            "feedbacks": feedbacks_data
        }, status=200)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@require_http_methods(["GET"])
def feedback_stats_view(request):
    try:
        published_feedbacks = Feedback.objects.filter(publish=True)
        avg_rating = published_feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
        count = published_feedbacks.count()
        
        return JsonResponse({
            "success": True,
            "stats": {
                "average_rating": round(float(avg_rating), 1),
                "total_feedbacks": count,
                "rating_distribution": {
                    1: published_feedbacks.filter(rating=1).count(),
                    2: published_feedbacks.filter(rating=2).count(),
                    3: published_feedbacks.filter(rating=3).count(),
                    4: published_feedbacks.filter(rating=4).count(),
                    5: published_feedbacks.filter(rating=5).count(),
                }
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
