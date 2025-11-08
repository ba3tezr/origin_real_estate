"""
Views for Core app - Notifications & Dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Notification
from .services import NotificationService


@login_required
def dashboard(request):
    """
    Main dashboard for the application
    """
    from apps.properties.models import Property
    from apps.contracts.models import Contract
    from apps.maintenance.models import MaintenanceRequest
    from apps.sales.models import SalesContract, PropertyReservation
    
    # Get statistics
    today = timezone.now().date()
    
    context = {
        'total_properties': Property.objects.count(),
        'active_contracts': Contract.objects.filter(status='active').count(),
        'pending_maintenance': MaintenanceRequest.objects.filter(status='pending').count(),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        'total_sales': SalesContract.objects.filter(status='active').count(),
        'pending_reservations': PropertyReservation.objects.filter(status='pending').count(),
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
