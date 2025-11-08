from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from apps.sales.models import Buyer, PropertyReservation, SalesContract, SalesPayment


@login_required
def sales_dashboard(request):
    """Sales module dashboard with statistics and charts"""
    
    # Date ranges
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    this_year_start = today.replace(month=1, day=1)
    
    # Buyers statistics
    total_buyers = Buyer.objects.count()
    qualified_buyers = Buyer.objects.filter(is_qualified=True, is_active=True).count()
    new_buyers_this_month = Buyer.objects.filter(created_at__gte=this_month_start).count()
    
    # Reservations statistics
    total_reservations = PropertyReservation.objects.count()
    active_reservations = PropertyReservation.objects.filter(
        status__in=['pending', 'approved'],
        expiry_date__gte=today
    ).count()
    expired_reservations = PropertyReservation.objects.filter(
        status='pending',
        expiry_date__lt=today
    ).count()
    
    # Contracts statistics
    contracts_stats = SalesContract.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status__in=['signed', 'in_progress'])),
        completed=Count('id', filter=Q(status='completed')),
        this_month=Count('id', filter=Q(contract_date__gte=this_month_start)),
        total_value=Sum('sale_price'),
        avg_value=Avg('sale_price'),
    )
    
    # Payments statistics
    payments_stats = SalesPayment.objects.filter(status='completed').aggregate(
        total=Count('id'),
        total_amount=Sum('amount'),
        this_month_amount=Sum('amount', filter=Q(payment_date__gte=this_month_start)),
        this_year_amount=Sum('amount', filter=Q(payment_date__gte=this_year_start)),
    )
    
    # Recent activities
    recent_buyers = Buyer.objects.order_by('-created_at')[:5]
    recent_contracts = SalesContract.objects.select_related('property', 'buyer').order_by('-created_at')[:5]
    recent_payments = SalesPayment.objects.select_related('sales_contract').order_by('-payment_date')[:10]
    pending_reservations = PropertyReservation.objects.filter(
        status='pending'
    ).select_related('property', 'buyer').order_by('-created_at')[:5]
    
    # Overdue installments
    overdue_installments = SalesContract.objects.filter(
        has_installments=True,
        payment_plans__is_paid=False,
        payment_plans__due_date__lt=today
    ).distinct().count()
    
    # Sales by month (last 6 months)
    monthly_sales = []
    for i in range(6):
        month_start = (this_month_start - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        sales = SalesContract.objects.filter(
            contract_date__gte=month_start,
            contract_date__lte=month_end
        ).aggregate(
            count=Count('id'),
            total=Sum('sale_price')
        )
        
        monthly_sales.insert(0, {
            'month': month_start.strftime('%b %Y'),
            'count': sales['count'] or 0,
            'total': sales['total'] or 0,
        })
    
    context = {
        # Buyers
        'total_buyers': total_buyers,
        'qualified_buyers': qualified_buyers,
        'new_buyers_this_month': new_buyers_this_month,
        
        # Reservations
        'total_reservations': total_reservations,
        'active_reservations': active_reservations,
        'expired_reservations': expired_reservations,
        
        # Contracts
        'total_contracts': contracts_stats['total'] or 0,
        'active_contracts': contracts_stats['active'] or 0,
        'completed_contracts': contracts_stats['completed'] or 0,
        'contracts_this_month': contracts_stats['this_month'] or 0,
        'total_sales_value': contracts_stats['total_value'] or 0,
        'avg_sale_value': contracts_stats['avg_value'] or 0,
        
        # Payments
        'total_payments': payments_stats['total'] or 0,
        'total_payments_amount': payments_stats['total_amount'] or 0,
        'payments_this_month': payments_stats['this_month_amount'] or 0,
        'payments_this_year': payments_stats['this_year_amount'] or 0,
        
        # Alerts
        'overdue_installments': overdue_installments,
        
        # Recent activities
        'recent_buyers': recent_buyers,
        'recent_contracts': recent_contracts,
        'recent_payments': recent_payments,
        'pending_reservations': pending_reservations,
        
        # Charts data
        'monthly_sales': monthly_sales,
    }
    
    return render(request, 'sales/dashboard.html', context)
