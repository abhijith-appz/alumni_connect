"""
jobs/views.py
Job board, job detail, apply, post job, manage jobs, internships.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import Job, JobApplication, SavedJob
from .forms import JobForm, JobApplicationForm
from apps.accounts.models import Notification


# ── Public / Student: Browse Jobs ─────────────────────────────────────────────

@login_required
def job_list(request):
    qs = Job.objects.filter(status=Job.Status.ACTIVE).select_related('posted_by')

    # Filtering
    q      = request.GET.get('q', '').strip()
    jtype  = request.GET.get('type', '')
    dept   = request.GET.get('dept', '')
    loc    = request.GET.get('location', '')
    sort   = request.GET.get('sort', '-created_at')

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(skills__icontains=q))
    if jtype:
        qs = qs.filter(job_type=jtype)
    if dept:
        qs = qs.filter(domain__icontains=dept)
    if loc:
        qs = qs.filter(location__icontains=loc)

    valid_sorts = ['-created_at', 'created_at', 'title', '-title']
    if sort in valid_sorts:
        qs = qs.order_by(sort)

    paginator = Paginator(qs, settings.JOBS_PER_PAGE)
    page      = paginator.get_page(request.GET.get('page'))

    return render(request, 'student/jobs.html', {
        'jobs': page,
        'total_jobs': qs.count(),
        'new_jobs_count': Job.objects.filter(status=Job.Status.ACTIVE).count(),
    })


# ── Job Detail ────────────────────────────────────────────────────────────────

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, status=Job.Status.ACTIVE)

    # Track view
    Job.objects.filter(pk=pk).update(views=job.views + 1)

    # Check if already applied
    already_applied = False
    if request.user.is_authenticated:
        already_applied = JobApplication.objects.filter(
            job=job, applicant=request.user
        ).exists()

    # Similar jobs
    similar = Job.objects.filter(
        status=Job.Status.ACTIVE,
        domain=job.domain,
    ).exclude(pk=pk)[:4]

    form = JobApplicationForm()

    return render(request, 'student/job_detail.html', {
        'job': job,
        'already_applied': already_applied,
        'similar_jobs': similar,
        'form': form,
    })


# ── Apply for Job ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk, status=Job.Status.ACTIVE)

    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)

    form = JobApplicationForm(request.POST, request.FILES)
    if form.is_valid():
        application = form.save(commit=False)
        application.job       = job
        application.applicant = request.user
        application.save()

        # Notify the job poster
        Notification.create(
            user    = job.posted_by,
            type    = Notification.Type.JOB,
            title   = 'New Job Application',
            message = f'{request.user.get_full_name()} applied for "{job.title}"',
            link    = f'/alumni/jobs/manage/',
        )

        messages.success(request, f'Application submitted for "{job.title}"!')
    else:
        messages.error(request, 'Please correct the errors in the form.')

    return redirect('job_detail', pk=pk)


# ── Save / Unsave Job ─────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_save_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})


# ── Alumni: Post Job ──────────────────────────────────────────────────────────

@login_required
def post_job(request):
    if not request.user.is_alumni:
        messages.error(request, 'Only alumni can post jobs.')
        return redirect('student_jobs')

    form = JobForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        job.posted_by = request.user
        if 'save_draft' in request.POST:
            job.status = Job.Status.DRAFT
        else:
            job.status = Job.Status.ACTIVE
        job.save()
        messages.success(request, f'"{job.title}" has been posted successfully.')
        return redirect('manage_jobs')

    return render(request, 'alumni/post_job.html', {'form': form})


# ── Alumni: Manage Jobs ───────────────────────────────────────────────────────

@login_required
def manage_jobs(request):
    if not (request.user.is_alumni or request.user.is_staff_member):
        return redirect('student_jobs')

    if request.user.is_staff_member:
        my_jobs = Job.objects.all().select_related('posted_by').order_by('-created_at')
    else:
        my_jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')

    return render(request, 'alumni/manage_jobs.html', {'my_jobs': my_jobs})


# ── Alumni: Edit Job ──────────────────────────────────────────────────────────

@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    form = JobForm(request.POST or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Job updated.')
        return redirect('manage_jobs')
    return render(request, 'alumni/post_job.html', {'form': form, 'job': job, 'editing': True})


# ── Alumni: Close / Activate / Delete Job ────────────────────────────────────

@login_required
@require_POST
def close_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    job.status = Job.Status.CLOSED
    job.save()
    messages.success(request, f'"{job.title}" has been closed.')
    return redirect('manage_jobs')


@login_required
@require_POST
def activate_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    job.status = Job.Status.ACTIVE
    job.save()
    messages.success(request, f'"{job.title}" is now active.')
    return redirect('manage_jobs')


@login_required
@require_POST
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    title = job.title
    job.delete()
    messages.success(request, f'"{title}" has been deleted.')
    return redirect('manage_jobs')


# ── Internships ───────────────────────────────────────────────────────────────

@login_required
def internship_list(request):
    qs = Job.objects.filter(
        status=Job.Status.ACTIVE,
        job_type=Job.Type.INTERNSHIP
    ).select_related('posted_by')

    domain = request.GET.get('domain', '')
    if domain:
        qs = qs.filter(domain__icontains=domain)

    paginator = Paginator(qs, settings.JOBS_PER_PAGE)
    page      = paginator.get_page(request.GET.get('page'))

    return render(request, 'student/internships.html', {'internships': page})
