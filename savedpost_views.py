from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from community.models import SavedPost, Post, CustomUser
from job_analysis.utils import jwt_decode, auth_user
from django.forms.models import model_to_dict

import json

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def list_all_saved_posts(request):
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

    saved_posts = SavedPost.objects.all()
    saved_posts_data = [model_to_dict(saved_post) for saved_post in saved_posts]
    return JsonResponse(saved_posts_data, safe=False)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_saved_post(request):
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

    data = json.loads(request.body)
    post_id = data.get('post_id')
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)

    saved_post = SavedPost.objects.create(user=user, post=post)
    return JsonResponse(model_to_dict(saved_post), status=201)

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def remove_saved_post(request, post_id):
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
        saved_post = SavedPost.objects.get(user=user, post__id=post_id)
    except SavedPost.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Saved Post not found.'}, status=404)

    saved_post.delete()
    return JsonResponse({'success': True, 'message': 'Saved Post removed.'}, status=200)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def list_saved_posts_by_user(request, user_email):
    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    saved_posts = user.saved_posts.all()
    saved_posts_data = [model_to_dict(saved_post) for saved_post in saved_posts]
    return JsonResponse(saved_posts_data, safe=False)
