"""
alumni/models.py
Alumni profile, work experience, and education models.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AlumniProfile(models.Model):

    class Status(models.TextChoices):
        PENDING  = 'pending',  _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    user             = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alumni_profile'
    )
    department       = models.CharField(max_length=100)
    graduation_year  = models.PositiveIntegerField()
    company          = models.CharField(max_length=150, blank=True)
    current_position = models.CharField(max_length=150, blank=True)
    location         = models.CharField(max_length=100, blank=True)
    linkedin_url     = models.URLField(blank=True)
    skills           = models.TextField(blank=True, help_text='Comma-separated')
    bio              = models.TextField(blank=True)
    is_mentor_available = models.BooleanField(default=False)
    email_visible    = models.BooleanField(default=False)

    status           = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    approved_at      = models.DateTimeField(null=True, blank=True)
    approved_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_alumni'
    )

    profile_views    = models.PositiveIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alumni_profiles'
        verbose_name = 'Alumni Profile'
        ordering = ['-graduation_year']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.graduation_year})"

    def get_skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED


class WorkExperience(models.Model):
    alumni          = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='experience')
    title           = models.CharField(max_length=150)
    company         = models.CharField(max_length=150)
    location        = models.CharField(max_length=100, blank=True)
    start_year      = models.PositiveIntegerField()
    end_year        = models.PositiveIntegerField(null=True, blank=True)
    is_current      = models.BooleanField(default=False)
    description     = models.TextField(blank=True)

    class Meta:
        db_table = 'alumni_work_experience'
        ordering = ['-start_year']

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Education(models.Model):
    alumni          = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='education')
    degree          = models.CharField(max_length=150)
    institution     = models.CharField(max_length=200)
    year            = models.PositiveIntegerField()
    description     = models.TextField(blank=True)

    class Meta:
        db_table = 'alumni_education'
        ordering = ['-year']
