"""
core/views.py
Public pages: home, about, FAQ, alumni directory.
Admin dashboard, manage students/alumni, reports, announcements.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from apps.accounts.models import User, Notification
from apps.alumni.models import AlumniProfile
from apps.students.models import StudentProfile
from apps.jobs.models import Job
from apps.events.models import Event
from apps.messaging.models import ContactMessage


# ── Public Pages ──────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    featured_alumni = AlumniProfile.objects.filter(
        status=AlumniProfile.Status.APPROVED
    ).select_related('user').order_by('?')[:6]

    recent_jobs = Job.objects.filter(
        status=Job.Status.ACTIVE
    ).select_related('posted_by').order_by('-created_at')[:5]

    return render(request, 'public/home.html', {
        'featured_alumni': featured_alumni,
        'recent_jobs':     recent_jobs,
        'total_alumni':    AlumniProfile.objects.filter(status=AlumniProfile.Status.APPROVED).count(),
    })


def about(request):
    return render(request, 'public/about.html', {
        'stats': {
            'alumni': AlumniProfile.objects.filter(status=AlumniProfile.Status.APPROVED).count(),
            'students': StudentProfile.objects.count(),
            'jobs': Job.objects.filter(status=Job.Status.ACTIVE).count(),
        }
    })


def faq(request):
    return render(request, 'public/faq.html', {})


def public_alumni_directory(request):
    qs = AlumniProfile.objects.filter(
        status=AlumniProfile.Status.APPROVED
    ).select_related('user').order_by('-graduation_year')

    q    = request.GET.get('q', '')
    dept = request.GET.get('dept', '')
    year = request.GET.get('year', '')

    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) |
            Q(company__icontains=q)
        )
    if dept:
        qs = qs.filter(department__icontains=dept)
    if year:
        qs = qs.filter(graduation_year=year)

    paginator    = Paginator(qs, settings.ALUMNI_PER_PAGE)
    page         = paginator.get_page(request.GET.get('page'))
    total_alumni = qs.count()

    return render(request, 'public/alumni_directory.html', {
        'alumni_list':  page,
        'total_alumni': total_alumni,
    })


# ── Dashboard Redirect ────────────────────────────────────────────────────────

@login_required
def dashboard_redirect(request):
    return redirect(request.user.get_dashboard_url())


# ── Admin Section ─────────────────────────────────────────────────────────────

def staff_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff_member:
            messages.error(request, 'Access denied.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def admin_dashboard(request):
    now = timezone.now()
    ctx = {
        'total_users':     User.objects.count(),
        'total_students':  StudentProfile.objects.count(),
        'total_alumni':    AlumniProfile.objects.filter(status=AlumniProfile.Status.APPROVED).count(),
        'pending_alumni':  AlumniProfile.objects.filter(status=AlumniProfile.Status.PENDING).select_related('user')[:5],
        'pending_alumni_count': AlumniProfile.objects.filter(status=AlumniProfile.Status.PENDING).count(),
        'active_jobs':     Job.objects.filter(status=Job.Status.ACTIVE).count(),
        'upcoming_events': Event.objects.filter(is_published=True, event_date__gte=now).count(),
        'new_users_this_month': User.objects.filter(date_joined__month=now.month).count(),
    }
    return render(request, 'admin/admin_dashboard.html', ctx)


@staff_required
def manage_students(request):
    qs = StudentProfile.objects.select_related('user').order_by('-created_at')
    q    = request.GET.get('q', '')
    dept = request.GET.get('dept', '')
    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) |
            Q(student_id__icontains=q)
        )
    if dept:
        qs = qs.filter(department__icontains=dept)

    paginator = Paginator(qs, 25)
    page      = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin/manage_students.html', {
        'students':       page,
        'total_students': qs.count(),
    })


@staff_required
def manage_alumni(request):
    qs = AlumniProfile.objects.select_related('user').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    paginator     = Paginator(qs, 25)
    page          = paginator.get_page(request.GET.get('page'))
    pending_count = AlumniProfile.objects.filter(status=AlumniProfile.Status.PENDING).count()

    return render(request, 'admin/manage_alumni.html', {
        'alumni_list':  page,
        'pending_count': pending_count,
    })


@staff_required
@require_POST
def approve_alumni(request, pk):
    profile = get_object_or_404(AlumniProfile, pk=pk)
    profile.status      = AlumniProfile.Status.APPROVED
    profile.approved_at = timezone.now()
    profile.approved_by = request.user
    profile.save()

    profile.user.is_active = True
    profile.user.save()

    Notification.create(
        user    = profile.user,
        type    = Notification.Type.SYSTEM,
        title   = 'Account Approved',
        message = 'Your alumni registration has been approved. Welcome to AlumniConnect!',
        link    = '/alumni/dashboard/',
    )
    messages.success(request, f'{profile.user.get_full_name()} approved.')
    return redirect('manage_alumni')


@staff_required
@require_POST
def reject_alumni(request, pk):
    profile = get_object_or_404(AlumniProfile, pk=pk)
    profile.status = AlumniProfile.Status.REJECTED
    profile.save()
    messages.warning(request, f'{profile.user.get_full_name()} rejected.')
    return redirect('manage_alumni')


@staff_required
def system_reports(request):
    now = timezone.now()
    ctx = {
        'new_registrations': User.objects.filter(date_joined__month=now.month).count(),
        'active_jobs':       Job.objects.filter(status=Job.Status.ACTIVE).count(),
        'total_messages':    0,  # from messaging
        'ai_chats':          0,  # from ai_assistant
        'top_companies':     AlumniProfile.objects.values('company').annotate(
                                 count=Count('id')
                             ).order_by('-count')[:8],
    }
    return render(request, 'admin/system_reports.html', ctx)


@staff_required
def manage_admin_jobs(request):
    jobs = Job.objects.all().select_related('posted_by').order_by('-created_at')
    paginator = Paginator(jobs, 25)
    page      = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin/manage_jobs.html', {
        'jobs':       page,
        'total_jobs': jobs.count(),
    })


@staff_required
@require_POST
def admin_delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.delete()
    messages.success(request, 'Job removed.')
    return redirect('admin_manage_jobs')


@staff_required
def manage_announcements(request):
    from apps.core.models import Announcement
    if request.method == 'POST':
        title    = request.POST.get('title', '')
        message  = request.POST.get('message', '')
        ann_type = request.POST.get('announcement_type', 'general')
        audience = request.POST.get('audience', 'all')
        if title and message:
            Announcement.objects.create(
                title=title, message=message,
                type=ann_type, audience=audience,
                created_by=request.user,
            )
            messages.success(request, 'Announcement published.')
            return redirect('manage_announcements')
        messages.error(request, 'Title and message are required.')

    from apps.core.models import Announcement
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'admin/manage_announcements.html', {
        'announcements': announcements,
    })


# ── Error Handlers ────────────────────────────────────────────────────────────

def error_404(request, exception=None):
    return render(request, 'shared/404.html', status=404)


def error_403(request, exception=None):
    return render(request, 'shared/403.html', status=403)


def error_500(request):
    return render(request, 'shared/404.html', status=500)


# ── Admin stub views (used in templates) ─────────────────────────────────────

@staff_required
def admin_student_detail(request, pk):
    from apps.students.models import StudentProfile
    student = get_object_or_404(StudentProfile, pk=pk)
    return render(request, 'admin/manage_students.html', {'student': student})


@staff_required
def admin_edit_student(request, pk):
    from apps.students.models import StudentProfile
    student = get_object_or_404(StudentProfile, pk=pk)
    return render(request, 'admin/manage_students.html', {'student': student})


@staff_required
def admin_alumni_detail(request, pk):
    from apps.alumni.models import AlumniProfile
    profile = get_object_or_404(AlumniProfile, pk=pk)
    return render(request, 'admin/manage_alumni.html', {'alumni_detail': profile})


@staff_required
@require_POST
def delete_announcement(request, pk):
    from apps.core.models import Announcement
    ann = get_object_or_404(Announcement, pk=pk)
    ann.delete()
    messages.success(request, 'Announcement deleted.')
    return redirect('manage_announcements')


@staff_required
def edit_announcement(request, pk):
    from apps.core.models import Announcement
    ann  = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.title   = request.POST.get('title', ann.title)
        ann.message = request.POST.get('message', ann.message)
        ann.save()
        messages.success(request, 'Announcement updated.')
        return redirect('manage_announcements')
    return render(request, 'admin/manage_announcements.html', {'edit_ann': ann})
