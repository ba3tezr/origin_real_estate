"""
URL configuration for Core app - Notifications & Dashboard
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Notification URLs
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.notification_mark_as_read, name='notification_mark_as_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_as_read, name='notification_mark_all_as_read'),
    path('notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),

    # AJAX endpoints
    path('api/notifications/count/', views.notification_unread_count, name='notification_unread_count'),
    path('api/notifications/recent/', views.notification_recent, name='notification_recent'),
]
