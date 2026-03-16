# ── alumni/forms.py ───────────────────────────────────────────────────────────
from django import forms
from .models import AlumniProfile, WorkExperience
from apps.accounts.forms import DEPARTMENTS


class AlumniProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name  = forms.CharField(max_length=50)
    email      = forms.EmailField()

    class Meta:
        model  = AlumniProfile
        fields = [
            'department', 'graduation_year', 'company', 'current_position',
            'location', 'linkedin_url', 'skills', 'bio', 'is_mentor_available',
            'email_visible',
        ]
        widgets = {
            'bio':    forms.Textarea(attrs={'rows': 4}),
            'skills': forms.TextInput(attrs={'placeholder': 'Python, Leadership, System Design…'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial  = self.user.last_name
            self.fields['email'].initial      = self.user.email

    def save(self, user=None, commit=True):
        profile = super().save(commit=False)
        u = user or self.user
        if u:
            u.first_name = self.cleaned_data['first_name']
            u.last_name  = self.cleaned_data['last_name']
            u.email      = self.cleaned_data['email']
            u.save()
            profile.user = u
        if commit:
            profile.save()
        return profile


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model  = WorkExperience
        fields = ['title', 'company', 'location', 'start_year', 'end_year',
                  'is_current', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
