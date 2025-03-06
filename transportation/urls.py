# transportation/urls.py
from django.urls import path
from .views import (
    BusRouteListView,
    BusRouteDetailView,
    BusStopDetailView,
    BusTrackerView,
    BusAlertListView
)

app_name = 'transportation'  # Namespace for the app

urlpatterns = [
    # Bus route URLs
    path('routes/', BusRouteListView.as_view(), name='route_list'),
    path('routes/<int:pk>/', BusRouteDetailView.as_view(), name='route_detail'),

    # Bus stop URLs
    path('stops/<int:pk>/', BusStopDetailView.as_view(), name='stop_detail'),

    # Bus tracking
    path('tracker/', BusTrackerView.as_view(), name='bus_tracker'),

    # Alerts
    path('alerts/', BusAlertListView.as_view(), name='alert_list'),

    # Index page (redirects to route list)
    path('', BusRouteListView.as_view(), name='index'),
]