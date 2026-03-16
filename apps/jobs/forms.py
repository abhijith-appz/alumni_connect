# ── jobs/forms.py ─────────────────────────────────────────────────────────────
from django import forms
from .models import Job, JobApplication


class JobForm(forms.ModelForm):
    class Meta:
        model  = Job
        fields = [
            'title', 'company', 'location', 'job_type', 'domain',
            'salary', 'experience', 'description', 'requirements',
            'skills', 'apply_link', 'deadline',
        ]
        widgets = {
            'description':  forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'deadline':     forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_skills(self):
        raw = self.cleaned_data.get('skills', '')
        # Normalise: strip extra spaces around commas
        return ', '.join(s.strip() for s in raw.split(',') if s.strip())


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model  = JobApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell the alumni why you are a great fit…',
            }),
        }
