# events/serializers.py
from rest_framework import serializers
from .models import Event, EventRegistration, AgendaItem


class AgendaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AgendaItem
        fields = ['id', 'time', 'title', 'description', 'order']


class EventSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    spots_left       = serializers.IntegerField(read_only=True)
    agenda_items     = AgendaItemSerializer(many=True, read_only=True)
    is_full          = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'location',
            'event_date', 'end_date', 'capacity', 'banner',
            'is_published', 'registered_count', 'spots_left',
            'is_full', 'agenda_items', 'created_at',
        ]


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EventRegistration
        fields = ['id', 'event', 'user', 'dietary', 'special_needs',
                  'attended', 'registered_at']
        read_only_fields = ['user', 'attended', 'registered_at']
