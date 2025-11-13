from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import CustomUser, ResumeAnalysis, JobDescription

@login_required
@require_http_methods(["GET"])
def admin_dashboard(request):
    if not request.user.is_admin:
        return JsonResponse({"success": False, "message": "Unauthorized access"}, status=403)
    
    # Get all analyses with related user and job description
    analyses = ResumeAnalysis.objects.select_related('user', 'job_description').all()
    
    # Prepare data for response
    analysis_data = []
    for analysis in analyses:
        analysis_data.append({
            "user_email": analysis.user.email,
            "job_title": analysis.job_description.title,
            "company": analysis.job_description.company_name,
            "match_percentage": analysis.match_percentage,
            "missing_skills": analysis.missing_skills,
            "extra_skills": analysis.extra_skills,
            "analyzed_at": analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S'),
            "user_details": {
                "first_name": analysis.user.first_name,
                "last_name": analysis.user.last_name,
                "phone_number": analysis.user.phone_number,
                "location": f"{analysis.user.city}, {analysis.user.country}" if analysis.user.city else "N/A"
            }
        })
    
    return JsonResponse({
        "success": True,
        "message": "Analysis data retrieved successfully",
        "analyses": analysis_data
    }, status=200)

@login_required
@require_http_methods(["GET"])
def get_analysis_details(request, analysis_id):
    if not request.user.is_admin:
        return JsonResponse({"success": False, "message": "Unauthorized access"}, status=403)
    
    try:
        analysis = ResumeAnalysis.objects.select_related('user', 'job_description').get(id=analysis_id)
        return JsonResponse({
            "success": True,
            "analysis": {
                "user": {
                    "email": analysis.user.email,
                    "full_name": f"{analysis.user.first_name} {analysis.user.last_name}",
                    "phone": analysis.user.phone_number,
                    "location": f"{analysis.user.city}, {analysis.user.country}"
                },
                "job_description": {
                    "title": analysis.job_description.title,
                    "company": analysis.job_description.company_name,
                    "posted_at": analysis.job_description.posted_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "description": analysis.job_description.description
                },
                "match_details": {
                    "match_percentage": analysis.match_percentage,
                    "missing_skills": analysis.missing_skills,
                    "extra_skills": analysis.extra_skills,
                    "analysis_details": analysis.analysis_details
                },
                "analyzed_at": analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=200)
    except ResumeAnalysis.DoesNotExist:
        return JsonResponse({"success": False, "message": "Analysis not found"}, status=404)

@login_required
@require_http_methods(["GET"])
def search_analyses(request):
    if not request.user.is_admin:
        return JsonResponse({"success": False, "message": "Unauthorized access"}, status=403)
    
    query = request.GET.get('q', '')
    
    # Search across multiple fields
    analyses = ResumeAnalysis.objects.select_related('user', 'job_description').filter(
        Q(user__email__icontains=query) |
        Q(job_description__title__icontains=query) |
        Q(job_description__company_name__icontains=query) |
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query)
    )
    
    analysis_data = []
    for analysis in analyses:
        analysis_data.append({
            "id": analysis.id,
            "user_email": analysis.user.email,
            "job_title": analysis.job_description.title,
            "company": analysis.job_description.company_name,
            "match_percentage": analysis.match_percentage,
            "analyzed_at": analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({
        "success": True,
        "message": "Search results retrieved successfully",
        "results": analysis_data
    }, status=200)
