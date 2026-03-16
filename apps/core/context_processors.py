from django.conf import settings


def global_context(request):
    ctx = {
        'PLATFORM_NAME':              getattr(settings, 'PLATFORM_NAME',   'AlumniConnect'),
        'UNIVERSITY_NAME':            getattr(settings, 'UNIVERSITY_NAME', "St. Xavier's University"),
        'unread_notifications_count': 0,
        'unread_messages':            0,
        'pending_alumni_count':       0,
        'recent_notifications':       [],
    }

    if not request.user.is_authenticated:
        return ctx

    try:
        from apps.accounts.models import Notification
        ctx['unread_notifications_count'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        ctx['recent_notifications'] = list(
            Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        )
    except Exception:
        pass

    try:
        unread = 0
        for conv in request.user.conversations.all():
            unread += conv.messages.filter(
                is_read=False
            ).exclude(sender=request.user).count()
        ctx['unread_messages'] = unread
    except Exception:
        pass

    try:
        if hasattr(request.user, 'is_staff_member') and request.user.is_staff_member:
            from apps.alumni.models import AlumniProfile
            ctx['pending_alumni_count'] = AlumniProfile.objects.filter(
                status=AlumniProfile.Status.PENDING
            ).count()
    except Exception:
        pass

    return ctx
