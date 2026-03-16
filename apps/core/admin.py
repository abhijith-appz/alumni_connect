from django.contrib import admin
from .models import Announcement, ActivityLog


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display    = ('title', 'type', 'audience', 'views', 'created_at')
    list_filter     = ('type', 'audience')
    search_fields   = ('title', 'message')
    ordering        = ('-created_at',)
    readonly_fields = ('views', 'created_at')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display    = ('user', 'action', 'ip_address', 'created_at')
    list_filter     = ('created_at',)
    search_fields   = ('user__username', 'action')
    ordering        = ('-created_at',)
    readonly_fields = ('created_at',)
