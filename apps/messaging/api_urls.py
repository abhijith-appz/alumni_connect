# messaging/api_urls.py
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_api(request):
    count = sum(
        c.messages.filter(is_read=False).exclude(sender=request.user).count()
        for c in request.user.conversations.all()
    )
    return Response({'unread': count})


urlpatterns = [
    path('unread/', unread_api, name='api_unread'),
]
