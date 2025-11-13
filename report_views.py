from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from community.models import Report, Post, Comment, CustomUser
from job_analysis.utils import jwt_decode, auth_user
from django.forms.models import model_to_dict

import json

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def list_all_reports_view(request):
    reports = Report.objects.all()
    reports_data = [model_to_dict(report) for report in reports]
    return JsonResponse(reports_data, safe=False)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def retrieve_report_view(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Report not found.'}, status=404)
    return JsonResponse(model_to_dict(report))

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_report_view(request):
    data = json.loads(request.body)
    user = auth_user(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    if 'post_id' in data:
        try:
            post = Post.objects.get(id=data['post_id'])
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)
        report = Report(user=user, post=post, reason=data['reason'], description=data.get('description'))
        report.save()
        return JsonResponse(model_to_dict(report))
    elif 'comment_id' in data:
        try:
            comment = Comment.objects.get(id=data['comment_id'])
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Comment not found.'}, status=404)
        report = Report(user=user, comment=comment, reason=data['reason'], description=data.get('description'))
        report.save()
        return JsonResponse(model_to_dict(report))
    else:
        return JsonResponse({'success': False, 'message': 'No target specified.'}, status=400)

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def update_report_view(request, report_id):
    data = json.loads(request.body)
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Report not found.'}, status=404)
    user = auth_user(request)
    if not user or report.user != user:
        return JsonResponse({'success': False, 'message': 'User not found or not authorized.'}, status=404)
    report.reason = data.get('reason', report.reason)
    report.description = data.get('description', report.description)
    report.save()
    return JsonResponse(model_to_dict(report))

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_report_view(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Report not found.'}, status=404)
    user = auth_user(request)
    if not user or report.user != user:
        return JsonResponse({'success': False, 'message': 'User not found or not authorized.'}, status=404)
    report.delete()
    return JsonResponse({'success': True, 'message': 'Report deleted successfully'})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def list_reports_for_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)
    reports = post.reports.all()
    reports_data = [model_to_dict(report) for report in reports]
    return JsonResponse(reports_data, safe=False)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def list_reports_for_comment_view(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Comment not found.'}, status=404)
    reports = comment.reports.all()
    reports_data = [model_to_dict(report) for report in reports]
    return JsonResponse(reports_data, safe=False)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def list_reports_by_user_view(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    reports = user.reports.all()
    reports_data = [model_to_dict(report) for report in reports]
    return JsonResponse(reports_data, safe=False)
