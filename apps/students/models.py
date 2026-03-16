"""
students/models.py
Student profile linked 1-to-1 to the User model.
"""

from django.db import models
from django.conf import settings


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id          = models.CharField(max_length=20, unique=True)
    department          = models.CharField(max_length=100)
    current_year        = models.PositiveSmallIntegerField(default=1)
    expected_graduation = models.PositiveIntegerField(null=True, blank=True)
    skills              = models.TextField(blank=True, help_text='Comma-separated skills')
    interests           = models.TextField(blank=True, help_text='Comma-separated interests')
    linkedin_url        = models.URLField(blank=True)
    github_url          = models.URLField(blank=True)
    resume              = models.FileField(upload_to='resumes/', blank=True, null=True)
    is_job_seeking      = models.BooleanField(default=True)

    # Computed
    profile_views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'

    def __str__(self):
        return f"{self.user.get_full_name()} [{self.student_id}]"

    def get_skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def get_interests_list(self):
        return [i.strip() for i in self.interests.split(',') if i.strip()]

    @property
    def profile_completeness(self):
        """Return 0–100 completeness score."""
        fields = [
            bool(self.user.first_name),
            bool(self.user.last_name),
            bool(self.user.email),
            bool(self.user.photo),
            bool(self.department),
            bool(self.skills),
            bool(self.interests),
            bool(self.linkedin_url),
            bool(self.github_url),
            bool(self.resume),
        ]
        return int(sum(fields) / len(fields) * 100)
