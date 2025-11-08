"""
URL configuration for Contracts app
"""
from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list, name='list'),
    path('create/', views.contract_create, name='create'),
    path('<int:pk>/', views.contract_detail, name='detail'),
    path('<int:pk>/edit/', views.contract_update, name='update'),
    path('<int:pk>/delete/', views.contract_delete, name='delete'),
    path('<int:contract_pk>/payments/add/', views.contract_payment_create, name='payment_create'),
    path('payments/<int:pk>/delete/', views.contract_payment_delete, name='payment_delete'),
    path('<int:contract_pk>/renewals/add/', views.contract_renewal_create, name='renewal_create'),
    path('renewals/<int:pk>/delete/', views.contract_renewal_delete, name='renewal_delete'),
]
