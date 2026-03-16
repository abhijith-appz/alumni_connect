"""
accounts/views.py
Login, logout, register (student & alumni), password reset, settings.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

from .models import User, Notification
from .forms import (
    StudentRegistrationForm, AlumniRegistrationForm,
    LoginForm, ForgotPasswordForm, SetPasswordForm, ChangePasswordForm,
    UserSettingsForm,
)
from apps.students.models import StudentProfile
from apps.alumni.models import AlumniProfile


# ── Login / Logout ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember  = form.cleaned_data.get('remember', False)
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', user.get_dashboard_url())
            return redirect(next_url)
        messages.error(request, 'Invalid email or password.')

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ── Student Registration ──────────────────────────────────────────────────────

@require_http_methods(['GET', 'POST'])
def register_student(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    form = StudentRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.email      = form.cleaned_data['email']
            user.save()

            StudentProfile.objects.create(
                user=user,
                student_id=form.cleaned_data['student_id'],
                department=form.cleaned_data['department'],
                current_year=form.cleaned_data['current_year'],
                expected_graduation=form.cleaned_data.get('expected_graduation'),
                interests=form.cleaned_data.get('interests', ''),
            )

            login(request, user)
            messages.success(request, 'Account created! Welcome to AlumniConnect.')
            return redirect('student_dashboard')

    return render(request, 'auth/register_student.html', {'form': form})


# ── Alumni Registration ───────────────────────────────────────────────────────

@require_http_methods(['GET', 'POST'])
def register_alumni(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    form = AlumniRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.role       = User.Role.ALUMNI
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.email      = form.cleaned_data['email']
            user.is_active  = False  # pending admin approval
            user.save()

            AlumniProfile.objects.create(
                user=user,
                department=form.cleaned_data['department'],
                graduation_year=form.cleaned_data['graduation_year'],
                company=form.cleaned_data.get('company', ''),
                current_position=form.cleaned_data.get('current_position', ''),
                linkedin_url=form.cleaned_data.get('linkedin_url', ''),
                bio=form.cleaned_data.get('bio', ''),
                status=AlumniProfile.Status.PENDING,
            )

        messages.success(
            request,
            'Registration submitted! Your account will be reviewed and activated within 1–2 business days.'
        )
        return redirect('login')

    return render(request, 'auth/register_alumni.html', {'form': form})


# ── Password Reset ────────────────────────────────────────────────────────────

def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/auth/reset/{uid}/{token}/"

            send_mail(
                subject='Password Reset — AlumniConnect',
                message=(
                    f"Hi {user.first_name},\n\n"
                    f"Click the link below to reset your password:\n{reset_url}\n\n"
                    "This link expires in 24 hours.\n\n"
                    "If you didn't request this, please ignore this email.\n\n"
                    "— AlumniConnect Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists

        messages.success(request, 'If that email is registered, a reset link has been sent.')
        return redirect('login')

    return render(request, 'auth/forgot_password.html', {'form': form})


def reset_password(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'The reset link is invalid or has expired.')
        return redirect('forgot_password')

    form = SetPasswordForm(user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Password reset successfully. Please log in.')
        return redirect('login')

    return render(request, 'auth/reset_password.html', {'form': form})


# ── Change Password (logged in) ───────────────────────────────────────────────

@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated successfully.')
        return redirect('user_settings')

    return render(request, 'auth/change_password.html', {'form': form})


# ── User Settings ─────────────────────────────────────────────────────────────

@login_required
def user_settings(request):
    form = UserSettingsForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Settings saved.')
        return redirect('user_settings')

    return render(request, 'shared/user_settings.html', {
        'form': form,
        'section': request.POST.get('section', 'profile'),
    })


# ── Notifications ─────────────────────────────────────────────────────────────

@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shared/notifications.html', {
        'notifications': notifs,
        'unread_count': notifs.filter(is_read=False).count(),
    })


@login_required
def mark_notification_read(request, pk):
    Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')


# ── AJAX: Quick Search ────────────────────────────────────────────────────────

@login_required
def quick_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        from apps.alumni.models import AlumniProfile
        from apps.jobs.models import Job

        alumni = AlumniProfile.objects.filter(
            user__first_name__icontains=q,
            status=AlumniProfile.Status.APPROVED
        ).select_related('user')[:4]

        jobs = Job.objects.filter(title__icontains=q, is_active=True)[:3]

        for a in alumni:
            results.append({
                'label': a.user.get_full_name(),
                'url': f'/alumni/profile/{a.pk}/',
                'icon': '👤',
            })
        for j in jobs:
            results.append({
                'label': j.title,
                'url': f'/jobs/{j.pk}/',
                'icon': '💼',
            })

    return JsonResponse({'results': results})
