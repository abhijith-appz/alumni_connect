# ── jobs/urls.py ──────────────────────────────────────────────────────────────
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('',                    views.job_list,       name='list'),
    path('<int:pk>/',           views.job_detail,     name='detail'),
    path('<int:pk>/apply/',     views.apply_job,      name='apply'),
    path('<int:pk>/save/',      views.toggle_save_job,name='save'),
    path('post/',               views.post_job,       name='post'),
    path('manage/',             views.manage_jobs,    name='manage'),
    path('<int:pk>/edit/',      views.edit_job,       name='edit'),
    path('<int:pk>/close/',     views.close_job,      name='close'),
    path('<int:pk>/activate/',  views.activate_job,   name='activate'),
    path('<int:pk>/delete/',    views.delete_job,     name='delete'),
    path('internships/',        views.internship_list,name='internships'),
]
