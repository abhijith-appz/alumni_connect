# ── alumni/admin.py ───────────────────────────────────────────────────────────
from django.contrib import admin
from .models import AlumniProfile, WorkExperience, Education


class WorkExperienceInline(admin.TabularInline):
    model  = WorkExperience
    extra  = 0


class EducationInline(admin.TabularInline):
    model  = Education
    extra  = 0


@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display   = ('user', 'department', 'graduation_year', 'company',
                      'current_position', 'status', 'is_mentor_available')
    list_filter    = ('status', 'department', 'graduation_year', 'is_mentor_available')
    search_fields  = ('user__first_name', 'user__last_name', 'company',
                      'current_position', 'department')
    ordering       = ('-graduation_year',)
    actions        = ['approve_selected', 'reject_selected']
    inlines        = [WorkExperienceInline, EducationInline]
    readonly_fields = ('profile_views', 'created_at', 'updated_at')

    def approve_selected(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=AlumniProfile.Status.APPROVED,
            approved_at=timezone.now(),
            approved_by=request.user,
        )
        for profile in queryset:
            profile.user.is_active = True
            profile.user.save()
        self.message_user(request, f'{updated} alumni approved.')
    approve_selected.short_description = 'Approve selected alumni'

    def reject_selected(self, request, queryset):
        updated = queryset.update(status=AlumniProfile.Status.REJECTED)
        self.message_user(request, f'{updated} alumni rejected.')
    reject_selected.short_description = 'Reject selected alumni'
