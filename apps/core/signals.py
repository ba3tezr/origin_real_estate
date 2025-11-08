"""
Signal handlers for automatic notifications
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

# Import models (will be imported when needed to avoid circular imports)


# ===================================================================
# CONTRACT SIGNALS
# ===================================================================

@receiver(post_save, sender='contracts.Contract')
def contract_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when new contract is created
    """
    if created:
        from .services import NotificationService
        NotificationService.notify_contract_created(instance)


# ===================================================================
# MAINTENANCE SIGNALS
# ===================================================================

@receiver(post_save, sender='maintenance.MaintenanceRequest')
def maintenance_request_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when new maintenance request is created
    """
    if created:
        from .services import NotificationService
        NotificationService.notify_maintenance_request_created(instance)


@receiver(post_save, sender='maintenance.MaintenanceRequest')
def maintenance_completed_notification(sender, instance, created, **kwargs):
    """
    Send notification when maintenance is completed
    """
    if not created and instance.status == 'completed':
        # Check if status was just changed to completed
        if instance.completed_date and not hasattr(instance, '_notified_completed'):
            from .services import NotificationService
            NotificationService.notify_maintenance_completed(instance)
            instance._notified_completed = True


# ===================================================================
# PAYMENT SIGNALS
# ===================================================================

@receiver(post_save, sender='contracts.ContractPayment')
def payment_received_notification(sender, instance, created, **kwargs):
    """
    Send notification when payment is received
    """
    if created and instance.status == 'completed':
        from .services import NotificationService
        NotificationService.notify_payment_received(instance, instance.contract)


# ===================================================================
# SALES SIGNALS
# ===================================================================

@receiver(post_save, sender='sales.SalesPayment')
def sales_payment_received_notification(sender, instance, created, **kwargs):
    """
    Send notification when sales payment is received
    """
    if created and instance.status == 'completed':
        from .services import NotificationService
        from django.contrib.auth.models import User
        
        # Notify staff about new payment
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        for staff in staff_users:
            NotificationService.create_notification(
                user=staff,
                title="Sales Payment Received",
                message=f"Payment of EGP {instance.amount} received for contract {instance.sales_contract.contract_number}",
                notification_type='success',
                priority='low',
                related_object=instance,
                link=f'/sales/contracts/{instance.sales_contract.pk}/',
                send_email=False
            )


# ===================================================================
# BUDGET SIGNALS
# ===================================================================

@receiver(post_save, sender='financial.Budget')
def budget_threshold_notification(sender, instance, created, **kwargs):
    """
    Send notification when budget reaches threshold
    """
    if not created:
        utilization = instance.get_utilization_percentage()
        
        # Check if budget exceeded
        if instance.is_over_budget() and not hasattr(instance, '_notified_exceeded'):
            from .services import NotificationService
            NotificationService.notify_budget_exceeded(instance)
            instance._notified_exceeded = True
        
        # Check if reached 80% threshold
        elif utilization >= 80 and utilization < 100 and not hasattr(instance, '_notified_80'):
            from .services import NotificationService
            NotificationService.notify_budget_threshold(instance, int(utilization))
            instance._notified_80 = True
