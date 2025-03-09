from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/', views.chatbot_view, name='chat'),
    path('get-response/', views.get_response, name='get_response'),
    path('messages/', views.message_view, name='messages'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/', views.get_messages, name='get_messages'),
]