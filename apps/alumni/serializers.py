"""
alumni/serializers.py  —  DRF serializers for Alumni REST API.
"""
from rest_framework import serializers
from apps.accounts.models import User
from .models import AlumniProfile, WorkExperience, Education


class UserLiteSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'first_name', 'last_name', 'email', 'photo_url']

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WorkExperience
        fields = ['id', 'title', 'company', 'location',
                  'start_year', 'end_year', 'is_current', 'description']


class AlumniProfileSerializer(serializers.ModelSerializer):
    user            = UserLiteSerializer(read_only=True)
    experience      = WorkExperienceSerializer(many=True, read_only=True)
    skills_list     = serializers.SerializerMethodField()
    full_name       = serializers.SerializerMethodField()

    class Meta:
        model  = AlumniProfile
        fields = [
            'id', 'user', 'full_name', 'department', 'graduation_year',
            'company', 'current_position', 'location', 'linkedin_url',
            'skills', 'skills_list', 'bio', 'is_mentor_available',
            'status', 'profile_views', 'experience', 'created_at',
        ]

    def get_skills_list(self, obj):
        return obj.get_skills_list()

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class AlumniProfileListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""
    full_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = AlumniProfile
        fields = ['id', 'full_name', 'photo_url', 'department',
                  'graduation_year', 'company', 'current_position',
                  'is_mentor_available', 'status']

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_photo_url(self, obj):
        if obj.user.photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.user.photo.url) if request else obj.user.photo.url
        return None
