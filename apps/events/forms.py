# ── events/forms.py ───────────────────────────────────────────────────────────
from django import forms
from .models import Event, EventRegistration


class EventForm(forms.ModelForm):
    class Meta:
        model  = Event
        fields = ['title', 'description', 'event_type', 'location',
                  'event_date', 'end_date', 'capacity', 'banner', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'event_date':  forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date':    forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model  = EventRegistration
        fields = ['dietary', 'special_needs']


# ── events/urls.py ────────────────────────────────────────────────────────────
# (placed here for compactness)
