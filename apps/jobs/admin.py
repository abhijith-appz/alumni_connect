from django.contrib import admin
from .models import Job, JobApplication, SavedJob


class JobApplicationInline(admin.TabularInline):
    model           = JobApplication
    extra           = 0
    readonly_fields = ('applicant', 'status', 'applied_at')
    can_delete      = False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display    = ('title', 'company', 'job_type', 'location', 'status',
                       'posted_by', 'applications_count', 'views', 'created_at')
    list_filter     = ('status', 'job_type', 'domain')
    search_fields   = ('title', 'company', 'location', 'skills')
    ordering        = ('-created_at',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines         = [JobApplicationInline]

    def applications_count(self, obj):
        return obj.applications.count()
    applications_count.short_description = 'Applications'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display  = ('applicant', 'job', 'status', 'applied_at')
    list_filter   = ('status',)
    search_fields = ('applicant__username', 'job__title')
    ordering      = ('-applied_at',)
