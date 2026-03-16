from django.contrib import admin
from .models import AIConversation, AIMessage

class AIMessageInline(admin.TabularInline):
    model           = AIMessage
    extra           = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete      = False

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display    = ('user', 'title', 'created_at', 'updated_at')
    search_fields   = ('user__username', 'title')
    ordering        = ('-updated_at',)
    inlines         = [AIMessageInline]
    readonly_fields = ('created_at', 'updated_at')
