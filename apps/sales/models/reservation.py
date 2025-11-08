from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.properties.models import Property
from .buyer import Buyer
import builtins

User = get_user_model()


class PropertyReservation(models.Model):
    """
    حجز العقار قبل إتمام عملية البيع
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('converted', 'Converted to Sale'),
    ]
    
    # Basic Information
    reservation_number = models.CharField(max_length=50, unique=True)
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='sales_reservations')
    buyer = models.ForeignKey(Buyer, on_delete=models.PROTECT, related_name='reservations')
    
    # Dates
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()
    
    # Financial
    reservation_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
    ])
    payment_reference = models.CharField(max_length=100)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Notes
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Staff
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reservations_made')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Property Reservation'
        verbose_name_plural = 'Property Reservations'
        ordering = ['-reservation_date']
        indexes = [
            models.Index(fields=['reservation_number']),
            models.Index(fields=['status', 'expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.reservation_number} - {self.property.code}"
    
    @builtins.property
    def is_expired(self):
        """تحقق من انتهاء صلاحية الحجز"""
        from django.utils import timezone
        return timezone.now().date() > self.expiry_date
    
    def convert_to_sale(self):
        """تحويل الحجز إلى عقد بيع"""
        if self.status == 'approved':
            self.status = 'converted'
            self.save()
            return True
        return False
    
    def cancel_reservation(self, reason):
        """إلغاء الحجز"""
        self.status = 'cancelled'
        self.cancellation_reason = reason
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.reservation_number:
            # توليد رقم حجز تلقائي
            from django.utils.crypto import get_random_string
            self.reservation_number = f"RSV-{timezone.now().strftime('%Y%m%d')}-{get_random_string(6, '0123456789')}"
        super().save(*args, **kwargs)
