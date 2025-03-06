from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event list and search
    path('', views.EventListView.as_view(), name='event_list'),

    # Event CRUD operations
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),

    # RSVP functionality
    path('<int:pk>/rsvp/', views.rsvp_event, name='rsvp_event'),

    # My Events view
    path('my-events/', views.MyEventsView.as_view(), name='my_events'),
    path('clubs/', views.ClubListView.as_view(), name='club_list'),
    path('clubs/<int:pk>/', views.ClubDetailView.as_view(), name='club_detail'),
]