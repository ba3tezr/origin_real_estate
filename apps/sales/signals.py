"""
Signals for Sales module - Financial Integration
Auto-create journal entries when sales payments are recorded
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

from apps.sales.models import SalesPayment
from apps.financial.models import JournalEntry, JournalEntryLine, Account


@receiver(post_save, sender=SalesPayment)
def create_journal_entry_for_sales_payment(sender, instance, created, **kwargs):
    """
    Auto-create journal entry when sales payment is completed
    
    Accounting Entry:
    Debit: Bank/Cash Account (Asset)
    Credit: Sales Revenue Account (Revenue)
    """
    # Only process completed payments
    if instance.status != 'completed':
        return
    
    # Check if journal entry already exists for this payment
    existing_entry = JournalEntry.objects.filter(
        reference=f"SALES-PAY-{instance.receipt_number}"
    ).first()
    
    if existing_entry:
        # Already has a journal entry, skip
        return
    
    try:
        # Get or create accounts
        # 1. Bank/Cash Account (Asset) - Debit
        bank_account = get_or_create_bank_account(instance.payment_method)
        
        # 2. Sales Revenue Account - Credit
        revenue_account = get_or_create_sales_revenue_account()
        
        # Generate unique entry number
        entry_number = generate_journal_entry_number()
        
        # Create Journal Entry
        journal_entry = JournalEntry.objects.create(
            entry_number=entry_number,
            entry_date=instance.payment_date,
            entry_type='automated',
            reference=f"SALES-PAY-{instance.receipt_number}",
            description=f"Sales payment from {instance.sales_contract.buyer.name} for contract {instance.sales_contract.contract_number}",
            property=instance.sales_contract.property,
            created_by=instance.received_by,
            is_posted=True,
            posted_at=timezone.now()
        )
        
        # Create Debit Line (Bank/Cash)
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=bank_account,
            debit_amount=instance.amount,
            credit_amount=Decimal('0.00'),
            description=f"Receipt: {instance.receipt_number} - {instance.get_payment_type_display()}"
        )
        
        # Create Credit Line (Sales Revenue)
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=revenue_account,
            debit_amount=Decimal('0.00'),
            credit_amount=instance.amount,
            description=f"Sales revenue from contract {instance.sales_contract.contract_number}"
        )
        
        print(f"✅ Journal Entry {entry_number} created for payment {instance.receipt_number}")
        
    except Exception as e:
        print(f"❌ Error creating journal entry for payment {instance.receipt_number}: {str(e)}")


def get_or_create_bank_account(payment_method):
    """
    Get or create appropriate bank/cash account based on payment method
    """
    account_mapping = {
        'cash': ('1010', 'Cash on Hand', 'النقدية في الصندوق'),
        'bank_transfer': ('1020', 'Bank Account - Main', 'الحساب البنكي الرئيسي'),
        'check': ('1030', 'Checks Received', 'الشيكات المستلمة'),
        'credit_card': ('1020', 'Bank Account - Main', 'الحساب البنكي الرئيسي'),
        'mortgage': ('1040', 'Mortgage Receivable', 'قروض المستلمة'),
        'online': ('1020', 'Bank Account - Main', 'الحساب البنكي الرئيسي'),
    }
    
    code, name, name_ar = account_mapping.get(payment_method, ('1020', 'Bank Account - Main', 'الحساب البنكي الرئيسي'))
    
    account, created = Account.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'name_ar': name_ar,
            'account_type': 'asset',
            'is_system': True,
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ Created account: {code} - {name}")
    
    return account


def get_or_create_sales_revenue_account():
    """
    Get or create sales revenue account
    """
    account, created = Account.objects.get_or_create(
        code='4010',
        defaults={
            'name': 'Property Sales Revenue',
            'name_ar': 'إيرادات مبيعات العقارات',
            'account_type': 'revenue',
            'is_system': True,
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ Created account: 4010 - Property Sales Revenue")
    
    return account


def generate_journal_entry_number():
    """
    Generate unique journal entry number
    Format: JE-YYYYMMDD-NNNN
    """
    from django.utils.crypto import get_random_string
    
    today = timezone.now().strftime('%Y%m%d')
    
    # Find last entry today
    last_entry = JournalEntry.objects.filter(
        entry_number__startswith=f"JE-{today}"
    ).order_by('-entry_number').first()
    
    if last_entry:
        try:
            last_num = int(last_entry.entry_number.split('-')[-1])
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    return f"JE-{today}-{next_num:04d}"
