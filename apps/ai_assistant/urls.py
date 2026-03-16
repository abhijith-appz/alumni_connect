# ── ai_assistant/urls.py ──────────────────────────────────────────────────────
from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('chat/',               views.ai_chat,                name='chat'),
    path('career-guidance/',    views.ai_career_guidance,     name='career_guidance'),
    path('alumni-finder/',      views.ai_alumni_finder,       name='alumni_finder'),
    path('job-recommendations/',views.ai_job_recommendations, name='job_recommendations'),
    path('help/',               views.ai_help_center,         name='help_center'),
]
