from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from community.models import Post
from job_analysis.models import CustomUser

import json

from job_analysis.utils import jwt_encode, jwt_decode, auth_user


@csrf_exempt
@require_http_methods(["GET"])
def list_all_posts(request):
    try:
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

        posts = Post.objects.all().order_by('-created_at')
        post_list = []
        for post in posts:
            comments = []
            for comment in post.comments.all():
                replies = [{
                    'id': reply.id,
                    'user': reply.user.first_name,
                    'content': reply.content,
                    'created_at': reply.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                } for reply in comment.replies.all()]
                comment_data = {
                    'id': comment.id,
                    'user': comment.user.first_name,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    'replies': replies
                }
                comments.append(comment_data)
            post_data = {
                'id': post.id,
                'user': post.user.email,
                'title': post.title,
                'content': post.content,
                'image': post.image.url if post.image else None,
                'created_at': post.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'updated_at': post.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'comments': comments,
                'like_count': post.likes.count(),
                'user_liked': post.likes.filter(user=user).exists()
            }
            post_list.append(post_data)
        return JsonResponse({'success': True, 'message': 'Posts retrieved successfully', 'posts': post_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Error retrieving posts: {e}"}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_post_by_id(request, post_id):
    try:
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

        post = Post.objects.get(id=post_id)
        comments = []
        for comment in post.comments.all():
            replies = []
            for reply in comment.replies.all():
                replies.append({
                    'id': reply.id,
                    'user': reply.user.first_name,
                    'content': reply.content,
                    'created_at': reply.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                })
            comments.append({
                'id': comment.id,
                'user': comment.user.first_name,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'replies': replies
            })
        post_data = {
            'post': {
                'id': post.id,
                'user': post.user.email,
                'title': post.title,
                'content': post.content,
                'image': post.image.url if post.image else None,
                'created_at': post.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'updated_at': post.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            },
            'comments': comments,
            'like_count': post.likes.count(),
            'user_liked': post.likes.filter(user=user).exists()
        }
        return JsonResponse({'success': True, 'message': 'Post retrieved successfully', 'post': post_data}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Error retrieving post: {e}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_post(request):
    try:
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

        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        post = Post.objects.create(user=user, title=title, content=content, image=image)
        post_data = {
            'post': post.id,
            'user': post.user.email,
            'title': post.title,
            'content': post.content,
            'image': post.image.url if post.image else None,
            'created_at': post.created_at,
            'updated_at': post.updated_at
        }
        return JsonResponse({'success': True, 'message': 'Post created successfully', 'post': post_data}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Error creating post: {e}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_post(request, post_id):
    try:
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

        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if not title:
            return JsonResponse({'success': False, 'message': 'Title is required.'}, status=400)
        
        post = Post.objects.get(id=post_id, user=user)
        post.title = title
        post.content = content
        if 'image' in request.FILES:
            post.image = request.FILES.get('image')
        post.save()

        post_data = {
            'id': post.id,
            'user': post.user.email,
            'title': post.title,
            'content': post.content,
            'image': post.image.url if post.image else None,
            'created_at': post.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'updated_at': post.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        return JsonResponse({'success': True, 'message': 'Post updated successfully', 'post': post_data}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found or user not authorized'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Error updating post: {e}"}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_post(request, post_id):
    try:
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
            post = Post.objects.get(id=post_id, user=user)
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)

        if post.user != user:
            return JsonResponse({'success': False, 'message': 'User not authorized'}, status=403)

        post.delete()
        return JsonResponse({'success': True, 'message': 'Post deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Error deleting post: {e}"}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def list_posts_by_user(request):
    try:
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
        
        posts = Post.objects.filter(user=user)
        post_list = [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'created_at': post.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'updated_at': post.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'image': post.image.url if post.image else None
            }
            for post in posts
        ]
        return JsonResponse({'success': True, 'message': 'Posts retrieved successfully', 'posts': post_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Error retrieving posts: {e}"}, status=500)

