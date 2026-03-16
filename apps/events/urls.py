# ── events/urls.py ────────────────────────────────────────────────────────────
from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('',                         views.event_list,          name='list'),
    path('<int:pk>/',                views.event_detail,        name='detail'),
    path('<int:pk>/register/',       views.register_for_event,  name='register'),
    path('manage/',                  views.admin_manage_events, name='admin_manage'),
    path('<int:pk>/edit/',           views.edit_event,          name='edit'),
    path('<int:pk>/delete/',         views.delete_event,        name='delete'),
]
