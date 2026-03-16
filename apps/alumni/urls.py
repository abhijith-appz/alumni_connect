from django.urls import path
from . import views

app_name = 'alumni'

urlpatterns = [
    path('dashboard/',    views.dashboard,      name='dashboard'),
    path('profile/',      views.alumni_profile, name='profile'),
    path('profile/edit/', views.edit_profile,   name='edit_profile'),
    path('network/',      views.alumni_network, name='network'),
    path('students/',     views.view_students,  name='students'),
    path('events/',       views.alumni_events,  name='events'),
]
