from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from apps.properties.models import Property
from apps.owners.models import Owner
from .buyer import Buyer

User = get_user_model()


class SalesContract(models.Model):
    """
    عقود بيع العقارات - منفصل عن عقود الإيجار
    """
    CONTRACT_STATUS = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('signed', 'Signed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    INSTALLMENT_FREQUENCY = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
    ]
    
    # Basic Information
    contract_number = models.CharField(max_length=50, unique=True)
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='sales_contracts')
    buyer = models.ForeignKey(Buyer, on_delete=models.PROTECT, related_name='purchases')
    seller = models.ForeignKey(Owner, on_delete=models.PROTECT, related_name='sales')
    
    # Price & Payment
    sale_price = models.DecimalField(max_digits=15, decimal_places=2)
    down_payment = models.DecimalField(max_digits=15, decimal_places=2)
    financed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Financing Details
    has_financing = models.BooleanField(default=False)
    financing_institution = models.CharField(max_length=200, blank=True)
    financing_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    financing_years = models.IntegerField(default=0)
    
    # Dates
    contract_date = models.DateField()
    signing_date = models.DateField(null=True, blank=True)
    expected_handover_date = models.DateField()
    actual_handover_date = models.DateField(null=True, blank=True)
    
    # Payment Plan
    has_installments = models.BooleanField(default=False)
    number_of_installments = models.IntegerField(default=0)
    installment_frequency = models.CharField(max_length=20, choices=INSTALLMENT_FREQUENCY, default='monthly')
    
    # Property Condition
    sold_as_is = models.BooleanField(default=False)
    includes_furniture = models.BooleanField(default=False)
    furniture_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Legal & Documents
    title_deed_number = models.CharField(max_length=100, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    notary_name = models.CharField(max_length=200, blank=True)
    lawyer_name = models.CharField(max_length=200, blank=True)
    
    # Terms & Conditions
    terms_and_conditions = models.TextField(blank=True)
    special_conditions = models.TextField(blank=True)
    warranty_terms = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='draft')
    is_registered = models.BooleanField(default=False)
    registration_date = models.DateField(null=True, blank=True)
    
    # Files
    contract_file = models.FileField(upload_to='sales_contracts/', blank=True)
    signed_contract_file = models.FileField(upload_to='sales_contracts/signed/', blank=True)
    
    # Agent Commission
    has_agent = models.BooleanField(default=False)
    agent_name = models.CharField(max_length=200, blank=True)
    agent_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    agent_commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Staff
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_contracts_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_contracts_approved')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Contract'
        verbose_name_plural = 'Sales Contracts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contract_number']),
            models.Index(fields=['status']),
            models.Index(fields=['contract_date']),
        ]
    
    def __str__(self):
        return f"{self.contract_number} - {self.property.code}"
    
    def get_total_paid(self):
        """إجمالي المبلغ المدفوع"""
        total = self.payments.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total']
        return total or Decimal('0.00')
    
    def get_remaining_amount(self):
        """المبلغ المتبقي"""
        return self.sale_price - self.get_total_paid()
    
    def get_payment_progress_percentage(self):
        """نسبة إتمام الدفع"""
        if self.sale_price > 0:
            return float((self.get_total_paid() / self.sale_price) * 100)
        return 0
    
    def is_fully_paid(self):
        """هل تم دفع المبلغ بالكامل"""
        return self.get_remaining_amount() <= 0
    
    def save(self, *args, **kwargs):
        if not self.contract_number:
            # توليد رقم عقد تلقائي
            from django.utils.crypto import get_random_string
            self.contract_number = f"SC-{timezone.now().strftime('%Y%m%d')}-{get_random_string(6, '0123456789')}"
        super().save(*args, **kwargs)


class SalesPaymentPlan(models.Model):
    """
    خطة الدفع بالتقسيط لعقود البيع
    """
    sales_contract = models.ForeignKey(SalesContract, on_delete=models.CASCADE, related_name='payment_plans')
    
    # Installment Details
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Late Payment
    is_overdue = models.BooleanField(default=False)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Payment Plan'
        verbose_name_plural = 'Sales Payment Plans'
        ordering = ['due_date', 'installment_number']
        unique_together = ['sales_contract', 'installment_number']
        indexes = [
            models.Index(fields=['due_date', 'is_paid']),
        ]
    
    def __str__(self):
        return f"{self.sales_contract.contract_number} - Installment #{self.installment_number}"
    
    def check_overdue(self):
        """تحقق من تأخر الدفع"""
        if not self.is_paid and timezone.now().date() > self.due_date:
            self.is_overdue = True
            self.save()
            return True
        return False
    
    def mark_as_paid(self, payment_reference):
        """تمييز القسط كمدفوع"""
        self.is_paid = True
        self.payment_date = timezone.now().date()
        self.payment_reference = payment_reference
        self.save()


class SalesPayment(models.Model):
    """
    مدفوعات عقود البيع
    """
    PAYMENT_TYPES = [
        ('down_payment', 'Down Payment'),
        ('installment', 'Installment'),
        ('final_payment', 'Final Payment'),
        ('late_fee', 'Late Fee'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('mortgage', 'Mortgage Payment'),
        ('online', 'Online Payment'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # References
    sales_contract = models.ForeignKey(SalesContract, on_delete=models.PROTECT, related_name='payments')
    payment_plan = models.ForeignKey(SalesPaymentPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    
    # References
    reference_number = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=200, blank=True)
    check_number = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Receipt
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_file = models.FileField(upload_to='sales_payments/receipts/', blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Staff
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_payments_received')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Payment'
        verbose_name_plural = 'Sales Payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['payment_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # توليد رقم إيصال تلقائي
            from django.utils.crypto import get_random_string
            self.receipt_number = f"RCP-{timezone.now().strftime('%Y%m%d')}-{get_random_string(8, '0123456789')}"
        super().save(*args, **kwargs)
