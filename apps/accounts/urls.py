# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',              views.login_view,             name='login'),
    path('logout/',             views.logout_view,            name='logout'),
    path('register/student/',   views.register_student,       name='register_student'),
    path('register/alumni/',    views.register_alumni,        name='register_alumni'),
    path('forgot-password/',    views.forgot_password,        name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.reset_password,     name='reset_password'),
    path('change-password/',    views.change_password,        name='change_password'),
    path('settings/',           views.user_settings,          name='settings'),
    path('notifications/',      views.notifications_view,     name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_read'),
    path('notifications/mark-all/', views.mark_all_read,      name='mark_all_read'),
    path('search/',             views.quick_search,           name='quick_search'),
]
