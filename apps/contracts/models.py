"""
Contract models for Origin App Real Estate Management System.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.properties.models import Property
from apps.clients.models import Client

class Contract(models.Model):
    """
    Rental contract model.
    """
    CONTRACT_TYPES = [
        ('residential', _('Residential')),
        ('commercial', _('Commercial')),
        ('industrial', _('Industrial')),
    ]

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('terminated', _('Terminated')),
        ('renewed', _('Renewed')),
    ]

    PAYMENT_FREQUENCY = [
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('semi_annual', _('Semi-Annual')),
        ('annual', _('Annual')),
    ]

    # Basic Information
    contract_number = models.CharField(
        _('Contract Number'),
        max_length=50,
        unique=True
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name=_('Property')
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name=_('Client/Tenant')
    )
    contract_type = models.CharField(
        _('Contract Type'),
        max_length=20,
        choices=CONTRACT_TYPES,
        default='residential'
    )
    
    # Dates
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    signed_date = models.DateField(_('Signed Date'), null=True, blank=True)
    
    # Financial Terms
    rent_amount = models.DecimalField(
        _('Rent Amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    security_deposit = models.DecimalField(
        _('Security Deposit'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    payment_frequency = models.CharField(
        _('Payment Frequency'),
        max_length=20,
        choices=PAYMENT_FREQUENCY,
        default='monthly'
    )
    payment_day = models.IntegerField(
        _('Payment Day of Month'),
        default=1,
        help_text=_('Day of the month when rent is due')
    )
    
    # Additional Charges
    maintenance_fee = models.DecimalField(
        _('Maintenance Fee'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    utility_charges = models.DecimalField(
        _('Utility Charges'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Terms and Conditions
    terms_and_conditions = models.TextField(
        _('Terms and Conditions'),
        blank=True
    )
    special_conditions = models.TextField(
        _('Special Conditions'),
        blank=True
    )
    
    # Auto-renewal
    auto_renew = models.BooleanField(_('Auto Renew'), default=False)
    renewal_notice_days = models.IntegerField(
        _('Renewal Notice Days'),
        default=30,
        help_text=_('Days before end date to send renewal notice')
    )
    
    # Status and Notes
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    notes = models.TextField(_('Notes'), blank=True)
    
    # File Attachments
    contract_file = models.FileField(
        _('Contract File'),
        upload_to='contracts/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Contract')
        verbose_name_plural = _('Contracts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contract_number']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.property.code}"

    def get_total_amount(self):
        """Calculate total amount including all charges."""
        return (
            self.rent_amount +
            self.maintenance_fee +
            self.utility_charges
        )

    def get_duration_months(self):
        """Calculate contract duration in months."""
        from dateutil.relativedelta import relativedelta
        delta = relativedelta(self.end_date, self.start_date)
        return delta.years * 12 + delta.months

    def is_active(self):
        """Check if contract is currently active."""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'active' and
            self.start_date <= today <= self.end_date
        )

    def days_until_expiry(self):
        """Get number of days until contract expires."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date > today:
            return (self.end_date - today).days
        return 0

    def get_payment_history(self):
        """Get all payments for this contract."""
        return self.payments.all().order_by('-payment_date')

    def get_total_paid(self):
        """Get total amount paid for this contract."""
        return self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def get_outstanding_balance(self):
        """Calculate outstanding balance."""
        total_due = self.get_total_amount() * self.get_duration_months()
        total_paid = self.get_total_paid()
        return total_due - total_paid

class ContractPayment(models.Model):
    """
    Payment records for contracts.
    """
    PAYMENT_METHODS = [
        ('cash', _('Cash')),
        ('bank_transfer', _('Bank Transfer')),
        ('check', _('Check')),
        ('credit_card', _('Credit Card')),
        ('online', _('Online Payment')),
    ]

    PAYMENT_STATUS = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Contract')
    )
    payment_date = models.DateField(_('Payment Date'))
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash'
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=PAYMENT_STATUS,
        default='completed'
    )
    reference_number = models.CharField(
        _('Reference Number'),
        max_length=100,
        blank=True
    )
    notes = models.TextField(_('Notes'), blank=True)
    receipt_file = models.FileField(
        _('Receipt File'),
        upload_to='payments/receipts/%Y/%m/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Contract Payment')
        verbose_name_plural = _('Contract Payments')
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.contract.contract_number} - {self.amount} on {self.payment_date}"

class ContractRenewal(models.Model):
    """
    Contract renewal history.
    """
    original_contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='renewals',
        verbose_name=_('Original Contract')
    )
    new_contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='renewed_from',
        verbose_name=_('New Contract')
    )
    renewal_date = models.DateField(_('Renewal Date'))
    rent_increase = models.DecimalField(
        _('Rent Increase'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Amount of rent increase')
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Contract Renewal')
        verbose_name_plural = _('Contract Renewals')
        ordering = ['-renewal_date']

    def __str__(self):
        return f"Renewal: {self.original_contract.contract_number}"
