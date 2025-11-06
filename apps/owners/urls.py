"""
URL configuration for Owners app
"""
from django.urls import path
from . import views

app_name = 'owners'

urlpatterns = [
    path('', views.owner_list, name='list'),
    path('create/', views.owner_create, name='create'),
    path('<int:pk>/edit/', views.owner_update, name='update'),
    path('<int:pk>/delete/', views.owner_delete, name='delete'),
]
