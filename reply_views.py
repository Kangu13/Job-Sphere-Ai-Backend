from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from community.models import Reply, Comment, CustomUser

from job_analysis.utils import jwt_decode, auth_user
from django.forms.models import model_to_dict

import json

@csrf_exempt
@require_http_methods(["GET"])
def list_all_replies(request):
    replies = Reply.objects.all()
    replies_data = [model_to_dict(reply) for reply in replies]
    return JsonResponse(replies_data, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def retrieve_reply(request, reply_id):
    try:
        reply = Reply.objects.get(id=reply_id)
    except Reply.DoesNotExist:
        return JsonResponse({"success": False, "message": "Reply not found."}, status=404)
    return JsonResponse(model_to_dict(reply))

@csrf_exempt
@require_http_methods(["POST"])
def create_reply(request, comment_id):
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
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Comment not found.'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    content = data.get('content')

    if not content:
        return JsonResponse({'success': False, 'message': 'Content is required.'}, status=400)

    try:
        reply = Reply.objects.create(
            user=user,
            comment=comment,
            content=content
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error creating reply: {e}"}, status=500)

    return JsonResponse({"success": True, "message": "Reply created successfully.", "reply": model_to_dict(reply)}, status=200)

@csrf_exempt
@require_http_methods(["PUT"])
def update_reply(request, reply_id):
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
        reply = Reply.objects.get(id=reply_id)
    except Reply.DoesNotExist:
        return JsonResponse({"success": False, "message": "Reply not found."}, status=404)

    if reply.user != user:
        return JsonResponse({"success": False, "message": "You can only update your own replies."}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    content = data.get('content')

    if not content:
        return JsonResponse({'success': False, 'message': 'Content is required.'}, status=400)

    reply.content = content
    reply.save()

    return JsonResponse({"success": True, "message": "Reply updated successfully.", "reply": model_to_dict(reply)}, status=200)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_reply(request, reply_id):
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
        reply = Reply.objects.get(id=reply_id)
    except Reply.DoesNotExist:
        return JsonResponse({"success": False, "message": "Reply not found."}, status=404)

    if reply.user != user:
        return JsonResponse({"success": False, "message": "You can only delete your own replies."}, status=403)

    reply.delete()

    return JsonResponse({"success": True, "message": "Reply deleted successfully."}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def list_replies_for_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"success": False, "message": "Comment not found."}, status=404)
    replies = comment.replies.all()
    replies_data = [model_to_dict(reply) for reply in replies]
    return JsonResponse(replies_data, safe=False)

