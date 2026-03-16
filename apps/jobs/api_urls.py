# ── jobs/api_urls.py ──────────────────────────────────────────────────────────
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Job, JobApplication
from .serializers import JobSerializer, JobListSerializer, JobApplicationSerializer


class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'company', 'location', 'skills']
    ordering_fields    = ['created_at', 'title', 'company']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Job.objects.filter(status=Job.Status.ACTIVE).select_related('posted_by')
        jtype = self.request.query_params.get('type')
        loc   = self.request.query_params.get('location')
        if jtype: qs = qs.filter(job_type=jtype)
        if loc:   qs = qs.filter(location__icontains=loc)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job = self.get_object()
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response({'error': 'Already applied'}, status=400)
        app = JobApplication.objects.create(
            job=job, applicant=request.user,
            cover_letter=request.data.get('cover_letter', ''),
        )
        return Response(JobApplicationSerializer(app).data, status=201)


router = DefaultRouter()
router.register(r'', JobViewSet, basename='job')
urlpatterns = [path('', include(router.urls))]


# ── events/api_urls.py ────────────────────────────────────────────────────────
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.events.models import Event, EventRegistration
from apps.events.serializers import EventSerializer, EventRegistrationSerializer


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
            defaults={
                'dietary': request.data.get('dietary', ''),
                'special_needs': request.data.get('special_needs', ''),
            }
        )
        if not created:
            return Response({'error': 'Already registered'}, status=400)
        return Response({'status': 'registered'}, status=201)


router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')

# Store events api_urls as separate file
events_api_urlpatterns = [path('', include(router.urls))]
