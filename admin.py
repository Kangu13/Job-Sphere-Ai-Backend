from django.contrib import admin
from .models import CustomUser, JobDescription, OTP, Resume, ResumeAnalysis, Feedback

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'is_customer', 'last_login')
    list_filter = ('is_admin', 'is_customer', 'is_email', 'two_factor')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-last_login',)

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'posted_at')
    list_filter = ('posted_at',)
    search_fields = ('title', 'company_name')
    ordering = ('-posted_at',)

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'code')
    ordering = ('-created_at',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('user__email',)
    ordering = ('-uploaded_at',)

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_description', 'match_percentage', 'analyzed_at')
    list_filter = ('analyzed_at',)
    search_fields = ('user__email', 'job_description__title')
    ordering = ('-analyzed_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'publish', 'created_at')
    list_filter = ('rating', 'publish', 'created_at')
    search_fields = ('user__email', 'comment')
    ordering = ('-created_at',)

# Unregister the default admin registrations
admin.site.unregister(CustomUser)
admin.site.unregister(JobDescription)
admin.site.unregister(OTP)
admin.site.unregister(Resume)
admin.site.unregister(ResumeAnalysis)
admin.site.unregister(Feedback)

# Register with the enhanced configurations
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(JobDescription, JobDescriptionAdmin)
admin.site.register(OTP, OTPAdmin)
admin.site.register(Resume, ResumeAdmin)
admin.site.register(ResumeAnalysis, ResumeAnalysisAdmin)
admin.site.register(Feedback, FeedbackAdmin)
