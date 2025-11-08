from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models
from datetime import timedelta
from decimal import Decimal

from apps.sales.models import (
    Buyer,
    PropertyReservation,
    SalesContract,
    SalesPaymentPlan,
    SalesPayment
)
from .serializers import (
    BuyerSerializer,
    BuyerListSerializer,
    PropertyReservationSerializer,
    SalesContractSerializer,
    SalesContractListSerializer,
    SalesPaymentPlanSerializer,
    SalesPaymentSerializer,
)


class BuyerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing buyers
    """
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['buyer_type', 'is_qualified', 'is_active', 'financing_approved']
    search_fields = ['name', 'email', 'phone', 'national_id']
    ordering_fields = ['created_at', 'name', 'credit_score']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BuyerListSerializer
        return BuyerSerializer
    
    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """Qualify a buyer"""
        buyer = self.get_object()
        if buyer.qualify_buyer():
            return Response({'status': 'Buyer qualified successfully'})
        return Response(
            {'status': 'Buyer does not meet qualification criteria'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def qualified(self, request):
        """Get all qualified buyers"""
        qualified_buyers = self.queryset.filter(is_qualified=True, is_active=True)
        serializer = self.get_serializer(qualified_buyers, many=True)
        return Response(serializer.data)


class PropertyReservationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing property reservations
    """
    queryset = PropertyReservation.objects.select_related('property', 'buyer', 'reserved_by').all()
    serializer_class = PropertyReservationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'property', 'buyer']
    search_fields = ['reservation_number', 'property__code', 'buyer__name']
    ordering_fields = ['reservation_date', 'expiry_date']
    ordering = ['-reservation_date']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a reservation"""
        reservation = self.get_object()
        if reservation.status == 'pending':
            reservation.status = 'approved'
            reservation.save()
            return Response({'status': 'Reservation approved'})
        return Response(
            {'status': 'Reservation cannot be approved'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()
        reason = request.data.get('reason', '')
        reservation.cancel_reservation(reason)
        return Response({'status': 'Reservation cancelled'})
    
    @action(detail=True, methods=['post'])
    def convert_to_sale(self, request, pk=None):
        """Convert reservation to sales contract"""
        reservation = self.get_object()
        if reservation.convert_to_sale():
            return Response({'status': 'Reservation converted to sale'})
        return Response(
            {'status': 'Cannot convert reservation. Must be approved first.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired reservations"""
        expired = self.queryset.filter(
            expiry_date__lt=timezone.now().date(),
            status='pending'
        )
        serializer = self.get_serializer(expired, many=True)
        return Response(serializer.data)


class SalesContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales contracts
    """
    queryset = SalesContract.objects.select_related(
        'property', 'buyer', 'seller', 'created_by', 'approved_by'
    ).prefetch_related('payment_plans', 'payments').all()
    serializer_class = SalesContractSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'has_financing', 'has_installments', 'is_registered',
        'property', 'buyer', 'seller'
    ]
    search_fields = ['contract_number', 'property__code', 'buyer__name']
    ordering_fields = ['contract_date', 'sale_price', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SalesContractListSerializer
        return SalesContractSerializer
    
    @action(detail=True, methods=['post'])
    def generate_payment_plan(self, request, pk=None):
        """Generate payment plan for contract"""
        contract = self.get_object()
        
        if not contract.has_installments:
            return Response(
                {'status': 'Contract does not have installments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete existing payment plans
        contract.payment_plans.all().delete()
        
        # Calculate installment amount
        remaining_amount = contract.sale_price - contract.down_payment - contract.financed_amount
        installment_amount = remaining_amount / contract.number_of_installments
        
        # Generate payment plans
        for i in range(1, contract.number_of_installments + 1):
            if contract.installment_frequency == 'monthly':
                due_date = contract.contract_date + timedelta(days=30*i)
            elif contract.installment_frequency == 'quarterly':
                due_date = contract.contract_date + timedelta(days=90*i)
            elif contract.installment_frequency == 'semi_annual':
                due_date = contract.contract_date + timedelta(days=180*i)
            else:  # annual
                due_date = contract.contract_date + timedelta(days=365*i)
            
            SalesPaymentPlan.objects.create(
                sales_contract=contract,
                installment_number=i,
                due_date=due_date,
                amount=installment_amount
            )
        
        return Response({'status': f'Generated {contract.number_of_installments} payment plans'})
    
    @action(detail=True, methods=['get'])
    def payment_summary(self, request, pk=None):
        """Get payment summary for contract"""
        contract = self.get_object()
        return Response({
            'sale_price': float(contract.sale_price),
            'total_paid': float(contract.get_total_paid()),
            'remaining_amount': float(contract.get_remaining_amount()),
            'payment_progress': contract.get_payment_progress_percentage(),
            'is_fully_paid': contract.is_fully_paid(),
            'number_of_payments': contract.payments.count(),
            'completed_payments': contract.payments.filter(status='completed').count(),
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active contracts"""
        active = self.queryset.filter(status__in=['signed', 'in_progress'])
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get sales statistics"""
        from django.db.models import Sum, Count, Avg
        
        stats = self.queryset.aggregate(
            total_contracts=Count('id'),
            total_value=Sum('sale_price'),
            average_price=Avg('sale_price'),
            completed=Count('id', filter=models.Q(status='completed')),
            active=Count('id', filter=models.Q(status__in=['signed', 'in_progress'])),
        )
        
        return Response(stats)


class SalesPaymentPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment plans
    """
    queryset = SalesPaymentPlan.objects.select_related('sales_contract').all()
    serializer_class = SalesPaymentPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sales_contract', 'is_paid', 'is_overdue']
    ordering_fields = ['due_date', 'installment_number']
    ordering = ['due_date']
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark installment as paid"""
        plan = self.get_object()
        reference = request.data.get('payment_reference', '')
        plan.mark_as_paid(reference)
        return Response({'status': 'Payment plan marked as paid'})
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue payment plans"""
        overdue = self.queryset.filter(
            is_paid=False,
            due_date__lt=timezone.now().date()
        )
        for plan in overdue:
            plan.check_overdue()
        
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)


class SalesPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales payments
    """
    queryset = SalesPayment.objects.select_related(
        'sales_contract', 'payment_plan', 'received_by'
    ).all()
    serializer_class = SalesPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sales_contract', 'payment_type', 'payment_method', 'status']
    search_fields = ['receipt_number', 'reference_number', 'sales_contract__contract_number']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm payment"""
        payment = self.get_object()
        if payment.status == 'pending':
            payment.status = 'completed'
            payment.save()
            
            # Update payment plan if linked
            if payment.payment_plan:
                payment.payment_plan.mark_as_paid(payment.receipt_number)
            
            return Response({'status': 'Payment confirmed'})
        return Response(
            {'status': 'Payment cannot be confirmed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent payments (last 30 days)"""
        from_date = timezone.now().date() - timedelta(days=30)
        recent = self.queryset.filter(payment_date__gte=from_date)
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
