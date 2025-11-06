"""
Maintenance models for Origin App Real Estate Management System.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.properties.models import Property


class MaintenanceCategory(models.Model):
    """
    Maintenance request categories.
    """
    name = models.CharField(_('Category Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Maintenance Category')
        verbose_name_plural = _('Maintenance Categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class MaintenanceRequest(models.Model):
    """
    Maintenance request model.
    """
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    # Basic Information
    request_number = models.CharField(
        _('Request Number'),
        max_length=50,
        unique=True
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
        verbose_name=_('Property')
    )
    category = models.ForeignKey(
        MaintenanceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests',
        verbose_name=_('Category')
    )
    
    # Request Details
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    priority = models.CharField(
        _('Priority'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance',
        verbose_name=_('Assigned To')
    )
    
    # Dates
    request_date = models.DateTimeField(_('Request Date'), auto_now_add=True)
    scheduled_date = models.DateTimeField(
        _('Scheduled Date'),
        null=True,
        blank=True
    )
    completed_date = models.DateTimeField(
        _('Completed Date'),
        null=True,
        blank=True
    )
    
    # Cost
    estimated_cost = models.DecimalField(
        _('Estimated Cost'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_cost = models.DecimalField(
        _('Actual Cost'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Additional Information
    notes = models.TextField(_('Notes'), blank=True)
    resolution_notes = models.TextField(_('Resolution Notes'), blank=True)
    
    # Reported By
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_maintenance',
        verbose_name=_('Reported By')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Maintenance Request')
        verbose_name_plural = _('Maintenance Requests')
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['request_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['request_date']),
        ]

    def __str__(self):
        return f"{self.request_number} - {self.title}"

    def is_overdue(self):
        """Check if request is overdue."""
        if self.scheduled_date and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return timezone.now() > self.scheduled_date
        return False

    def get_duration(self):
        """Get duration from request to completion."""
        if self.completed_date:
            return self.completed_date - self.request_date
        return None

    def mark_completed(self, actual_cost=None, resolution_notes=''):
        """Mark request as completed."""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_date = timezone.now()
        if actual_cost:
            self.actual_cost = actual_cost
        if resolution_notes:
            self.resolution_notes = resolution_notes
        self.save()


class MaintenanceAttachment(models.Model):
    """
    Attachments for maintenance requests.
    """
    ATTACHMENT_TYPES = [
        ('image', _('Image')),
        ('document', _('Document')),
        ('invoice', _('Invoice')),
        ('report', _('Report')),
    ]

    maintenance_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('Maintenance Request')
    )
    file = models.FileField(
        _('File'),
        upload_to='maintenance/attachments/%Y/%m/'
    )
    attachment_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=ATTACHMENT_TYPES,
        default='image'
    )
    description = models.CharField(_('Description'), max_length=200, blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Uploaded By')
    )
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Maintenance Attachment')
        verbose_name_plural = _('Maintenance Attachments')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.maintenance_request.request_number} - {self.attachment_type}"


class MaintenanceSchedule(models.Model):
    """
    Scheduled preventive maintenance.
    """
    FREQUENCY_CHOICES = [
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('semi_annual', _('Semi-Annual')),
        ('annual', _('Annual')),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='maintenance_schedules',
        verbose_name=_('Property')
    )
    category = models.ForeignKey(
        MaintenanceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='schedules',
        verbose_name=_('Category')
    )
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    frequency = models.CharField(
        _('Frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES
    )
    last_service_date = models.DateField(
        _('Last Service Date'),
        null=True,
        blank=True
    )
    next_service_date = models.DateField(_('Next Service Date'))
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Assigned To')
    )
    estimated_cost = models.DecimalField(
        _('Estimated Cost'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    is_active = models.BooleanField(_('Active'), default=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Maintenance Schedule')
        verbose_name_plural = _('Maintenance Schedules')
        ordering = ['next_service_date']

    def __str__(self):
        return f"{self.property.code} - {self.title}"

    def is_due(self):
        """Check if maintenance is due."""
        from django.utils import timezone
        return self.next_service_date <= timezone.now().date()

    def update_next_service_date(self):
        """Update next service date based on frequency."""
        from dateutil.relativedelta import relativedelta
        
        if not self.last_service_date:
            return
        
        frequency_map = {
            'weekly': {'weeks': 1},
            'monthly': {'months': 1},
            'quarterly': {'months': 3},
            'semi_annual': {'months': 6},
            'annual': {'years': 1},
        }
        
        delta = frequency_map.get(self.frequency, {'months': 1})
        self.next_service_date = self.last_service_date + relativedelta(**delta)
        self.save()
