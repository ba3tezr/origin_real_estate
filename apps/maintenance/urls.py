"""
URL configuration for Maintenance app
"""
from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.maintenance_list, name='list'),
    path('create/', views.maintenance_create, name='create'),
    path('<int:pk>/', views.maintenance_detail, name='detail'),
    path('<int:pk>/edit/', views.maintenance_update, name='update'),
    path('<int:pk>/delete/', views.maintenance_delete, name='delete'),
    path('<int:pk>/attachments/add/', views.maintenance_attachment_create, name='attachment_create'),
    path('attachments/<int:pk>/delete/', views.maintenance_attachment_delete, name='attachment_delete'),
    path('<int:pk>/schedules/add/', views.maintenance_schedule_create, name='schedule_create'),
    path('schedules/<int:pk>/edit/', views.maintenance_schedule_update, name='schedule_update'),
    path('schedules/<int:pk>/delete/', views.maintenance_schedule_delete, name='schedule_delete'),
]
