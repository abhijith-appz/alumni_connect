"""
jobs/models.py
Job postings by alumni and internship applications.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Job(models.Model):

    class Type(models.TextChoices):
        FULL_TIME  = 'Full Time',  _('Full Time')
        PART_TIME  = 'Part Time',  _('Part Time')
        INTERNSHIP = 'Internship', _('Internship')
        CONTRACT   = 'Contract',   _('Contract')
        REMOTE     = 'Remote',     _('Remote')

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        CLOSED = 'closed', _('Closed')
        DRAFT  = 'draft',  _('Draft')

    posted_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )
    title        = models.CharField(max_length=200)
    company      = models.CharField(max_length=150)
    location     = models.CharField(max_length=150)
    job_type     = models.CharField(max_length=15, choices=Type.choices, default=Type.FULL_TIME)
    domain       = models.CharField(max_length=80, blank=True)
    salary       = models.CharField(max_length=80, blank=True)
    experience   = models.CharField(max_length=80, blank=True)
    description  = models.TextField()
    requirements = models.TextField(blank=True)
    skills       = models.CharField(max_length=400, blank=True, help_text='Comma-separated')
    apply_link   = models.CharField(max_length=300, blank=True)
    deadline     = models.DateField(null=True, blank=True)
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    views        = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} @ {self.company}"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    def get_skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def get_requirements_list(self):
        return [r.strip() for r in self.requirements.split('\n') if r.strip()]

    @property
    def applications_count(self):
        return self.applications.count()


class JobApplication(models.Model):

    class Status(models.TextChoices):
        PENDING   = 'pending',   _('Pending')
        REVIEWED  = 'reviewed',  _('Reviewed')
        SHORTLIST = 'shortlist', _('Shortlisted')
        REJECTED  = 'rejected',  _('Rejected')

    job          = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    cover_letter = models.TextField(blank=True)
    resume       = models.FileField(upload_to='applications/', blank=True, null=True)
    status       = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    applied_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_applications'
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.get_full_name()} → {self.job.title}"


class SavedJob(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    job        = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_jobs'
        unique_together = ('user', 'job')
