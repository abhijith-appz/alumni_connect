from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/',       views.dashboard,             name='dashboard'),
    path('profile/',         views.student_profile,       name='profile'),
    path('search-alumni/',   views.alumni_search,         name='alumni_search'),
    path('career-guidance/', views.career_guidance,       name='career_guidance'),
    path('alumni/<int:pk>/', views.alumni_profile_public, name='alumni_profile'),
]
