from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('',                    views.conversation_list, name='list'),
    path('send/',               views.send_message,      name='send'),
    path('send/<int:conv_pk>/', views.send_message,      name='send_to_conv'),
    path('unread/',             views.unread_count,      name='unread_count'),
    path('contact/',            views.contact_view,      name='contact'),
    path('admin/',              views.admin_messages,    name='admin'),
]
