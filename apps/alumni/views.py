"""
alumni/views.py
Alumni dashboard, profile, edit profile, alumni network, view students.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings

from .models import AlumniProfile, WorkExperience, Education
from .forms import AlumniProfileForm, WorkExperienceForm
from apps.students.models import StudentProfile
from apps.jobs.models import Job
from apps.events.models import Event, EventRegistration
from apps.accounts.models import Notification


def alumni_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_alumni:
            messages.error(request, 'This section is for alumni only.')
            return redirect(request.user.get_dashboard_url())
        return view_func(request, *args, **kwargs)
    return wrapper


@alumni_required
def dashboard(request):
    user = request.user
    now  = timezone.now()

    try:
        profile = user.alumni_profile
    except AlumniProfile.DoesNotExist:
        profile = None

    my_jobs = Job.objects.filter(
        posted_by=user,
        status=Job.Status.ACTIVE,
    ).order_by('-created_at')[:5]

    upcoming_events = Event.objects.filter(
        is_published=True,
        event_date__gte=now,
    ).order_by('event_date')[:3]

    recent_notifications = Notification.objects.filter(
        user=user
    ).order_by('-created_at')[:5]

    return render(request, 'alumni/alumni_dashboard.html', {
        'profile':              profile,
        'my_jobs':              my_jobs,
        'upcoming_events':      upcoming_events,
        'recent_notifications': recent_notifications,
        'active_jobs':          my_jobs.count(),
        'profile_views':        profile.profile_views if profile else 0,
        'unread_messages':      sum(
            c.unread_count(user) for c in user.conversations.all()
        ),
    })


@alumni_required
def alumni_profile(request):
    profile = get_object_or_404(AlumniProfile, user=request.user)
    return render(request, 'alumni/alumni_profile_public.html', {
        'alumni':      profile,
        'is_own':      True,
        'alumni_jobs': Job.objects.filter(posted_by=request.user, status=Job.Status.ACTIVE),
    })


@alumni_required
def edit_profile(request):
    try:
        profile = request.user.alumni_profile
    except AlumniProfile.DoesNotExist:
        profile = AlumniProfile(user=request.user)

    form = AlumniProfileForm(
        request.POST  or None,
        request.FILES or None,
        instance=profile,
        user=request.user,
    )

    if request.method == 'POST' and form.is_valid():
        form.save(user=request.user)
        messages.success(request, 'Profile updated.')
        return redirect('alumni_profile')

    return render(request, 'alumni/edit_profile.html', {'form': form})


@alumni_required
def alumni_network(request):
    qs = AlumniProfile.objects.filter(
        status=AlumniProfile.Status.APPROVED
    ).exclude(
        user=request.user
    ).select_related('user').order_by('-graduation_year')

    q    = request.GET.get('q', '').strip()
    year = request.GET.get('year', '')
    ind  = request.GET.get('industry', '')

    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) |
            Q(company__icontains=q)
        )
    if year:
        qs = qs.filter(graduation_year=year)
    if ind:
        qs = qs.filter(current_position__icontains=ind)

    paginator   = Paginator(qs, settings.ALUMNI_PER_PAGE)
    page        = paginator.get_page(request.GET.get('page'))
    my_connections = request.user.conversations.count()

    return render(request, 'alumni/alumni_network.html', {
        'alumni_list':    page,
        'my_connections': my_connections,
    })


@alumni_required
def view_students(request):
    qs = StudentProfile.objects.filter(
        user__is_active=True
    ).select_related('user').order_by('-created_at')

    q    = request.GET.get('q', '')
    dept = request.GET.get('dept', '')
    year = request.GET.get('year', '')

    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
        )
    if dept:
        qs = qs.filter(department__icontains=dept)
    if year:
        qs = qs.filter(current_year=year)

    paginator = Paginator(qs, 20)
    page      = paginator.get_page(request.GET.get('page'))

    return render(request, 'alumni/view_students.html', {'students': page})


@alumni_required
def alumni_events(request):
    now    = timezone.now()
    events = Event.objects.filter(is_published=True, event_date__gte=now).order_by('event_date')
    my_registrations = EventRegistration.objects.filter(
        user=request.user
    ).values_list('event_id', flat=True)

    return render(request, 'alumni/alumni_events.html', {
        'events':           events,
        'my_registrations': set(my_registrations),
    })
