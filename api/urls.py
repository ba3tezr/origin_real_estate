"""
API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets (will be created)
# from .viewsets import property_viewsets, contract_viewsets

router = DefaultRouter()

# Register viewsets here
# router.register(r'properties', property_viewsets.PropertyViewSet)
# router.register(r'contracts', contract_viewsets.ContractViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
