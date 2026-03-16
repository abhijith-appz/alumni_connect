"""
messaging/views.py
Direct messaging between students and alumni, plus contact form.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone

from .models import Conversation, Message, ContactMessage
from .forms import MessageForm, ContactForm
from apps.accounts.models import User, Notification


@login_required
def conversation_list(request):
    """Show all conversations for the logged-in user."""
    convs = request.user.conversations.prefetch_related('participants').order_by('-updated_at')

    # Determine active conversation
    conv_pk = request.GET.get('user')
    active_conv = None

    if conv_pk:
        try:
            other = User.objects.get(pk=conv_pk)
            active_conv, _ = Conversation.get_or_create_between(request.user, other)
        except User.DoesNotExist:
            pass
    elif convs.exists():
        active_conv = convs.first()

    # Fetch messages for active conversation
    chat_messages = []
    if active_conv:
        chat_messages = active_conv.messages.select_related('sender').order_by('created_at')
        # Mark as read
        active_conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Annotate unread counts
    conversations_annotated = []
    for conv in convs:
        conv.unread = conv.unread_count(request.user)
        conv.other  = conv.other_participant(request.user)
        conv.last   = conv.last_message()
        conversations_annotated.append(conv)

    template = 'student/messages.html' if request.user.is_student else 'alumni/alumni_messages.html'
    return render(request, template, {
        'conversations': conversations_annotated,
        'active_conv':   active_conv,
        'messages_list': chat_messages,
    })


@login_required
@require_POST
def send_message(request, conv_pk=None):
    content = request.POST.get('content', '').strip()
    if not content:
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if conv_pk:
        conv = get_object_or_404(Conversation, pk=conv_pk)
        if request.user not in conv.participants.all():
            return redirect('student_messages')
    else:
        other_pk = request.POST.get('recipient')
        try:
            other = User.objects.get(pk=other_pk)
        except User.DoesNotExist:
            return redirect('student_messages')
        conv, _ = Conversation.get_or_create_between(request.user, other)

    Message.objects.create(
        conversation=conv,
        sender=request.user,
        content=content,
    )
    conv.save()  # update updated_at

    # Notify recipient
    other_user = conv.other_participant(request.user)
    if other_user:
        Notification.create(
            user    = other_user,
            type    = Notification.Type.MESSAGE,
            title   = 'New Message',
            message = f'{request.user.get_full_name()} sent you a message.',
            link    = f'/messages/?user={request.user.pk}',
        )

    return redirect(f'/messages/?chat={conv.pk}')


# ── Contact Page ──────────────────────────────────────────────────────────────

def contact_view(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        msg = form.save()
        # Notify admin
        for admin_user in User.objects.filter(role__in=[User.Role.ADMIN, User.Role.STAFF]):
            Notification.create(
                user    = admin_user,
                type    = Notification.Type.MESSAGE,
                title   = 'New Contact Message',
                message = f'{msg.name} sent: "{msg.subject}"',
                link    = '/staff/messages/',
            )
        django_messages.success(request, "Thank you! We'll get back to you within 24 hours.")
        return redirect('contact')

    return render(request, 'public/contact.html', {'form': form})


# ── Admin: Message Centre ─────────────────────────────────────────────────────

@login_required
def admin_messages(request):
    if not request.user.is_staff_member:
        return redirect('home')

    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    active_msg = None

    msg_pk = request.GET.get('msg')
    if not msg_pk and contact_messages.exists():
        msg_pk = str(contact_messages.first().pk)

    if msg_pk:
        active_msg = get_object_or_404(ContactMessage, pk=msg_pk)
        ContactMessage.objects.filter(pk=msg_pk).update(is_read=True)
        active_msg.refresh_from_db()

        if request.method == 'POST':
            action = request.POST.get('action', '')
            if action == 'resolve':
                active_msg.is_read = True
                active_msg.save()
                django_messages.success(request, 'Marked as resolved.')
                return redirect(f'/staff/messages/?msg={msg_pk}')
            reply = request.POST.get('reply', '').strip()
            if reply:
                active_msg.reply = reply
                active_msg.replied_at = timezone.now()
                active_msg.is_read = True
                active_msg.save()
                django_messages.success(request, 'Reply sent.')
                return redirect(f'/staff/messages/?msg={msg_pk}')

    return render(request, 'admin/admin_messages.html', {
        'contact_messages': contact_messages,
        'active_msg': active_msg,
        'active_msg_pk': msg_pk,
    })

# ── AJAX: Unread count ────────────────────────────────────────────────────────

@login_required
def unread_count(request):
    count = sum(
        conv.unread_count(request.user)
        for conv in request.user.conversations.all()
    )
    return JsonResponse({'count': count})
