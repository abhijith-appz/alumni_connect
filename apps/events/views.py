"""
events/views.py
Event listing, detail, registration, and admin management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import Event, EventRegistration
from .forms import EventForm, EventRegistrationForm
from apps.accounts.models import Notification


@login_required
def event_list(request):
    qs = Event.objects.filter(is_published=True).order_by('event_date')

    event_type = request.GET.get('type', '')
    if event_type:
        qs = qs.filter(event_type=event_type)

    paginator = Paginator(qs, settings.EVENTS_PER_PAGE)
    page      = paginator.get_page(request.GET.get('page'))

    return render(request, 'student/events.html', {'events': page})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    user_registered = EventRegistration.objects.filter(
        event=event, user=request.user
    ).exists()

    return render(request, 'student/event_detail.html', {
        'event': event,
        'user_registered': user_registered,
        'form': EventRegistrationForm(),
    })


@login_required
@require_POST
def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)

    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('event_detail', pk=pk)

    if event.is_full:
        messages.error(request, 'This event is at full capacity.')
        return redirect('event_detail', pk=pk)

    form = EventRegistrationForm(request.POST)
    if form.is_valid():
        reg = form.save(commit=False)
        reg.event = event
        reg.user  = request.user
        reg.save()

        Notification.create(
            user    = request.user,
            type    = Notification.Type.EVENT,
            title   = 'Event Registration Confirmed',
            message = f'You are registered for "{event.title}" on {event.event_date.strftime("%b %d, %Y")}.',
            link    = f'/events/{event.pk}/',
        )
        messages.success(request, f'Registered for "{event.title}"!')
    else:
        messages.error(request, 'Registration failed. Please try again.')

    return redirect('event_detail', pk=pk)


# ── Admin: Manage Events ──────────────────────────────────────────────────────

@login_required
def admin_manage_events(request):
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created.')
            return redirect('manage_events')
        messages.error(request, 'Please fix the form errors.')
    else:
        form = EventForm()

    events = Event.objects.all().order_by('event_date')
    return render(request, 'admin/manage_events.html', {'events': events, 'form': form})


@login_required
def edit_event(request, pk):
    if not request.user.is_staff_member:
        return redirect('home')
    event = get_object_or_404(Event, pk=pk)
    form  = EventForm(request.POST or None, request.FILES or None, instance=event)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Event updated.')
        return redirect('manage_events')
    return render(request, 'admin/manage_events.html', {'form': form, 'editing': True, 'event': event})


@login_required
@require_POST
def delete_event(request, pk):
    if not request.user.is_staff_member:
        return redirect('home')
    event = get_object_or_404(Event, pk=pk)
    title = event.title
    event.delete()
    messages.success(request, f'"{title}" deleted.')
    return redirect('manage_events')
