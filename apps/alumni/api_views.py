"""
alumni/api_views.py  —  DRF ViewSets for Alumni REST API.
"""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import AlumniProfile
from .serializers import AlumniProfileSerializer, AlumniProfileListSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff_member


class AlumniProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['user__first_name', 'user__last_name', 'company',
                          'current_position', 'department', 'skills']
    ordering_fields    = ['graduation_year', 'company', 'created_at']
    ordering           = ['-graduation_year']

    def get_queryset(self):
        qs = AlumniProfile.objects.filter(
            status=AlumniProfile.Status.APPROVED
        ).select_related('user').prefetch_related('experience')

        dept    = self.request.query_params.get('department')
        year    = self.request.query_params.get('year')
        company = self.request.query_params.get('company')
        mentor  = self.request.query_params.get('mentor')

        if dept:    qs = qs.filter(department__icontains=dept)
        if year:    qs = qs.filter(graduation_year=year)
        if company: qs = qs.filter(company__icontains=company)
        if mentor:  qs = qs.filter(is_mentor_available=True)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return AlumniProfileListSerializer
        return AlumniProfileSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.is_staff_member:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object()
        from django.utils import timezone
        profile.status      = AlumniProfile.Status.APPROVED
        profile.approved_at = timezone.now()
        profile.approved_by = request.user
        profile.save()
        profile.user.is_active = True
        profile.user.save()
        return Response({'status': 'approved'})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        if not request.user.is_staff_member:
            return Response(status=status.HTTP_403_FORBIDDEN)
        qs = AlumniProfile.objects.filter(status=AlumniProfile.Status.PENDING).select_related('user')
        serializer = AlumniProfileListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)
