"""
students/views.py
Student dashboard, profile, alumni search, career guidance.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings

from .models import StudentProfile
from .forms import StudentProfileForm
from apps.alumni.models import AlumniProfile
from apps.jobs.models import Job
from apps.events.models import Event
from apps.accounts.models import Notification


def student_required(view_func):
    """Decorator: user must be authenticated and a student."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_student:
            messages.error(request, 'This section is for students only.')
            return redirect(request.user.get_dashboard_url())
        return view_func(request, *args, **kwargs)
    return wrapper


@student_required
def dashboard(request):
    user = request.user
    now  = timezone.now()

    latest_jobs   = Job.objects.filter(status=Job.Status.ACTIVE).order_by('-created_at')[:5]
    upcoming_events = Event.objects.filter(
        is_published=True, event_date__gte=now
    ).order_by('event_date')[:3]

    profile_completeness = 0
    try:
        profile_completeness = user.student_profile.profile_completeness
    except StudentProfile.DoesNotExist:
        pass

    unread_notifications = Notification.objects.filter(
        user=user, is_read=False
    ).count()

    return render(request, 'student/student_dashboard.html', {
        'latest_jobs':          latest_jobs,
        'upcoming_events_list': upcoming_events,
        'profile_completeness': profile_completeness,
        'unread_notifications': unread_notifications,
        'new_jobs_count':       Job.objects.filter(status=Job.Status.ACTIVE).count(),
        'total_messages':       user.conversations.count(),
        'greeting':             _greeting(),
    })


def _greeting():
    hour = timezone.now().hour
    if hour < 12:   return 'Good morning'
    if hour < 17:   return 'Good afternoon'
    return 'Good evening'


@student_required
def student_profile(request):
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = None

    form = StudentProfileForm(
        request.POST  or None,
        request.FILES or None,
        instance=profile,
        user=request.user,
    )

    if request.method == 'POST' and form.is_valid():
        form.save(user=request.user)
        messages.success(request, 'Profile updated.')
        return redirect('student_profile')

    return render(request, 'student/student_profile.html', {
        'form':    form,
        'profile': profile,
    })


@student_required
def alumni_search(request):
    qs = AlumniProfile.objects.filter(
        status=AlumniProfile.Status.APPROVED
    ).select_related('user').order_by('-graduation_year')

    q       = request.GET.get('q', '').strip()
    dept    = request.GET.get('dept', '')
    year    = request.GET.get('year', '')
    company = request.GET.get('company', '')

    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)  |
            Q(company__icontains=q)          |
            Q(current_position__icontains=q)
        )
    if dept:
        qs = qs.filter(department__icontains=dept)
    if year:
        qs = qs.filter(graduation_year=year)
    if company:
        qs = qs.filter(company__icontains=company)

    paginator   = Paginator(qs, settings.ALUMNI_PER_PAGE)
    page        = paginator.get_page(request.GET.get('page'))
    alumni_count = qs.count()

    return render(request, 'student/alumni_search.html', {
        'alumni_list':  page,
        'alumni_count': alumni_count,
    })


@student_required
def career_guidance(request):
    return render(request, 'student/career_guidance.html', {})


@login_required
def alumni_profile_public(request, pk):
    """Publicly-viewable alumni profile (accessible to logged-in students and alumni)."""
    profile = get_object_or_404(
        AlumniProfile,
        pk=pk,
        status=AlumniProfile.Status.APPROVED,
    )
    # Track view
    AlumniProfile.objects.filter(pk=pk).update(profile_views=profile.profile_views + 1)

    alumni_jobs = Job.objects.filter(
        posted_by=profile.user,
        status=Job.Status.ACTIVE,
    ).order_by('-created_at')[:4]

    return render(request, 'alumni/alumni_profile_public.html', {
        'alumni':     profile,
        'alumni_jobs': alumni_jobs,
    })
