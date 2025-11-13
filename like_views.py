from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from community.models import Like, Post, CustomUser

from job_analysis.utils import jwt_decode, auth_user
from django.forms.models import model_to_dict

import json

# =============================== #
# ======== Like API's ========== #
# =============================== #


@csrf_exempt
@require_http_methods(["GET"])
def list_likes_view(request):
    likes = Like.objects.all()
    likes_data = [model_to_dict(like) for like in likes]
    return JsonResponse(likes_data, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_like_view(request, post_id):
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

    like, created = Like.objects.get_or_create(
        user=user,
        post=post
    )
    if not created:
        like.delete()
        return JsonResponse({'success': True, 'message': 'Like removed successfully.'}, status=200)
    
    return JsonResponse({"success": True, "message": "Like created successfully.", "like": model_to_dict(like)}, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def list_posts_liked_by_user_view(request, user_email):
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

    likes = user.likes.all()
    likes_data = [model_to_dict(like) for like in likes]
    return JsonResponse(likes_data, safe=False)

