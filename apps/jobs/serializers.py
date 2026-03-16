# ── jobs/serializers.py ───────────────────────────────────────────────────────
from rest_framework import serializers
from .models import Job, JobApplication


class JobSerializer(serializers.ModelSerializer):
    posted_by_name   = serializers.SerializerMethodField()
    skills_list      = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    is_active        = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Job
        fields = [
            'id', 'title', 'company', 'location', 'job_type', 'domain',
            'salary', 'experience', 'description', 'requirements',
            'skills', 'skills_list', 'apply_link', 'deadline',
            'status', 'is_active', 'views', 'applications_count',
            'posted_by_name', 'created_at',
        ]

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name()

    def get_skills_list(self, obj):
        return obj.get_skills_list()

    def get_applications_count(self, obj):
        return obj.applications_count


class JobListSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()
    is_active      = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Job
        fields = ['id', 'title', 'company', 'location', 'job_type',
                  'salary', 'status', 'is_active', 'posted_by_name', 'created_at']

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name()


class JobApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    job_title      = serializers.SerializerMethodField()

    class Meta:
        model  = JobApplication
        fields = ['id', 'job', 'job_title', 'applicant', 'applicant_name',
                  'cover_letter', 'status', 'applied_at']
        read_only_fields = ['applicant', 'applied_at']

    def get_applicant_name(self, obj):
        return obj.applicant.get_full_name()

    def get_job_title(self, obj):
        return obj.job.title


# ── events/serializers.py ─────────────────────────────────────────────────────
from rest_framework import serializers as s
from apps.events.models import Event, EventRegistration, AgendaItem


class AgendaItemSerializer(s.ModelSerializer):
    class Meta:
        model  = AgendaItem
        fields = ['id', 'time', 'title', 'description', 'order']


class EventSerializer(s.ModelSerializer):
    registered_count = s.IntegerField(read_only=True)
    spots_left       = s.IntegerField(read_only=True)
    agenda_items     = AgendaItemSerializer(many=True, read_only=True)
    is_full          = s.BooleanField(read_only=True)

    class Meta:
        model  = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'location',
            'event_date', 'end_date', 'capacity', 'banner',
            'is_published', 'registered_count', 'spots_left',
            'is_full', 'agenda_items', 'created_at',
        ]


class EventRegistrationSerializer(s.ModelSerializer):
    class Meta:
        model  = EventRegistration
        fields = ['id', 'event', 'user', 'dietary', 'special_needs',
                  'attended', 'registered_at']
        read_only_fields = ['user', 'attended', 'registered_at']
