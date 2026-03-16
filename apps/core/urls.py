# ── core/urls.py ──────────────────────────────────────────────────────────────
from django.urls import path
from . import views
from apps.messaging.views import contact_view

app_name = 'core'

urlpatterns = [
    # Public
    path('',                    views.home,                   name='home'),
    path('about/',              views.about,                  name='about'),
    path('faq/',                views.faq,                    name='faq'),
    path('contact/',            contact_view,                 name='contact'),
    path('directory/',          views.public_alumni_directory,name='directory'),

    # Admin section
    path('staff/dashboard/',    views.admin_dashboard,        name='admin_dashboard'),
    path('staff/students/',     views.manage_students,        name='manage_students'),
    path('staff/alumni/',       views.manage_alumni,          name='manage_alumni'),
    path('staff/alumni/<int:pk>/approve/', views.approve_alumni, name='approve_alumni'),
    path('staff/alumni/<int:pk>/reject/',  views.reject_alumni,  name='reject_alumni'),
    path('staff/jobs/',         views.manage_admin_jobs,      name='manage_jobs'),
    path('staff/jobs/<int:pk>/delete/', views.admin_delete_job, name='delete_job'),
    path('staff/reports/',      views.system_reports,         name='reports'),
    path('staff/announcements/', views.manage_announcements,  name='announcements'),
]
