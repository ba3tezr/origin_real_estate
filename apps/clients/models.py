"""
Client models for Origin App Real Estate Management System.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class Client(models.Model):
    """
    Client/Tenant model.
    """
    # Personal Information
    name = models.CharField(_('Full Name'), max_length=200)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in format: '+999999999'.")
    )
    phone = models.CharField(
        _('Phone Number'),
        validators=[phone_regex],
        max_length=17
    )
    email = models.EmailField(_('Email'), blank=True)
    national_id = models.CharField(
        _('National ID'),
        max_length=50,
        unique=True
    )
    
    # Address Information
    address = models.TextField(_('Address'))
    city = models.CharField(_('City'), max_length=100, blank=True)
    country = models.CharField(_('Country'), max_length=100, default='Egypt')
    
    # Employment Information
    employer = models.CharField(_('Employer'), max_length=200, blank=True)
    occupation = models.CharField(_('Occupation'), max_length=100, blank=True)
    monthly_income = models.DecimalField(
        _('Monthly Income'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(
        _('Emergency Contact Name'),
        max_length=200,
        blank=True
    )
    emergency_contact_phone = models.CharField(
        _('Emergency Contact Phone'),
        max_length=17,
        blank=True
    )
    
    # Additional Information
    notes = models.TextField(_('Notes'), blank=True)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    credit_score = models.IntegerField(
        _('Credit Score'),
        null=True,
        blank=True,
        help_text=_('Credit score from 0 to 100')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['national_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_active_contracts_count(self):
        """Get number of active contracts."""
        return self.contracts.filter(status='active').count()

    def get_total_rent_payments(self):
        """Get total rent amount for all active contracts."""
        active_contracts = self.contracts.filter(status='active')
        return sum(c.rent_amount for c in active_contracts)

    def has_active_contract(self):
        """Check if client has any active contract."""
        return self.contracts.filter(status='active').exists()
