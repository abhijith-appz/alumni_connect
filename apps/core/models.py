"""
core/models.py
Shared/utility models: Announcements, Activity log.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Announcement(models.Model):

    class Type(models.TextChoices):
        GENERAL = 'general', _('General')
        URGENT  = 'urgent',  _('Urgent')
        INFO    = 'info',    _('Information')
        EVENT   = 'event',   _('Event')

    class Audience(models.TextChoices):
        ALL      = 'all',      _('All Users')
        STUDENTS = 'students', _('Students Only')
        ALUMNI   = 'alumni',   _('Alumni Only')

    title      = models.CharField(max_length=200)
    message    = models.TextField()
    type       = models.CharField(max_length=10, choices=Type.choices, default=Type.GENERAL)
    audience   = models.CharField(max_length=10, choices=Audience.choices, default=Audience.ALL)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='announcements',
    )
    views      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ActivityLog(models.Model):
    """Lightweight audit log for admin reporting."""
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
    )
    action     = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.action}"
