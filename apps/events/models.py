"""
events/models.py
Alumni events, registrations, and agenda items.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Event(models.Model):

    class EventType(models.TextChoices):
        ON_CAMPUS = 'on_campus', _('On Campus')
        ONLINE    = 'online',    _('Online')
        HYBRID    = 'hybrid',    _('Hybrid')

    title        = models.CharField(max_length=200)
    description  = models.TextField()
    event_type   = models.CharField(max_length=15, choices=EventType.choices, default=EventType.ON_CAMPUS)
    location     = models.CharField(max_length=300, help_text='Venue or online link')
    event_date   = models.DateTimeField()
    end_date     = models.DateTimeField(null=True, blank=True)
    capacity     = models.PositiveIntegerField(default=200)
    banner       = models.ImageField(upload_to='events/', blank=True, null=True)
    is_published = models.BooleanField(default=True)

    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_events'
    )
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events'
        ordering = ['event_date']

    def __str__(self):
        return self.title

    @property
    def registered_count(self):
        return self.registrations.count()

    @property
    def spots_left(self):
        return max(0, self.capacity - self.registered_count)

    @property
    def is_full(self):
        return self.registered_count >= self.capacity


class AgendaItem(models.Model):
    event       = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='agenda_items')
    time        = models.CharField(max_length=20)
    title       = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'event_agenda'
        ordering = ['order', 'time']


class EventRegistration(models.Model):
    event      = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    dietary    = models.CharField(max_length=30, blank=True)
    special_needs = models.CharField(max_length=200, blank=True)
    attended   = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_registrations'
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.event.title}"
