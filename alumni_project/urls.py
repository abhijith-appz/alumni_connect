from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.accounts.views import (
    login_view, logout_view, register_student, register_alumni,
    forgot_password, reset_password, change_password,
    user_settings, notifications_view, mark_all_read,
    mark_notification_read, quick_search,
)
from apps.students.views import (
    dashboard as student_dashboard, student_profile,
    alumni_search, career_guidance, alumni_profile_public,
)
from apps.alumni.views import (
    dashboard as alumni_dashboard, alumni_profile,
    edit_profile as edit_alumni_profile, alumni_network,
    view_students, alumni_events,
)
from apps.jobs.views import (
    job_list, job_detail, apply_job, post_job, manage_jobs,
    edit_job, close_job, activate_job, delete_job,
    internship_list, toggle_save_job,
)
from apps.events.views import (
    event_list, event_detail, register_for_event,
    admin_manage_events, edit_event, delete_event,
)
from apps.messaging.views import (
    conversation_list, send_message, contact_view, admin_messages,
)
from apps.ai_assistant.views import (
    ai_chat, ai_career_guidance, ai_alumni_finder,
    ai_job_recommendations, ai_help_center,
)
from apps.core.views import (
    home, about, faq, public_alumni_directory, dashboard_redirect,
    admin_dashboard, manage_students, manage_alumni,
    approve_alumni, reject_alumni, system_reports,
    manage_admin_jobs, admin_delete_job, manage_announcements,
    admin_student_detail, admin_edit_student, admin_alumni_detail,
    delete_announcement, edit_announcement,
    error_404, error_403,
)

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # ── Public ────────────────────────────────────────────────────────────────
    path('',           home,                      name='home'),
    path('about/',     about,                     name='about'),
    path('faq/',       faq,                       name='faq'),
    path('contact/',   contact_view,              name='contact'),
    path('directory/', public_alumni_directory,   name='alumni_directory'),

    # ── Auth ──────────────────────────────────────────────────────────────────
    path('auth/login/',                       login_view,          name='login'),
    path('auth/logout/',                      logout_view,         name='logout'),
    path('auth/register/student/',            register_student,    name='register_student'),
    path('auth/register/alumni/',             register_alumni,     name='register_alumni'),
    path('auth/forgot-password/',             forgot_password,     name='forgot_password'),
    path('auth/reset/<uidb64>/<token>/',      reset_password,      name='reset_password'),
    path('auth/change-password/',             change_password,     name='change_password'),
    path('auth/settings/',                    user_settings,       name='user_settings'),
    path('auth/notifications/',               notifications_view,  name='notifications'),
    path('auth/notifications/<int:pk>/read/', mark_notification_read, name='mark_read'),
    path('auth/notifications/mark-all/',      mark_all_read,       name='mark_all_read'),

    # ── Student ───────────────────────────────────────────────────────────────
    path('student/dashboard/',       student_dashboard,     name='student_dashboard'),
    path('student/profile/',         student_profile,       name='student_profile'),
    path('student/search-alumni/',   alumni_search,         name='alumni_search'),
    path('student/career-guidance/', career_guidance,       name='career_guidance'),
    path('student/alumni/<int:pk>/', alumni_profile_public, name='alumni_profile_public'),

    # ── Alumni ────────────────────────────────────────────────────────────────
    path('alumni/dashboard/',       alumni_dashboard,    name='alumni_dashboard'),
    path('alumni/profile/',         alumni_profile,      name='alumni_profile'),
    path('alumni/profile/edit/',    edit_alumni_profile, name='edit_alumni_profile'),
    path('alumni/network/',         alumni_network,      name='alumni_network'),
    path('alumni/students/',        view_students,       name='view_students'),
    path('alumni/events/',          alumni_events,       name='alumni_events'),

    # ── Jobs (order matters: specific paths before <int:pk>) ─────────────────
    path('jobs/',                   job_list,         name='student_jobs'),
    path('jobs/post/',              post_job,         name='post_job'),
    path('jobs/manage/',            manage_jobs,      name='manage_jobs'),
    path('jobs/internships/',       internship_list,  name='student_internships'),
    path('jobs/<int:pk>/',          job_detail,       name='job_detail'),
    path('jobs/<int:pk>/apply/',    apply_job,        name='apply_job'),
    path('jobs/<int:pk>/save/',     toggle_save_job,  name='save_job'),
    path('jobs/<int:pk>/edit/',     edit_job,         name='edit_job'),
    path('jobs/<int:pk>/close/',    close_job,        name='close_job'),
    path('jobs/<int:pk>/activate/', activate_job,     name='activate_job'),
    path('jobs/<int:pk>/delete/',   delete_job,       name='delete_job'),

    # ── Events (specific before <int:pk>) ────────────────────────────────────
    path('events/',                   event_list,           name='student_events'),
    path('events/manage/',            admin_manage_events,  name='manage_events'),
    path('events/<int:pk>/',          event_detail,         name='event_detail'),
    path('events/<int:pk>/register/', register_for_event,   name='event_register'),
    path('events/<int:pk>/edit/',     edit_event,           name='edit_event'),
    path('events/<int:pk>/delete/',   delete_event,         name='delete_event'),

    # ── Messages ──────────────────────────────────────────────────────────────
    path('messages/',                  conversation_list, name='student_messages'),
    path('messages/alumni/',           conversation_list, name='alumni_messages'),
    path('messages/send/',             send_message,      name='send_message'),
    path('messages/send/<int:conv_pk>/', send_message,    name='send_to_conv'),
    path('staff/messages/',            admin_messages,    name='admin_messages'),

    # ── AI ────────────────────────────────────────────────────────────────────
    path('ai/chat/',                   ai_chat,                name='ai_chat'),
    path('ai/career-guidance/',        ai_career_guidance,     name='ai_career_guidance'),
    path('ai/alumni-finder/',          ai_alumni_finder,       name='ai_alumni_finder'),
    path('ai/job-recommendations/',    ai_job_recommendations, name='ai_job_recommendations'),
    path('ai/help/',                   ai_help_center,         name='ai_help_center'),

    # ── Staff / Admin ─────────────────────────────────────────────────────────
    path('staff/dashboard/',             admin_dashboard,     name='admin_dashboard'),
    path('staff/students/',              manage_students,     name='manage_students'),
    path('staff/alumni/',                manage_alumni,       name='manage_alumni'),
    path('staff/alumni/<int:pk>/approve/', approve_alumni,   name='approve_alumni'),
    path('staff/alumni/<int:pk>/reject/',  reject_alumni,    name='reject_alumni'),
    path('staff/jobs/',                  manage_admin_jobs,   name='admin_manage_jobs'),
    path('staff/jobs/<int:pk>/delete/',  admin_delete_job,   name='admin_delete_job'),
    path('staff/reports/',               system_reports,      name='system_reports'),
    path('staff/announcements/',         manage_announcements, name='manage_announcements'),


    path('staff/students/<int:pk>/',       admin_student_detail,  name='admin_student_detail'),
    path('staff/students/<int:pk>/edit/',  admin_edit_student,    name='admin_edit_student'),
    path('staff/alumni/<int:pk>/',         admin_alumni_detail,   name='admin_alumni_detail'),
    path('staff/announcements/<int:pk>/delete/', delete_announcement, name='delete_announcement'),
    path('staff/announcements/<int:pk>/edit/',   edit_announcement,   name='edit_announcement'),

    # ── Dashboard redirect ────────────────────────────────────────────────────
    path('dashboard/', dashboard_redirect, name='dashboard'),

    # ── REST API ──────────────────────────────────────────────────────────────
    path('api/v1/', include([
        path('accounts/', include('apps.accounts.api_urls')),
        path('alumni/',   include('apps.alumni.api_urls')),
        path('jobs/',     include('apps.jobs.api_urls')),
        path('events/',   include('apps.events.api_urls')),
        path('messages/', include('apps.messaging.api_urls')),
        path('ai/',       include('apps.ai_assistant.api_urls')),
        path('search/',   include('apps.core.search_urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'apps.core.views.error_404'
handler403 = 'apps.core.views.error_403'
handler500 = 'apps.core.views.error_500'
