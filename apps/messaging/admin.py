from django.contrib import admin
from .models import Conversation, Message, ContactMessage

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display  = ('pk', 'created_at', 'updated_at')
    ordering      = ('-updated_at',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter   = ('is_read',)
    search_fields = ('name', 'email', 'subject')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)
