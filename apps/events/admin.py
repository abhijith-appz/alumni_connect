from django.contrib import admin
from .models import Event, AgendaItem, EventRegistration


class AgendaInline(admin.TabularInline):
    model = AgendaItem
    extra = 1


class RegistrationInline(admin.TabularInline):
    model           = EventRegistration
    extra           = 0
    readonly_fields = ('user', 'registered_at')
    can_delete      = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display    = ('title', 'event_type', 'event_date', 'capacity', 'is_published')
    list_filter     = ('event_type', 'is_published')
    search_fields   = ('title', 'location')
    ordering        = ('event_date',)
    inlines         = [AgendaInline, RegistrationInline]
    readonly_fields = ('created_at',)

    def registered_count(self, obj):
        return obj.registered_count
    registered_count.short_description = 'Registered'
