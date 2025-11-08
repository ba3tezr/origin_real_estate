from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Buyer(models.Model):
    """
    نموذج المشترين - يختلف عن المستأجرين
    """
    BUYER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('investor', 'Investor'),
    ]
    
    # Personal Information
    buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=17)
    email = models.EmailField()
    national_id = models.CharField(max_length=50, unique=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Egypt')
    
    # Company Info (إذا كان شركة)
    company_name = models.CharField(max_length=200, blank=True)
    company_registration = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Financial Information
    annual_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_score = models.IntegerField(default=0)
    financing_approved = models.BooleanField(default=False)
    financing_institution = models.CharField(max_length=200, blank=True)
    approved_loan_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Identification Documents
    id_document = models.FileField(upload_to='buyers/documents/', blank=True)
    income_proof = models.FileField(upload_to='buyers/documents/', blank=True)
    
    # Agent/Representative
    has_agent = models.BooleanField(default=False)
    agent_name = models.CharField(max_length=200, blank=True)
    agent_phone = models.CharField(max_length=17, blank=True)
    agent_license = models.CharField(max_length=100, blank=True)
    
    # Status
    is_qualified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Buyer'
        verbose_name_plural = 'Buyers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['national_id']),
            models.Index(fields=['email']),
            models.Index(fields=['is_qualified', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_buyer_type_display()}"
    
    def get_purchasing_power(self):
        """حساب القدرة الشرائية"""
        return self.annual_income * Decimal('3.5') + self.approved_loan_amount
    
    def qualify_buyer(self):
        """تأهيل المشتري بناءً على المعايير"""
        if self.credit_score >= 650 and self.annual_income > 0:
            self.is_qualified = True
            self.save()
            return True
        return False
