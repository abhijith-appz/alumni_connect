from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        ALUMNI  = 'alumni',  _('Alumni')
        STAFF   = 'staff',   _('Staff')
        ADMIN   = 'admin',   _('Admin')

    role  = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio   = models.TextField(blank=True)

    notif_new_jobs    = models.BooleanField(default=True)
    notif_messages    = models.BooleanField(default=True)
    notif_events      = models.BooleanField(default=True)
    notif_connections = models.BooleanField(default=True)
    notif_ai          = models.BooleanField(default=True)
    notif_system      = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'accounts_user'
        verbose_name = 'User'
        ordering     = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_alumni(self):
        return self.role == self.Role.ALUMNI

    @property
    def is_staff_member(self):
        return self.role in (self.Role.STAFF, self.Role.ADMIN)

    def get_dashboard_url(self):
        if self.is_student:
            return '/student/dashboard/'
        elif self.is_alumni:
            return '/alumni/dashboard/'
        return '/staff/dashboard/'

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/images/default_avatar.png'

    @property
    def display_name(self):
        return self.get_full_name() or self.username


class Notification(models.Model):

    class Type(models.TextChoices):
        JOB     = 'job',     _('Job')
        EVENT   = 'event',   _('Event')
        MESSAGE = 'message', _('Message')
        ALUMNI  = 'alumni',  _('Alumni')
        SYSTEM  = 'system',  _('System')
        AI      = 'ai',      _('AI')

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type       = models.CharField(max_length=15, choices=Type.choices, default=Type.SYSTEM)
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    link       = models.CharField(max_length=300, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.type}] {self.title} → {self.user.username}"

    @classmethod
    def create(cls, user, type, title, message, link=''):
        return cls.objects.create(
            user=user, type=type, title=title,
            message=message, link=link,
        )

    @classmethod
    def unread_count(cls, user):
        return cls.objects.filter(user=user, is_read=False).count()
