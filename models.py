from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

LOGIN_BY = {
    (1, 'General'),
    (2, 'Guest'),
    (3, 'Google'),
    (4, 'Facebook')
}

class CustomUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, default="")
    last_name = models.CharField(max_length=255, default="")
    username = models.CharField(max_length=255, default="", blank=True, null=True)
    phone_number = models.CharField(max_length=255, default="", blank=True, null=True)
    dob = models.DateField(default=None, blank=True, null=True)
    marital_status = models.CharField(max_length=255, default="", blank=True, null=True)
    nationality = models.CharField(max_length=255, default="", blank=True, null=True)
    gender = models.CharField(max_length=255, default="", blank=True, null=True)
    country = models.CharField(max_length=255, default="", blank=True, null=True)
    city = models.CharField(max_length=255, default="", blank=True, null=True)
    address = models.TextField(default="", blank=True, null=True)
    zip_code = models.CharField(max_length=255, default="", blank=True, null=True)
    is_admin = models.BooleanField('Is admin', default=False)
    is_customer = models.BooleanField('Is customer', default=False)
    is_email = models.BooleanField('Is email', default=False)
    login_by = models.IntegerField(choices=LOGIN_BY, default=1, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    two_factor = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default="", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    


class JobDescription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="job_descriptions", unique=False)
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    skills_required = models.TextField(blank=True, null=True)
    experience_required = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.company_name if self.company_name else 'N/A'}"

class Resume(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="resume", unique=False)
    summary = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    languages = models.TextField(blank=True, null=True)
    resume_file = models.FileField(upload_to="resumes/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Resume"

class ResumeAnalysis(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="resume_analyses", unique=False)
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name="analyses")
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="analyses")
    match_percentage = models.FloatField()
    missing_skills = models.TextField(blank=True, null=True)
    extra_skills = models.TextField(blank=True, null=True)
    analysis_details = models.TextField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Analysis for {self.job_description.title}"
    
class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    publish = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback by {self.user.username} - {self.rating} Stars"
    

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self, expiry_minutes=5):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=expiry_minutes)

class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.name