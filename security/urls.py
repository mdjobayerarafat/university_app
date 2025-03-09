from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('reports/', views.report_list, name='report_list'),
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/<int:pk>/update/', views.update_report, name='update_report'),
]