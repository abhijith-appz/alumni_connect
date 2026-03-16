# ── accounts/admin.py ─────────────────────────────────────────────────────────
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'phone', 'photo', 'bio')}),
        ('Notifications',  {'fields': (
            'notif_new_jobs', 'notif_messages', 'notif_events',
            'notif_connections', 'notif_ai', 'notif_system',
        )}),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter   = ('type', 'is_read')
    search_fields = ('user__username', 'title', 'message')
    ordering      = ('-created_at',)
