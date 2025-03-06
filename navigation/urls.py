from django.urls import path
from . import views

app_name = 'navigation'

urlpatterns = [
    path('buildings/', views.BuildingListView.as_view(), name='building_list'),
    path('buildings/<int:pk>/', views.BuildingDetailView.as_view(), name='building_detail'),
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('markers/', views.ARMarkerListView.as_view(), name='marker_list'),
    path('markers/<int:pk>/', views.ARMarkerDetailView.as_view(), name='marker_detail'),
    path('nearby/', views.NearbyLocationsView.as_view(), name='nearby_locations'),
]