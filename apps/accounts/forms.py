from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    SetPasswordForm as DjangoSetPasswordForm,
    PasswordChangeForm,
)
from django.core.exceptions import ValidationError
from .models import User

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

YEARS = [(str(i), f'Year {i}') for i in range(1, 6)]
GRADUATION_YEARS = [(str(y), str(y)) for y in range(2024, 1961, -1)]


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Email or Username',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'you@example.com'}),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))
    remember = forms.BooleanField(required=False)


class StudentRegistrationForm(UserCreationForm):
    first_name          = forms.CharField(max_length=50)
    last_name           = forms.CharField(max_length=50)
    email               = forms.EmailField()
    student_id          = forms.CharField(max_length=20)
    department          = forms.ChoiceField(choices=DEPARTMENTS)
    current_year        = forms.ChoiceField(choices=YEARS)
    expected_graduation = forms.IntegerField(required=False, min_value=2024, max_value=2035)
    interests           = forms.CharField(required=False, max_length=300)
    agree_terms         = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms.'}
    )

    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'student_id', 'department', 'current_year',
                  'expected_graduation', 'interests',
                  'password1', 'password2', 'agree_terms')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_student_id(self):
        sid = self.cleaned_data['student_id']
        from apps.students.models import StudentProfile
        if StudentProfile.objects.filter(student_id=sid).exists():
            raise ValidationError('This student ID is already registered.')
        return sid


class AlumniRegistrationForm(UserCreationForm):
    first_name       = forms.CharField(max_length=50)
    last_name        = forms.CharField(max_length=50)
    email            = forms.EmailField()
    department       = forms.ChoiceField(choices=DEPARTMENTS)
    graduation_year  = forms.ChoiceField(choices=GRADUATION_YEARS)
    company          = forms.CharField(max_length=100, required=False)
    current_position = forms.CharField(max_length=100, required=False)
    linkedin_url     = forms.URLField(required=False)
    bio              = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    agree_terms      = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms.'}
    )

    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'department', 'graduation_year', 'company',
                  'current_position', 'linkedin_url', 'bio',
                  'password1', 'password2', 'agree_terms')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )


class SetPasswordForm(DjangoSetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'Min. 8 characters'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Repeat password'})


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['placeholder']   = 'Current password'
        self.fields['new_password1'].widget.attrs['placeholder']  = 'New password'
        self.fields['new_password2'].widget.attrs['placeholder']  = 'Confirm new password'


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'photo',
                  'notif_new_jobs', 'notif_messages', 'notif_events',
                  'notif_connections', 'notif_ai', 'notif_system')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email is already in use.')
        return email
