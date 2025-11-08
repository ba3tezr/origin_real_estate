from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    BuyerViewSet,
    PropertyReservationViewSet,
    SalesContractViewSet,
    SalesPaymentPlanViewSet,
    SalesPaymentViewSet,
)
from .views import (
    # Dashboard
    sales_dashboard,
    # Buyers
    buyer_list, buyer_detail, buyer_create, buyer_update, buyer_delete, buyer_qualify,
    # Reservations
    reservation_list, reservation_detail, reservation_create, reservation_update,
    reservation_approve, reservation_cancel, reservation_convert,
    # Contracts
    contract_list, contract_detail, contract_create, contract_update,
    # Payments
    payment_create, payment_list,
)

app_name = 'sales'

# API Router
router = DefaultRouter()
router.register(r'buyers', BuyerViewSet, basename='api-buyer')
router.register(r'reservations', PropertyReservationViewSet, basename='api-reservation')
router.register(r'contracts', SalesContractViewSet, basename='api-contract')
router.register(r'payment-plans', SalesPaymentPlanViewSet, basename='api-payment-plan')
router.register(r'payments', SalesPaymentViewSet, basename='api-payment')

urlpatterns = [
    # Dashboard
    path('', sales_dashboard, name='dashboard'),
    
    # Buyers
    path('buyers/', buyer_list, name='buyer_list'),
    path('buyers/create/', buyer_create, name='buyer_create'),
    path('buyers/<int:pk>/', buyer_detail, name='buyer_detail'),
    path('buyers/<int:pk>/update/', buyer_update, name='buyer_update'),
    path('buyers/<int:pk>/delete/', buyer_delete, name='buyer_delete'),
    path('buyers/<int:pk>/qualify/', buyer_qualify, name='buyer_qualify'),
    
    # Reservations
    path('reservations/', reservation_list, name='reservation_list'),
    path('reservations/create/', reservation_create, name='reservation_create'),
    path('reservations/<int:pk>/', reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/update/', reservation_update, name='reservation_update'),
    path('reservations/<int:pk>/approve/', reservation_approve, name='reservation_approve'),
    path('reservations/<int:pk>/cancel/', reservation_cancel, name='reservation_cancel'),
    path('reservations/<int:pk>/convert/', reservation_convert, name='reservation_convert'),
    
    # Contracts
    path('contracts/', contract_list, name='contract_list'),
    path('contracts/create/', contract_create, name='contract_create'),
    path('contracts/<int:pk>/', contract_detail, name='contract_detail'),
    path('contracts/<int:pk>/update/', contract_update, name='contract_update'),
    
    # Payments
    path('contracts/<int:contract_pk>/payments/create/', payment_create, name='payment_create'),
    path('payments/', payment_list, name='payment_list'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
