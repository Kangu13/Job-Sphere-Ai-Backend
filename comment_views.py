from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import json

from community.models import Comment, Post, CustomUser

from job_analysis.utils import jwt_decode, auth_user
from django.forms.models import model_to_dict

@csrf_exempt
@require_http_methods(["POST"])
def create_comment_view(request, post_id):
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
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    content = data.get('content')

    if not content:
        return JsonResponse({'success': False, 'message': 'Content is required.'}, status=400)

    try:
        comment = Comment.objects.create(
            user=user,
            post=post,
            content=content
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error creating comment: {e}"}, status=500)

    return JsonResponse({"success": True, "message": "Comment created successfully.", "comment": model_to_dict(comment)}, status=200)

@csrf_exempt
@require_http_methods(["PUT"])
def update_comment_view(request, comment_id):
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

    if comment.user != user:
        return JsonResponse({"success": False, "message": "You are not authorized to update this comment."}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    content = data.get('content')

    if not content:
        return JsonResponse({'success': False, 'message': 'Content is required.'}, status=400)

    comment.content = content
    comment.save()

    return JsonResponse({"success": True, "message": "Comment updated successfully.", "comment": model_to_dict(comment)}, status=200)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_comment_view(request, comment_id):
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

    if comment.user != user:
        return JsonResponse({"success": False, "message": "You are not authorized to delete this comment."}, status=403)

    comment.delete()

    return JsonResponse({"success": True, "message": "Comment deleted successfully."}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def list_comments_for_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)

    comments = post.comments.all()
    comments_data = [model_to_dict(comment) for comment in comments]
    return JsonResponse(comments_data, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def retrieve_comment_view(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"success": False, "message": "Comment not found."}, status=404)
    return JsonResponse(model_to_dict(comment))

