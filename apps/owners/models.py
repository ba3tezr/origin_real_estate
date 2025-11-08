"""
Owner models for Origin App Real Estate Management System.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class Owner(models.Model):
    """
    Property owner model.
    """
    # Personal Information
    name = models.CharField(_('Full Name'), max_length=200)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone = models.CharField(_('Phone Number'), validators=[phone_regex], max_length=17)
    email = models.EmailField(_('Email'), blank=True)
    national_id = models.CharField(_('National ID'), max_length=50, unique=True)
    
    # Address Information
    address = models.TextField(_('Address'), blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    country = models.CharField(_('Country'), max_length=100, default='Egypt')
    
    # Additional Information
    mobile = models.CharField(_('Mobile'), validators=[phone_regex], max_length=17, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    tax_id = models.CharField(_('Tax ID'), max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Owner')
        verbose_name_plural = _('Owners')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['national_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_properties_count(self):
        """Get total number of properties owned."""
        return self.properties.count()

    def get_active_properties_count(self):
        """Get number of active properties."""
        return self.properties.filter(is_active=True).count()

    def get_total_contracts_value(self):
        """Get total value of all contracts for this owner's properties."""
        from apps.contracts.models import Contract
        total = 0
        for property in self.properties.all():
            contracts = Contract.objects.filter(property=property, status='active')
            total += sum(c.rent_amount for c in contracts)
        return total
