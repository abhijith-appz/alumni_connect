from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display    = ('user', 'student_id', 'department', 'current_year',
                       'expected_graduation', 'is_job_seeking')
    list_filter     = ('department', 'current_year', 'is_job_seeking')
    search_fields   = ('user__first_name', 'user__last_name', 'student_id')
    ordering        = ('-created_at',)
    readonly_fields = ('profile_views', 'created_at', 'updated_at')
