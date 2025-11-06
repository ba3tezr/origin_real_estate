"""
API URLs for Origin App Real Estate Management System
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.viewsets import (
    PropertyTypeViewSet,
    PropertyViewSet,
    PropertyImageViewSet,
    PropertyDocumentViewSet,
    PropertyValuationViewSet,
    PropertyAmenityViewSet,
    PropertyInspectionViewSet,
    PropertyExpenseViewSet,
    PropertyRevenueViewSet,
    OwnerViewSet,
    ClientViewSet,
    ContractViewSet,
    ContractPaymentViewSet,
    ContractRenewalViewSet,
    MaintenanceCategoryViewSet,
    MaintenanceRequestViewSet,
    MaintenanceAttachmentViewSet,
    MaintenanceScheduleViewSet,
)

router = DefaultRouter()

# Properties
router.register(r'properties/types', PropertyTypeViewSet, basename='propertytype')
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'properties/images', PropertyImageViewSet, basename='propertyimage')
router.register(r'properties/documents', PropertyDocumentViewSet, basename='propertydocument')
router.register(r'properties/valuations', PropertyValuationViewSet, basename='propertyvaluation')
router.register(r'properties/amenities', PropertyAmenityViewSet, basename='propertyamenity')
router.register(r'properties/inspections', PropertyInspectionViewSet, basename='propertyinspection')
router.register(r'properties/expenses', PropertyExpenseViewSet, basename='propertyexpense')
router.register(r'properties/revenues', PropertyRevenueViewSet, basename='propertyrevenue')

# Owners & Clients
router.register(r'owners', OwnerViewSet, basename='owner')
router.register(r'clients', ClientViewSet, basename='client')

# Contracts
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'contracts/payments', ContractPaymentViewSet, basename='contractpayment')
router.register(r'contracts/renewals', ContractRenewalViewSet, basename='contractrenewal')

# Maintenance
router.register(r'maintenance/categories', MaintenanceCategoryViewSet, basename='maintenancecategory')
router.register(r'maintenance/requests', MaintenanceRequestViewSet, basename='maintenancerequest')
router.register(r'maintenance/attachments', MaintenanceAttachmentViewSet, basename='maintenanceattachment')
router.register(r'maintenance/schedules', MaintenanceScheduleViewSet, basename='maintenanceschedule')

# Swagger Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Origin App Real Estate API",
        default_version='v1',
        description="REST API for Origin App Real Estate Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@originapp.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # API Documentation
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Router
    path('', include(router.urls)),
]
