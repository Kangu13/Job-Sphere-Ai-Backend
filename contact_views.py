import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from job_analysis.models import ContactUs

@csrf_exempt
@require_http_methods(["POST"])
def contact_us(request):
    try:
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Validate required fields
        if not all([name, email, subject, message]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            }, status=400)

        # Save to database
        ContactUs.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # Send email to user
        try:
            user_html_content = render_to_string('email_templates/contact_us.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message
            })

            user_email = EmailMessage(
                subject="YOUR CONTACT FORM SUBMITTED SUCCESSFULLY",
                body=user_html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            user_email.content_subtype = "html"
            user_email.send(fail_silently=False)

            # Send email to admin
            admin_html_content = render_to_string('email_templates/admin_contact_us.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message
            })

            admin_email = EmailMessage(
                subject="USER WANTS TO CONTACT US",
                body=admin_html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER]
            )
            admin_email.content_subtype = "html"
            admin_email.send(fail_silently=False)

            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully'
            }, status=200)

        except Exception as e:
            # If email fails but data is saved, still return success
            return JsonResponse({
                'success': True,
                'message': 'Message saved successfully but email sending failed'
            }, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)