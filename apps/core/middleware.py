class ActivityTrackingMiddleware:
    """Log page visits for admin users only."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if (
                request.user.is_authenticated
                and hasattr(request.user, 'is_staff_member')
                and request.user.is_staff_member
                and request.method == 'GET'
                and not request.path.startswith(('/static/', '/media/', '/api/', '/admin/'))
            ):
                from apps.core.models import ActivityLog
                ActivityLog.objects.create(
                    user=request.user,
                    action=f'Visited {request.path}',
                    ip_address=_get_ip(request),
                )
        except Exception:
            pass
        return response


def _get_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
