from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('create/', views.CreateNotificationView.as_view(), name='create'),
    path('<int:pk>/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_read'),
    path('<int:pk>/delete/', views.DeleteNotificationView.as_view(), name='delete'),
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
]