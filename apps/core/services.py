"""
Notification Service for Origin App
Centralized notification management and delivery
"""
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import Notification, NotificationPreference


class NotificationService:
    """
    Service class for managing notifications
    """
    
    @staticmethod
    def create_notification(
        user,
        title,
        message,
        notification_type='info',
        priority='medium',
        related_object=None,
        link='',
        action_label='',
        action_url='',
        send_email=False,
        metadata=None
    ):
        """
        Create a notification with optional email sending
        """
        notification_data = {
            'user': user,
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'priority': priority,
            'link': link,
            'action_label': action_label,
            'action_url': action_url,
            'metadata': metadata,
        }
        
        # Add related object if provided
        if related_object:
            notification_data['content_type'] = ContentType.objects.get_for_model(related_object)
            notification_data['object_id'] = related_object.pk
        
        # Create notification
        notification = Notification.objects.create(**notification_data)
        
        # Check user preferences and send email if needed
        if send_email:
            try:
                prefs = user.notification_preferences
                if prefs.should_send_email(notification_type):
                    notification.send_email()
            except NotificationPreference.DoesNotExist:
                # No preferences set, send by default
                notification.send_email()
        
        return notification
    
    @staticmethod
    def create_bulk_notification(users, title, message, **kwargs):
        """
        Create notifications for multiple users
        """
        notifications = []
        for user in users:
            notification = NotificationService.create_notification(
                user=user,
                title=title,
                message=message,
                **kwargs
            )
            notifications.append(notification)
        return notifications
    
    # ===================================================================
    # CONTRACT NOTIFICATIONS
    # ===================================================================
    
    @staticmethod
    def notify_contract_expiring(contract, days_until_expiry):
        """
        Send notification when contract is expiring soon
        """
        # Notify property owner
        if hasattr(contract.property, 'owner') and hasattr(contract.property.owner, 'user'):
            owner_user = contract.property.owner.user
            NotificationService.create_notification(
                user=owner_user,
                title=f"Contract Expiring in {days_until_expiry} Days",
                message=f"Contract {contract.contract_number} for property {contract.property.code} expires on {contract.end_date}",
                notification_type='contract_expiry',
                priority='high' if days_until_expiry <= 7 else 'medium',
                related_object=contract,
                link=f'/contracts/{contract.pk}/',
                action_label='View Contract',
                action_url=f'/contracts/{contract.pk}/',
                send_email=True
            )
        
        # Notify assigned staff (superusers)
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        for staff in staff_users:
            NotificationService.create_notification(
                user=staff,
                title=f"Contract Expiring Soon",
                message=f"Contract {contract.contract_number} expires in {days_until_expiry} days",
                notification_type='contract_expiry',
                priority='medium',
                related_object=contract,
                link=f'/contracts/{contract.pk}/',
                send_email=False  # Only in-app for staff
            )
    
    @staticmethod
    def notify_contract_created(contract):
        """
        Send notification when new contract is created
        """
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        for staff in staff_users:
            NotificationService.create_notification(
                user=staff,
                title="New Contract Created",
                message=f"Contract {contract.contract_number} has been created for {contract.property.code}",
                notification_type='info',
                priority='low',
                related_object=contract,
                link=f'/contracts/{contract.pk}/',
                send_email=False
            )
    
    # ===================================================================
    # PAYMENT NOTIFICATIONS
    # ===================================================================
    
    @staticmethod
    def notify_payment_due(contract, days_until_due):
        """
        Send notification when payment is due soon
        """
        # Notify client
        if hasattr(contract.client, 'user'):
            NotificationService.create_notification(
                user=contract.client.user,
                title=f"Payment Due in {days_until_due} Days",
                message=f"Rent payment of EGP {contract.rent_amount} is due on {contract.payment_day}",
                notification_type='payment_due',
                priority='high' if days_until_due <= 3 else 'medium',
                related_object=contract,
                link=f'/contracts/{contract.pk}/',
                action_label='Make Payment',
                action_url=f'/contracts/{contract.pk}/payment/',
                send_email=True
            )
    
    @staticmethod
    def notify_payment_received(payment, contract):
        """
        Send notification when payment is received
        """
        if hasattr(contract.property, 'owner') and hasattr(contract.property.owner, 'user'):
            NotificationService.create_notification(
                user=contract.property.owner.user,
                title="Payment Received",
                message=f"Payment of EGP {payment.amount} received for contract {contract.contract_number}",
                notification_type='success',
                priority='low',
                related_object=payment,
                link=f'/contracts/{contract.pk}/',
                send_email=True
            )
    
    # ===================================================================
    # MAINTENANCE NOTIFICATIONS
    # ===================================================================
    
    @staticmethod
    def notify_maintenance_request_created(maintenance):
        """
        Send notification when new maintenance request is created
        """
        # Notify property owner
        if hasattr(maintenance.property, 'owner') and hasattr(maintenance.property.owner, 'user'):
            NotificationService.create_notification(
                user=maintenance.property.owner.user,
                title="New Maintenance Request",
                message=f"New {maintenance.get_priority_display()} priority request: {maintenance.title}",
                notification_type='maintenance_request',
                priority='high' if maintenance.priority == 'urgent' else 'medium',
                related_object=maintenance,
                link=f'/maintenance/{maintenance.pk}/',
                action_label='View Request',
                action_url=f'/maintenance/{maintenance.pk}/',
                send_email=True
            )
        
        # Notify assigned technician
        if maintenance.assigned_to:
            NotificationService.create_notification(
                user=maintenance.assigned_to,
                title="New Maintenance Assignment",
                message=f"You have been assigned to: {maintenance.title}",
                notification_type='maintenance_request',
                priority='high',
                related_object=maintenance,
                link=f'/maintenance/{maintenance.pk}/',
                send_email=True
            )
    
    @staticmethod
    def notify_maintenance_completed(maintenance):
        """
        Send notification when maintenance is completed
        """
        if maintenance.reported_by:
            NotificationService.create_notification(
                user=maintenance.reported_by,
                title="Maintenance Completed",
                message=f"Maintenance request '{maintenance.title}' has been completed",
                notification_type='success',
                priority='low',
                related_object=maintenance,
                link=f'/maintenance/{maintenance.pk}/',
                send_email=True
            )
    
    # ===================================================================
    # DOCUMENT NOTIFICATIONS
    # ===================================================================
    
    @staticmethod
    def notify_document_expiring(document, days_until_expiry):
        """
        Send notification when document is expiring soon
        """
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        for staff in staff_users:
            NotificationService.create_notification(
                user=staff,
                title=f"Document Expiring in {days_until_expiry} Days",
                message=f"Document '{document.title}' for property {document.property.code} expires on {document.expiry_date}",
                notification_type='document_expiry',
                priority='high' if days_until_expiry <= 7 else 'medium',
                related_object=document,
                link=f'/properties/{document.property.pk}/',
                send_email=True
            )
    
    # ===================================================================
    # BUDGET NOTIFICATIONS
    # ===================================================================
    
    @staticmethod
    def notify_budget_exceeded(budget):
        """
        Send notification when budget is exceeded
        """
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        for staff in staff_users:
            NotificationService.create_notification(
                user=staff,
                title="⚠️ Budget Exceeded",
                message=f"Budget '{budget.name}' has been exceeded. Spent: {budget.spent_amount}, Budget: {budget.total_amount}",
                notification_type='budget_alert',
                priority='urgent',
                related_object=budget,
                link=f'/financial/budgets/{budget.pk}/',
                send_email=True
            )
    
    @staticmethod
    def notify_budget_threshold(budget, percentage):
        """
        Send notification when budget reaches threshold (e.g., 80%)
        """
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        for staff in staff_users:
            NotificationService.create_notification(
                user=staff,
                title=f"Budget Alert - {percentage}% Used",
                message=f"Budget '{budget.name}' is at {percentage}% utilization",
                notification_type='budget_alert',
                priority='medium',
                related_object=budget,
                link=f'/financial/budgets/{budget.pk}/',
                send_email=False
            )
    
    # ===================================================================
    # SALES NOTIFICATIONS
    # ===================================================================
    
    @staticmethod
    def notify_sales_reservation_expiring(reservation, days_until_expiry):
        """
        Send notification when sales reservation is expiring
        """
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        for staff in staff_users:
            NotificationService.create_notification(
                user=staff,
                title=f"Reservation Expiring in {days_until_expiry} Days",
                message=f"Reservation {reservation.reservation_number} expires on {reservation.expiry_date}",
                notification_type='warning',
                priority='high',
                related_object=reservation,
                link=f'/sales/reservations/{reservation.pk}/',
                action_label='Approve Now',
                action_url=f'/sales/reservations/{reservation.pk}/approve/',
                send_email=True
            )
    
    # ===================================================================
    # UTILITY METHODS
    # ===================================================================
    
    @staticmethod
    def mark_all_as_read(user):
        """
        Mark all notifications as read for a user
        """
        notifications = Notification.objects.filter(user=user, is_read=False)
        count = notifications.count()
        for notification in notifications:
            notification.mark_as_read()
        return count
    
    @staticmethod
    def get_unread_count(user):
        """
        Get count of unread notifications for a user
        """
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @staticmethod
    def get_recent_notifications(user, limit=10):
        """
        Get recent notifications for a user
        """
        return Notification.objects.filter(user=user).order_by('-created_at')[:limit]
