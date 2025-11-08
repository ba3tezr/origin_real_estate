"""
Financial models for Origin App Real Estate Management System.
Implementing complete accounting system with Chart of Accounts.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.properties.models import Property
from apps.contracts.models import Contract


class AccountType(models.TextChoices):
    """Account types for Chart of Accounts"""
    ASSET = 'asset', _('Asset')
    LIABILITY = 'liability', _('Liability')
    EQUITY = 'equity', _('Equity')
    REVENUE = 'revenue', _('Revenue')
    EXPENSE = 'expense', _('Expense')


class Account(models.Model):
    """
    Chart of Accounts - شجرة الحسابات
    """
    code = models.CharField(
        _('Account Code'),
        max_length=20,
        unique=True,
        help_text=_('Unique account code (e.g., 1000, 2000)')
    )
    name = models.CharField(_('Account Name'), max_length=200)
    name_ar = models.CharField(_('Account Name (Arabic)'), max_length=200, blank=True)
    account_type = models.CharField(
        _('Account Type'),
        max_length=20,
        choices=AccountType.choices
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent Account')
    )
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    is_system = models.BooleanField(
        _('System Account'),
        default=False,
        help_text=_('System accounts cannot be deleted')
    )
    
    # Opening Balance
    opening_balance = models.DecimalField(
        _('Opening Balance'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    opening_balance_type = models.CharField(
        _('Opening Balance Type'),
        max_length=10,
        choices=[('debit', _('Debit')), ('credit', _('Credit'))],
        default='debit'
    )
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Chart of Accounts')
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['account_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_balance(self):
        """Calculate current account balance"""
        from django.db.models import Sum, Q
        
        # Get all journal entry lines for this account
        lines = JournalEntryLine.objects.filter(
            account=self,
            journal_entry__is_posted=True
        )
        
        debits = lines.aggregate(total=Sum('debit_amount'))['total'] or 0
        credits = lines.aggregate(total=Sum('credit_amount'))['total'] or 0
        
        if self.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
            return Decimal(debits) - Decimal(credits)
        else:  # LIABILITY, EQUITY, REVENUE
            return Decimal(credits) - Decimal(debits)
    
    def get_full_path(self):
        """Get full account path (e.g., Assets > Current Assets > Cash)"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class FinancialPeriod(models.Model):
    """
    Financial periods for reporting
    """
    name = models.CharField(_('Period Name'), max_length=100)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    is_closed = models.BooleanField(_('Closed'), default=False)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Financial Period')
        verbose_name_plural = _('Financial Periods')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


class JournalEntry(models.Model):
    """
    Journal Entry - القيد اليومي
    """
    ENTRY_TYPES = [
        ('manual', _('Manual Entry')),
        ('automated', _('Automated Entry')),
        ('adjustment', _('Adjustment Entry')),
        ('opening', _('Opening Entry')),
        ('closing', _('Closing Entry')),
    ]
    
    entry_number = models.CharField(
        _('Entry Number'),
        max_length=50,
        unique=True
    )
    entry_date = models.DateField(_('Entry Date'))
    entry_type = models.CharField(
        _('Entry Type'),
        max_length=20,
        choices=ENTRY_TYPES,
        default='manual'
    )
    period = models.ForeignKey(
        FinancialPeriod,
        on_delete=models.PROTECT,
        related_name='journal_entries',
        verbose_name=_('Financial Period'),
        null=True,
        blank=True
    )
    reference = models.CharField(
        _('Reference'),
        max_length=100,
        blank=True,
        help_text=_('External reference number')
    )
    description = models.TextField(_('Description'))
    
    # Related entities
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries',
        verbose_name=_('Related Property')
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries',
        verbose_name=_('Related Contract')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='journal_entries',
        verbose_name=_('Created By')
    )
    is_posted = models.BooleanField(_('Posted'), default=False)
    posted_at = models.DateTimeField(_('Posted At'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Journal Entry')
        verbose_name_plural = _('Journal Entries')
        ordering = ['-entry_date', '-entry_number']
    
    def __str__(self):
        return f"{self.entry_number} - {self.entry_date}"
    
    def get_total_debit(self):
        return self.lines.aggregate(total=models.Sum('debit_amount'))['total'] or 0
    
    def get_total_credit(self):
        return self.lines.aggregate(total=models.Sum('credit_amount'))['total'] or 0
    
    def is_balanced(self):
        return self.get_total_debit() == self.get_total_credit()
    
    def post(self):
        """Post the journal entry"""
        if self.is_balanced() and not self.is_posted:
            from django.utils import timezone
            self.is_posted = True
            self.posted_at = timezone.now()
            self.save()
            return True
        return False


class JournalEntryLine(models.Model):
    """
    Journal Entry Line - سطر القيد
    """
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('Journal Entry')
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        verbose_name=_('Account')
    )
    debit_amount = models.DecimalField(
        _('Debit Amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    credit_amount = models.DecimalField(
        _('Credit Amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    description = models.CharField(_('Description'), max_length=500, blank=True)
    
    class Meta:
        verbose_name = _('Journal Entry Line')
        verbose_name_plural = _('Journal Entry Lines')
    
    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.name}"


class Invoice(models.Model):
    """
    Invoice - الفواتير
    """
    INVOICE_TYPES = [
        ('sales', _('Sales Invoice')),
        ('purchase', _('Purchase Invoice')),
        ('rent', _('Rent Invoice')),
        ('service', _('Service Invoice')),
    ]
    
    INVOICE_STATUS = [
        ('draft', _('Draft')),
        ('issued', _('Issued')),
        ('paid', _('Paid')),
        ('partial', _('Partially Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]
    
    invoice_number = models.CharField(
        _('Invoice Number'),
        max_length=50,
        unique=True
    )
    invoice_type = models.CharField(
        _('Invoice Type'),
        max_length=20,
        choices=INVOICE_TYPES
    )
    invoice_date = models.DateField(_('Invoice Date'))
    due_date = models.DateField(_('Due Date'))
    
    # Related entities
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Property')
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Contract')
    )
    
    # Amounts
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        _('Tax Amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        _('Discount Amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        _('Total Amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    paid_amount = models.DecimalField(
        _('Paid Amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=INVOICE_STATUS,
        default='draft'
    )
    
    notes = models.TextField(_('Notes'), blank=True)
    terms_and_conditions = models.TextField(_('Terms and Conditions'), blank=True)
    
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Journal Entry')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Created By')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-invoice_date', '-invoice_number']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.get_invoice_type_display()}"
    
    def get_balance(self):
        return self.total_amount - self.paid_amount
    
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']


class InvoiceItem(models.Model):
    """
    Invoice Item - عناصر الفاتورة
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Invoice')
    )
    description = models.CharField(_('Description'), max_length=500)
    quantity = models.DecimalField(
        _('Quantity'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('1.00')
    )
    unit_price = models.DecimalField(
        _('Unit Price'),
        max_digits=15,
        decimal_places=2
    )
    tax_rate = models.DecimalField(
        _('Tax Rate %'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_rate = models.DecimalField(
        _('Discount Rate %'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total = models.DecimalField(
        _('Total'),
        max_digits=15,
        decimal_places=2
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Account')
    )
    
    class Meta:
        verbose_name = _('Invoice Item')
        verbose_name_plural = _('Invoice Items')
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"
    
    def calculate_total(self):
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_rate / 100)
        after_discount = subtotal - discount
        tax = after_discount * (self.tax_rate / 100)
        return after_discount + tax


class Payment(models.Model):
    """
    Payment - الدفعات
    """
    PAYMENT_TYPES = [
        ('receipt', _('Receipt')),
        ('payment', _('Payment')),
    ]
    
    PAYMENT_METHODS = [
        ('cash', _('Cash')),
        ('check', _('Check')),
        ('bank_transfer', _('Bank Transfer')),
        ('credit_card', _('Credit Card')),
        ('online', _('Online Payment')),
    ]
    
    payment_number = models.CharField(
        _('Payment Number'),
        max_length=50,
        unique=True
    )
    payment_type = models.CharField(
        _('Payment Type'),
        max_length=20,
        choices=PAYMENT_TYPES
    )
    payment_date = models.DateField(_('Payment Date'))
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PAYMENT_METHODS
    )
    
    amount = models.DecimalField(
        _('Amount'),
        max_digits=15,
        decimal_places=2
    )
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('Invoice')
    )
    
    reference_number = models.CharField(
        _('Reference Number'),
        max_length=100,
        blank=True,
        help_text=_('Check number, transaction ID, etc.')
    )
    
    notes = models.TextField(_('Notes'), blank=True)
    
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('Journal Entry')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Created By')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date', '-payment_number']
    
    def __str__(self):
        return f"{self.payment_number} - ${self.amount}"


class Budget(models.Model):
    """
    Budget - الميزانية
    """
    name = models.CharField(_('Budget Name'), max_length=200)
    period = models.ForeignKey(
        FinancialPeriod,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name=_('Financial Period')
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name=_('Account')
    )
    budgeted_amount = models.DecimalField(
        _('Budgeted Amount'),
        max_digits=15,
        decimal_places=2
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budgets',
        verbose_name=_('Property')
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')
        unique_together = ['period', 'account', 'property']
    
    def __str__(self):
        return f"{self.name} - ${self.budgeted_amount}"
    
    def get_actual_amount(self):
        """Get actual amount spent/earned in this period"""
        if not self.period:
            return 0
        
        entries = JournalEntryLine.objects.filter(
            account=self.account,
            journal_entry__entry_date__range=[
                self.period.start_date,
                self.period.end_date
            ],
            journal_entry__is_posted=True
        )
        
        if self.account.account_type == AccountType.EXPENSE:
            return entries.aggregate(total=models.Sum('debit_amount'))['total'] or 0
        else:  # REVENUE
            return entries.aggregate(total=models.Sum('credit_amount'))['total'] or 0
    
    def get_variance(self):
        return Decimal(self.budgeted_amount) - Decimal(self.get_actual_amount())
    
    def get_variance_percentage(self):
        if self.budgeted_amount == 0:
            return 0
        return (self.get_variance() / self.budgeted_amount) * 100
