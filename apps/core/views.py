"""
Views for Core app - Notifications & Dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Notification
from .services import NotificationService


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('core:login')


@login_required
def dashboard(request):
    """
    Modern Professional Dashboard with Real Data
    """
    from apps.properties.models import Property
    from apps.contracts.models import Contract, ContractPayment
    from apps.maintenance.models import MaintenanceRequest
    from apps.sales.models import SalesContract, PropertyReservation, SalesPayment
    from apps.clients.models import Client
    from apps.owners.models import Owner
    from apps.financial.models import Payment, Invoice
    from django.db.models import Count, Sum, Q, Avg
    from decimal import Decimal
    import json
    
    # Date ranges
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # ============ PROPERTIES STATISTICS ============
    properties_qs = Property.objects.all()
    total_properties = properties_qs.count()
    available_properties = properties_qs.filter(status='available').count()
    rented_properties = properties_qs.filter(status='rented').count()
    under_maintenance = properties_qs.filter(status='maintenance').count()
    sold_properties = properties_qs.filter(is_for_sale=True).count()
    
    # Properties by type
    property_types_data = properties_qs.values('property_type__name').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    # Properties by city
    properties_by_city = properties_qs.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # ============ CONTRACTS STATISTICS ============
    contracts_qs = Contract.objects.all()
    total_contracts = contracts_qs.count()
    active_contracts = contracts_qs.filter(status='active').count()
    expired_contracts = contracts_qs.filter(status='expired').count()
    expiring_soon = contracts_qs.filter(
        status='active',
        end_date__lte=today + timedelta(days=30),
        end_date__gte=today
    ).count()
    
    # Contracts created this month
    new_contracts_month = contracts_qs.filter(
        created_at__gte=first_day_month
    ).count()
    
    # ============ FINANCIAL STATISTICS ============
    # Payments this month (all payments with invoices)
    payments_month = Payment.objects.filter(
        payment_date__gte=first_day_month,
        invoice__isnull=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Total revenue (all time)
    total_revenue = Payment.objects.filter(
        invoice__isnull=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Invoices pending payment
    pending_invoices = Invoice.objects.filter(
        status='issued'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Sales revenue (using contract payments)
    sales_revenue = SalesPayment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # ============ MAINTENANCE STATISTICS ============
    maintenance_qs = MaintenanceRequest.objects.all()
    total_maintenance = maintenance_qs.count()
    pending_maintenance = maintenance_qs.filter(status='pending').count()
    in_progress_maintenance = maintenance_qs.filter(status='in_progress').count()
    completed_maintenance = maintenance_qs.filter(status='completed').count()
    urgent_maintenance = maintenance_qs.filter(priority='urgent', status__in=['pending', 'in_progress']).count()
    
    # Maintenance costs this month
    maintenance_costs = maintenance_qs.filter(
        request_date__gte=first_day_month,
        estimated_cost__isnull=False
    ).aggregate(total=Sum('estimated_cost'))['total'] or Decimal('0')
    
    # ============ CLIENTS & OWNERS ============
    total_clients = Client.objects.filter(is_active=True).count()
    total_owners = Owner.objects.filter(is_active=True).count()
    new_clients_month = Client.objects.filter(created_at__gte=first_day_month).count()
    
    # ============ SALES STATISTICS ============
    sales_qs = SalesContract.objects.all()
    total_sales = sales_qs.count()
    active_sales = sales_qs.filter(status='active').count()
    completed_sales = sales_qs.filter(status='completed').count()
    
    reservations_qs = PropertyReservation.objects.all()
    pending_reservations = reservations_qs.filter(status='pending').count()
    approved_reservations = reservations_qs.filter(status='approved').count()
    
    # ============ RECENT ACTIVITIES ============
    recent_contracts = contracts_qs.select_related('property', 'client').order_by('-created_at')[:6]
    recent_maintenance = maintenance_qs.select_related('property').order_by('-request_date')[:6]
    recent_payments = Payment.objects.select_related('invoice').order_by('-payment_date')[:6]
    
    # ============ ALERTS & WARNINGS ============
    contracts_expiring_7days = contracts_qs.filter(
        status='active',
        end_date__lte=today + timedelta(days=7),
        end_date__gte=today
    ).select_related('property', 'client')[:5]
    
    # Overdue invoices (issued but not paid for 30+ days)
    overdue_invoices = Invoice.objects.filter(
        status='issued',
        invoice_date__lt=today - timedelta(days=30)
    )[:5]
    
    # ============ CHART DATA ============
    # Properties by Type (Pie Chart)
    chart_property_types_labels = [item['property_type__name'] or 'Other' for item in property_types_data]
    chart_property_types_data = [item['count'] for item in property_types_data]
    
    # Properties by City (Bar Chart)
    chart_cities_labels = [item['city'] or 'Unknown' for item in properties_by_city]
    chart_cities_data = [item['count'] for item in properties_by_city]
    
    # Contracts Status (Doughnut Chart)
    chart_contracts_labels = ['Active', 'Expired', 'Terminated']
    chart_contracts_data = [
        active_contracts,
        expired_contracts,
        contracts_qs.filter(status='terminated').count()
    ]
    
    # Monthly Revenue Trend (Line Chart - Last 6 months)
    revenue_trend_labels = []
    revenue_trend_data = []
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_revenue = Payment.objects.filter(
            payment_date__gte=month_start,
            payment_date__lte=month_end,
            invoice__isnull=False
        ).aggregate(total=Sum('amount'))['total'] or 0
        revenue_trend_labels.append(month_start.strftime('%b %Y'))
        revenue_trend_data.append(float(month_revenue))
    
    # ============ PERFORMANCE METRICS ============
    occupancy_rate = (rented_properties / total_properties * 100) if total_properties > 0 else 0
    
    # Calculate average contract duration (in months) from start_date and end_date
    from django.db.models import F, ExpressionWrapper, fields
    active_contracts_with_duration = contracts_qs.filter(
        status='active',
        start_date__isnull=False,
        end_date__isnull=False
    )
    
    if active_contracts_with_duration.exists():
        # Calculate duration for each contract and average
        durations = []
        for contract in active_contracts_with_duration:
            duration_days = (contract.end_date - contract.start_date).days
            duration_months = duration_days / 30.0  # Approximate months
            durations.append(duration_months)
        avg_contract_duration = sum(durations) / len(durations) if durations else 0
    else:
        avg_contract_duration = 0
    
    context = {
        # Main Statistics
        'total_properties': total_properties,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        'under_maintenance': under_maintenance,
        'sold_properties': sold_properties,
        'occupancy_rate': round(occupancy_rate, 1),
        
        'total_contracts': total_contracts,
        'active_contracts': active_contracts,
        'expired_contracts': expired_contracts,
        'expiring_soon': expiring_soon,
        'new_contracts_month': new_contracts_month,
        'avg_contract_duration': round(avg_contract_duration or 0, 1),
        
        'total_maintenance': total_maintenance,
        'pending_maintenance': pending_maintenance,
        'in_progress_maintenance': in_progress_maintenance,
        'completed_maintenance': completed_maintenance,
        'urgent_maintenance': urgent_maintenance,
        'maintenance_costs': maintenance_costs,
        
        'total_clients': total_clients,
        'total_owners': total_owners,
        'new_clients_month': new_clients_month,
        
        'total_sales': total_sales,
        'active_sales': active_sales,
        'completed_sales': completed_sales,
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations,
        
        # Financial
        'total_revenue': total_revenue,
        'payments_month': payments_month,
        'pending_payments': pending_invoices,
        'sales_revenue': sales_revenue,
        
        # Recent Activities
        'recent_contracts': recent_contracts,
        'recent_maintenance': recent_maintenance,
        'recent_payments': recent_payments,
        
        # Alerts
        'contracts_expiring_7days': contracts_expiring_7days,
        'overdue_invoices': overdue_invoices,
        
        # Notifications
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        
        # Chart Data (JSON)
        'chart_property_types_labels': json.dumps(chart_property_types_labels),
        'chart_property_types_data': json.dumps(chart_property_types_data),
        'chart_cities_labels': json.dumps(chart_cities_labels),
        'chart_cities_data': json.dumps(chart_cities_data),
        'chart_contracts_labels': json.dumps(chart_contracts_labels),
        'chart_contracts_data': json.dumps(chart_contracts_data),
        'revenue_trend_labels': json.dumps(revenue_trend_labels),
        'revenue_trend_data': json.dumps(revenue_trend_data),
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def notification_list(request):
    """
    List all notifications for the current user
    """
    # Get filter parameters
    filter_type = request.GET.get('type', 'all')
    filter_status = request.GET.get('status', 'all')
    
    # Base queryset
    notifications = Notification.objects.filter(user=request.user)
    
    # Apply filters
    if filter_type != 'all':
        notifications = notifications.filter(notification_type=filter_type)
    
    if filter_status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_status == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Order by date
    notifications = notifications.order_by('-created_at')
    
    # Paginate
    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Get statistics
    total_count = Notification.objects.filter(user=request.user).count()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    read_count = total_count - unread_count
    
    context = {
        'notifications': page_obj,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
        'filter_type': filter_type,
        'filter_status': filter_status,
        'notification_types': Notification.NOTIFICATION_TYPES,
    }
    return render(request, 'core/notifications/list.html', context)


@login_required
def notification_mark_as_read(request, pk):
    """
    Mark a single notification as read
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': NotificationService.get_unread_count(request.user)
        })
    
    return redirect(notification.link if notification.link else 'core:notification_list')


@login_required
def notification_mark_all_as_read(request):
    """
    Mark all notifications as read for the current user
    """
    if request.method == 'POST':
        count = NotificationService.mark_all_as_read(request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'count': count,
                'unread_count': 0
            })
        
        return redirect('core:notification_list')
    
    return redirect('core:notification_list')


@login_required
def notification_delete(request, pk):
    """
    Delete a notification
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    if request.method == 'POST':
        notification.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'unread_count': NotificationService.get_unread_count(request.user)
            })
        
        return redirect('core:notification_list')
    
    return redirect('core:notification_list')


@login_required
def notification_unread_count(request):
    """
    Get unread notification count (AJAX endpoint)
    """
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({
        'count': count
    })


@login_required
def notification_recent(request):
    """
    Get recent notifications (AJAX endpoint for dropdown)
    """
    notifications = NotificationService.get_recent_notifications(request.user, limit=10)
    
    data = {
        'count': NotificationService.get_unread_count(request.user),
        'notifications': [
            {
                'id': n.pk,
                'title': n.title,
                'message': n.message[:100],
                'type': n.notification_type,
                'priority': n.priority,
                'is_read': n.is_read,
                'link': n.link,
                'created_at': n.created_at.isoformat(),
            }
            for n in notifications
        ]
    }
    
    return JsonResponse(data)
