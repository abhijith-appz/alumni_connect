# accounts/api_urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    u = request.user
    return Response({
        'id':         u.pk,
        'username':   u.username,
        'email':      u.email,
        'full_name':  u.get_full_name(),
        'role':       u.role,
        'photo_url':  u.get_photo_url(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_notification_prefs(request):
    u = request.user
    u.notif_new_jobs    = request.data.get('new_jobs', u.notif_new_jobs)
    u.notif_messages    = request.data.get('messages', u.notif_messages)
    u.notif_events      = request.data.get('events', u.notif_events)
    u.notif_connections = request.data.get('connections', u.notif_connections)
    u.notif_ai          = request.data.get('ai', u.notif_ai)
    u.notif_system      = request.data.get('system', u.notif_system)
    u.save()
    return Response({'status': 'updated'})


urlpatterns = [
    path('token/',    obtain_auth_token,         name='api_token'),
    path('me/',       me,                         name='api_me'),
    path('notif-prefs/', update_notification_prefs, name='api_notif_prefs'),
]
