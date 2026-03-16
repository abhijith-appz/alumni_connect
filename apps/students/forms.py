from django import forms
from .models import StudentProfile

DEPARTMENTS = [
    ('', 'Select Department'),
    ('Computer Science', 'Computer Science'),
    ('Management / MBA', 'Management / MBA'),
    ('Electronics & Communication', 'Electronics & Communication'),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Civil Engineering', 'Civil Engineering'),
    ('Commerce & Finance', 'Commerce & Finance'),
    ('Law', 'Law'),
    ('Arts & Humanities', 'Arts & Humanities'),
    ('Science', 'Science'),
    ('Architecture', 'Architecture'),
]


class StudentProfileForm(forms.ModelForm):
    first_name  = forms.CharField(max_length=50)
    last_name   = forms.CharField(max_length=50)
    email       = forms.EmailField()
    department  = forms.ChoiceField(choices=DEPARTMENTS)

    class Meta:
        model  = StudentProfile
        fields = [
            'department', 'current_year', 'expected_graduation',
            'skills', 'interests', 'linkedin_url', 'github_url', 'resume',
        ]

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
