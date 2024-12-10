from django.contrib import admin
from django.urls import path, include
from . import views as chat_views

urlpatterns = [
    path('', chat_views.chat_home, name='chat-home'),
    path('myconnectionrequests/', chat_views.view_my_requests, name='viewmyconnectionrequests'),  # This is the name to use
    path('reject-request/<int:request_id>/', chat_views.reject_connection_request, name='reject_connection_request'),
    path('viewall/', chat_views.viewallpeers, name='viewall'),
   # path('myrequests/', chat_views.view_my_requests, name='view_my_requests'),
    path('approve-request/<int:request_id>/', chat_views.approve_connection_request, name='approve_connection_request'),
    path('send-request/<int:profile_id>/', chat_views.send_connection_request, name='send_connection_request'),
    path('<slug:slug>/', chat_views.chat_room, name='chat-room'),
    path('upload/<str:room_name>/', chat_views.upload_file, name='upload_file'),
]
