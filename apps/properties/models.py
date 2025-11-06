"""
Property models for Origin App Real Estate Management System.
"""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.owners.models import Owner


class PropertyType(models.Model):
    """
    Property type categorization.
    """
    name = models.CharField(_('Type Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Property Type')
        verbose_name_plural = _('Property Types')
        ordering = ['name']

    def __str__(self):
        return self.name


class Property(models.Model):
    """
    Property model for real estate management.
    """
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('rented', _('Rented')),
        ('maintenance', _('Under Maintenance')),
        ('sold', _('Sold')),
    ]

    # Basic Information
    title = models.CharField(_('Property Title'), max_length=200)
    code = models.CharField(
        _('Property Code'),
        max_length=50,
        unique=True,
        help_text=_('Unique identifier for property')
    )
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.PROTECT,
        related_name='properties',
        verbose_name=_('Property Type')
    )
    owner = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        related_name='properties',
        verbose_name=_('Owner')
    )
    
    # Location
    address = models.TextField(_('Address'))
    city = models.CharField(_('City'), max_length=100)
    district = models.CharField(_('District'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    latitude = models.DecimalField(
        _('Latitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        _('Longitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    virtual_tour_url = models.URLField(_('Virtual Tour URL'), blank=True)
    video_url = models.URLField(_('Video URL'), blank=True)
    
    # Property Details
    area_sqm = models.DecimalField(
        _('Area (m²)'),
        max_digits=10,
        decimal_places=2
    )
    bedrooms = models.IntegerField(_('Bedrooms'), default=0)
    bathrooms = models.IntegerField(_('Bathrooms'), default=0)
    floors = models.IntegerField(_('Floors'), default=1)
    parking_spaces = models.IntegerField(_('Parking Spaces'), default=0)
    year_built = models.IntegerField(_('Year Built'), null=True, blank=True)
    floor_number = models.IntegerField(_('Floor Number'), null=True, blank=True)
    total_floors = models.IntegerField(_('Total Floors'), null=True, blank=True)
    
    # Pricing
    purchase_price = models.DecimalField(
        _('Purchase Price'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    market_value = models.DecimalField(
        _('Market Value'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    rental_price_monthly = models.DecimalField(
        _('Monthly Rental Price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Features
    has_elevator = models.BooleanField(_('Has Elevator'), default=False)
    has_garden = models.BooleanField(_('Has Garden'), default=False)
    has_pool = models.BooleanField(_('Has Swimming Pool'), default=False)
    has_security = models.BooleanField(_('Has Security'), default=False)
    is_furnished = models.BooleanField(_('Furnished'), default=False)
    pets_allowed = models.BooleanField(_('Pets Allowed'), default=False)
    energy_rating = models.CharField(_('Energy Rating'), max_length=10, blank=True)
    
    # Additional Information
    description = models.TextField(_('Description'), blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    last_renovation_date = models.DateField(_('Last Renovation Date'), null=True, blank=True)
    occupancy_rate = models.DecimalField(
        _('Occupancy Rate'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Occupancy percentage (0-100)')
    )
    average_roi = models.DecimalField(
        _('Average ROI'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Average return on investment percentage')
    )
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Property')
        verbose_name_plural = _('Properties')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['city']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def get_active_contract(self):
        """Get active contract for this property."""
        return self.contracts.filter(status='active').first()

    def is_available(self):
        """Check if property is available for rent."""
        return self.status == 'available' and self.is_active

    def get_maintenance_requests_count(self):
        """Get number of maintenance requests."""
        return self.maintenance_requests.count()

    def get_pending_maintenance_count(self):
        """Get number of pending maintenance requests."""
        return self.maintenance_requests.filter(status='pending').count()

    def get_absolute_url(self):
        return reverse('properties:detail', args=[self.pk])


class PropertyDocument(models.Model):
    """
    Documents related to properties.
    """
    DOCUMENT_TYPES = [
        ('deed', _('Property Deed')),
        ('contract', _('Contract')),
        ('insurance', _('Insurance')),
        ('inspection', _('Inspection Report')),
        ('permit', _('Permit')),
        ('other', _('Other')),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Property')
    )
    document_type = models.CharField(
        _('Document Type'),
        max_length=20,
        choices=DOCUMENT_TYPES
    )
    title = models.CharField(_('Title'), max_length=200)
    file = models.FileField(
        _('File'),
        upload_to='properties/documents/%Y/%m/'
    )
    description = models.TextField(_('Description'), blank=True)
    expiry_date = models.DateField(_('Expiry Date'), null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='property_documents',
        verbose_name=_('Uploaded By')
    )
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Document')
        verbose_name_plural = _('Property Documents')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.property.code} - {self.title}"

    def is_expired(self):
        """Check if document is expired."""
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False


class PropertyImage(models.Model):
    """
    Images for properties.
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Property')
    )
    image = models.ImageField(
        _('Image'),
        upload_to='properties/images/%Y/%m/'
    )
    title = models.CharField(_('Title'), max_length=200, blank=True)
    caption = models.CharField(_('Caption'), max_length=200, blank=True)
    description = models.TextField(_('Description'), blank=True)
    is_primary = models.BooleanField(_('Primary Image'), default=False)
    order = models.IntegerField(_('Order'), default=0)
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Image')
        verbose_name_plural = _('Property Images')
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return f"{self.property.code} - Image {self.order}"

    def save(self, *args, **kwargs):
        """Ensure only one primary image per property."""
        if self.is_primary:
            PropertyImage.objects.filter(
                property=self.property,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class PropertyValuation(models.Model):
    """Valuation records for properties."""
    VALUATION_TYPES = [
        ('market', _('Market Valuation')),
        ('bank', _('Bank Valuation')),
        ('insurance', _('Insurance Valuation')),
        ('other', _('Other')),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='valuations',
        verbose_name=_('Property')
    )
    valuation_date = models.DateField(_('Valuation Date'))
    valuation_amount = models.DecimalField(
        _('Valuation Amount'),
        max_digits=12,
        decimal_places=2
    )
    valuation_type = models.CharField(
        _('Valuation Type'),
        max_length=20,
        choices=VALUATION_TYPES,
        default='market'
    )
    valuator_name = models.CharField(_('Valuator Name'), max_length=200, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    document = models.FileField(
        _('Valuation Document'),
        upload_to='properties/valuations/%Y/%m/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Valuation')
        verbose_name_plural = _('Property Valuations')
        ordering = ['-valuation_date']

    def __str__(self):
        return f"{self.property.code} - {self.valuation_date}"


class PropertyAmenity(models.Model):
    """Amenities associated with properties."""
    AMENITY_TYPES = [
        ('indoor', _('Indoor')),
        ('outdoor', _('Outdoor')),
        ('security', _('Security')),
        ('technology', _('Technology')),
        ('other', _('Other')),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='amenities',
        verbose_name=_('Property')
    )
    amenity_type = models.CharField(
        _('Amenity Type'),
        max_length=20,
        choices=AMENITY_TYPES,
        default='other'
    )
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    is_available = models.BooleanField(_('Available'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Amenity')
        verbose_name_plural = _('Property Amenities')
        ordering = ['amenity_type', 'name']

    def __str__(self):
        return f"{self.property.code} - {self.name}"


class PropertyInspection(models.Model):
    """Inspection records for properties."""
    INSPECTION_TYPES = [
        ('routine', _('Routine')),
        ('safety', _('Safety')),
        ('pre_purchase', _('Pre-purchase')),
        ('maintenance', _('Maintenance')),
        ('other', _('Other')),
    ]

    CONDITION_CHOICES = [
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('fair', _('Fair')),
        ('poor', _('Poor')),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='inspections',
        verbose_name=_('Property')
    )
    inspection_date = models.DateField(_('Inspection Date'))
    inspector_name = models.CharField(_('Inspector Name'), max_length=200)
    inspection_type = models.CharField(
        _('Inspection Type'),
        max_length=20,
        choices=INSPECTION_TYPES,
        default='routine'
    )
    overall_condition = models.CharField(
        _('Overall Condition'),
        max_length=20,
        choices=CONDITION_CHOICES,
        default='good'
    )
    notes = models.TextField(_('Notes'))
    recommendations = models.TextField(_('Recommendations'), blank=True)
    next_inspection_date = models.DateField(_('Next Inspection Date'), null=True, blank=True)
    document = models.FileField(
        _('Inspection Report'),
        upload_to='properties/inspections/%Y/%m/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Inspection')
        verbose_name_plural = _('Property Inspections')
        ordering = ['-inspection_date']

    def __str__(self):
        return f"{self.property.code} - {self.inspection_date}"


class PropertyExpense(models.Model):
    """Expense records for properties."""
    EXPENSE_TYPES = [
        ('maintenance', _('Maintenance')),
        ('utilities', _('Utilities')),
        ('tax', _('Tax')),
        ('insurance', _('Insurance')),
        ('management', _('Management')),
        ('other', _('Other')),
    ]

    FREQUENCY_CHOICES = [
        ('once', _('One-time')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('annual', _('Annual')),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='expenses',
        verbose_name=_('Property')
    )
    expense_date = models.DateField(_('Expense Date'))
    expense_type = models.CharField(
        _('Expense Type'),
        max_length=20,
        choices=EXPENSE_TYPES,
        default='other'
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2
    )
    vendor = models.CharField(_('Vendor'), max_length=200, blank=True)
    description = models.TextField(_('Description'), blank=True)
    receipt = models.FileField(
        _('Receipt'),
        upload_to='properties/expenses/%Y/%m/',
        null=True,
        blank=True
    )
    is_recurring = models.BooleanField(_('Recurring'), default=False)
    recurrence_frequency = models.CharField(
        _('Recurrence Frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='once'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Expense')
        verbose_name_plural = _('Property Expenses')
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.property.code} - {self.expense_type}"


class PropertyRevenue(models.Model):
    """Revenue records for properties."""
    REVENUE_TYPES = [
        ('rent', _('Rent')),
        ('service', _('Service Charge')),
        ('parking', _('Parking')),
        ('other', _('Other')),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='revenues',
        verbose_name=_('Property')
    )
    revenue_date = models.DateField(_('Revenue Date'))
    revenue_type = models.CharField(
        _('Revenue Type'),
        max_length=20,
        choices=REVENUE_TYPES,
        default='rent'
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2
    )
    source = models.CharField(_('Source'), max_length=200, blank=True)
    description = models.TextField(_('Description'), blank=True)
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='property_revenues',
        verbose_name=_('Contract')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Property Revenue')
        verbose_name_plural = _('Property Revenues')
        ordering = ['-revenue_date']

    def __str__(self):
        return f"{self.property.code} - {self.revenue_type}"
