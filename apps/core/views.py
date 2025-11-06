"""
Views for Core app - Authentication and Dashboard.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Notification, SystemSetting
from apps.properties.models import Property
from apps.contracts.models import Contract
from apps.maintenance.models import MaintenanceRequest
from apps.clients.models import Client
from apps.owners.models import Owner

def user_login(request):
    """Login view."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry
            if not remember:
                request.session.set_expiry(0)
            
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Get system logo
    try:
        logo_setting = SystemSetting.objects.get(key='system_logo')
        logo_url = logo_setting.value
    except SystemSetting.DoesNotExist:
        logo_url = None
    
    context = {
        'logo_url': logo_url,
    }
    return render(request, 'login.html', context)

def user_logout(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:login')

@login_required
def dashboard(request):
    """Dashboard view with statistics."""
    
    # Get statistics
    total_properties = Property.objects.filter(is_active=True).count()
    available_properties = Property.objects.filter(
        status='available',
        is_active=True
    ).count()
    rented_properties = Property.objects.filter(
        status='rented',
        is_active=True
    ).count()
    
    active_contracts = Contract.objects.filter(status='active').count()
    total_contracts = Contract.objects.count()
    
    pending_maintenance = MaintenanceRequest.objects.filter(
        status='pending'
    ).count()
    in_progress_maintenance = MaintenanceRequest.objects.filter(
        status='in_progress'
    ).count()
    
    total_clients = Client.objects.filter(is_active=True).count()
    total_owners = Owner.objects.filter(is_active=True).count()
    
    # Get recent notifications
    recent_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    # Chart data - Properties by type
    properties_by_type = Property.objects.values(
        'property_type__name'
    ).annotate(count=Count('id'))
    
    chart_labels = [item['property_type__name'] or 'Unknown' for item in properties_by_type]
    chart_data = [item['count'] for item in properties_by_type]
    
    # Recent activities
    recent_maintenance = MaintenanceRequest.objects.select_related(
        'property'
    ).order_by('-request_date')[:5]
    
    recent_contracts = Contract.objects.select_related(
        'property', 'client'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        'active_contracts': active_contracts,
        'total_contracts': total_contracts,
        'pending_maintenance': pending_maintenance,
        'in_progress_maintenance': in_progress_maintenance,
        'total_clients': total_clients,
        'total_owners': total_owners,
        'recent_notifications': recent_notifications,
        'unread_notifications_count': unread_notifications_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'recent_maintenance': recent_maintenance,
        'recent_contracts': recent_contracts,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    """User profile view."""
    if request.method == 'POST':
        # Update profile
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        if hasattr(user, 'profile'):
            profile = user.profile
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            profile.language = request.POST.get('language', 'en')
            
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
        
        return redirect('core:profile')
    
    return render(request, 'profile.html')

@login_required
def notifications(request):
    """Notifications view."""
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    context = {
        'notifications': user_notifications,
    }
    
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read."""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        messages.success(request, 'Notification marked as read.')
    except Notification.DoesNotExist:
        messages.error(request, 'Notification not found.')
    
    return redirect('core:notifications')

@login_required
def online_users(request):
    """View online users (placeholder for future implementation)."""
    # This will be implemented with WebSockets or session tracking
    context = {
        'message': 'Online users feature is under development.',
        'status': 'coming_soon'
    }
    return render(request, 'online_users.html', context)
