# events/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Event, EventRegistration
from .serializers import EventSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Event.objects.filter(is_published=True).order_by('event_date')
    serializer_class   = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        if event.is_full:
            return Response({'error': 'Event is full'}, status=400)
        reg, created = EventRegistration.objects.get_or_create(
            event=event, user=request.user,
        )
        if not created:
            return Response({'error': 'Already registered'}, status=400)
        return Response({'status': 'registered'}, status=201)


router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')
urlpatterns = [path('', include(router.urls))]
