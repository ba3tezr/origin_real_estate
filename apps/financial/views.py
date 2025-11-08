"""
Views for Financial app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Account, AccountType, JournalEntry, JournalEntryLine,
    Invoice, InvoiceItem, Payment, Budget, FinancialPeriod
)
from .forms import (
    AccountForm, JournalEntryForm, InvoiceForm, PaymentForm,
    BudgetForm, FinancialPeriodForm, FinancialReportForm
)


@login_required
def financial_dashboard(request):
    """Financial Dashboard"""
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Summary Stats
    total_revenue = JournalEntryLine.objects.filter(
        account__account_type=AccountType.REVENUE,
        journal_entry__is_posted=True,
        journal_entry__entry_date__gte=last_30_days
    ).aggregate(total=Sum('credit_amount'))['total'] or 0
    
    total_expenses = JournalEntryLine.objects.filter(
        account__account_type=AccountType.EXPENSE,
        journal_entry__is_posted=True,
        journal_entry__entry_date__gte=last_30_days
    ).aggregate(total=Sum('debit_amount'))['total'] or 0
    
    net_income = Decimal(total_revenue) - Decimal(total_expenses)
    
    # Cash accounts balance
    cash_accounts = Account.objects.filter(
        account_type=AccountType.ASSET,
        name__icontains='cash'
    )
    cash_balance = sum([acc.get_balance() for acc in cash_accounts])
    
    # Invoices stats
    outstanding_invoices = Invoice.objects.filter(
        status__in=['issued', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    overdue_invoices = Invoice.objects.filter(
        due_date__lt=today,
        status__in=['issued', 'partial']
    ).count()
    
    # Recent transactions
    recent_entries = JournalEntry.objects.filter(
        is_posted=True
    ).order_by('-entry_date')[:10]
    
    # Recent invoices
    recent_invoices = Invoice.objects.order_by('-invoice_date')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.order_by('-payment_date')[:5]
    
    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'cash_balance': cash_balance,
        'outstanding_invoices': outstanding_invoices,
        'overdue_invoices': overdue_invoices,
        'recent_entries': recent_entries,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
    }
    return render(request, 'financial/dashboard.html', context)


# Chart of Accounts Views
@login_required
def account_list(request):
    """List all accounts in tree structure with filters"""
    # Start with all accounts
    queryset = Account.objects.all()
    
    # Apply filters
    account_type_filter = request.GET.get('account_type')
    search = request.GET.get('search')
    is_active = request.GET.get('is_active')
    
    if account_type_filter:
        queryset = queryset.filter(account_type=account_type_filter)
    
    if search:
        queryset = queryset.filter(
            Q(code__icontains=search) | Q(name__icontains=search)
        )
    
    if is_active == '1':
        queryset = queryset.filter(is_active=True)
    elif is_active == '0':
        queryset = queryset.filter(is_active=False)
    
    # Get all accounts grouped by type
    accounts_by_type = {}
    for acc_type in ['asset', 'liability', 'equity', 'revenue', 'expense']:
        accounts = queryset.filter(
            account_type=acc_type,
            parent=None
        ).prefetch_related('children').order_by('code')
        if accounts.exists():
            accounts_by_type[acc_type] = accounts
    
    # Count by type (from filtered queryset)
    asset_count = queryset.filter(account_type='asset').count()
    liability_count = queryset.filter(account_type='liability').count()
    equity_count = queryset.filter(account_type='equity').count()
    revenue_count = queryset.filter(account_type='revenue').count()
    expense_count = queryset.filter(account_type='expense').count()
    
    context = {
        'accounts_by_type': accounts_by_type,
        'total_accounts': queryset.count(),
        'asset_count': asset_count,
        'liability_count': liability_count,
        'equity_count': equity_count,
        'revenue_count': revenue_count,
        'expense_count': expense_count,
    }
    return render(request, 'financial/account_list.html', context)


@login_required
def account_create(request):
    """Create new account"""
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Account {account.code} created successfully!')
            return redirect('financial:account_list')
    else:
        form = AccountForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'financial/account_form.html', context)


@login_required
def account_detail(request, pk):
    """Account detail with transactions"""
    account = get_object_or_404(Account, pk=pk)
    
    # Get all transactions
    transactions = JournalEntryLine.objects.filter(
        account=account,
        journal_entry__is_posted=True
    ).select_related('journal_entry').order_by('-journal_entry__entry_date')
    
    paginator = Paginator(transactions, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'account': account,
        'transactions': page_obj,
        'balance': account.get_balance(),
    }
    return render(request, 'financial/account_detail.html', context)


# Journal Entry Views
@login_required
def journal_entry_list(request):
    """List all journal entries"""
    entries = JournalEntry.objects.all().order_by('-entry_date', '-entry_number')
    
    # Filters
    status = request.GET.get('status')
    if status == 'posted':
        entries = entries.filter(is_posted=True)
    elif status == 'unposted':
        entries = entries.filter(is_posted=False)
    
    paginator = Paginator(entries, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'entries': page_obj,
        'total_count': JournalEntry.objects.count(),
        'posted_count': JournalEntry.objects.filter(is_posted=True).count(),
    }
    return render(request, 'financial/journal_entry_list.html', context)


@login_required
def journal_entry_create(request):
    """Create new journal entry"""
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            messages.success(request, f'Journal Entry {entry.entry_number} created!')
            return redirect('financial:journal_entry_detail', pk=entry.pk)
    else:
        form = JournalEntryForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'financial/journal_entry_form.html', context)


@login_required
def journal_entry_detail(request, pk):
    """Journal entry detail"""
    entry = get_object_or_404(JournalEntry, pk=pk)
    
    context = {
        'entry': entry,
        'lines': entry.lines.all(),
        'total_debit': entry.get_total_debit(),
        'total_credit': entry.get_total_credit(),
        'is_balanced': entry.is_balanced(),
    }
    return render(request, 'financial/journal_entry_detail.html', context)


@login_required
def journal_entry_post(request, pk):
    """Post a journal entry"""
    entry = get_object_or_404(JournalEntry, pk=pk)
    
    if entry.post():
        messages.success(request, f'Journal Entry {entry.entry_number} posted successfully!')
    else:
        messages.error(request, 'Cannot post entry. Entry must be balanced!')
    
    return redirect('financial:journal_entry_detail', pk=pk)


# Invoice Views
@login_required
def invoice_list(request):
    """List all invoices"""
    invoices = Invoice.objects.all().order_by('-invoice_date')
    
    # Filters
    status = request.GET.get('status')
    if status:
        invoices = invoices.filter(status=status)
    
    invoice_type = request.GET.get('type')
    if invoice_type:
        invoices = invoices.filter(invoice_type=invoice_type)
    
    paginator = Paginator(invoices, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'invoices': page_obj,
        'total_count': Invoice.objects.count(),
        'draft_count': Invoice.objects.filter(status='draft').count(),
        'issued_count': Invoice.objects.filter(status='issued').count(),
        'paid_count': Invoice.objects.filter(status='paid').count(),
    }
    return render(request, 'financial/invoice_list.html', context)


@login_required
def invoice_create(request):
    """Create new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, f'Invoice {invoice.invoice_number} created!')
            return redirect('financial:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'financial/invoice_form.html', context)


@login_required
def invoice_detail(request, pk):
    """Invoice detail"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
        'payments': invoice.payments.all(),
        'balance': invoice.get_balance(),
    }
    return render(request, 'financial/invoice_detail.html', context)


# Payment/Receipt Voucher Views
@login_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all().order_by('-payment_date')
    
    # Filters
    payment_type = request.GET.get('type')
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    
    paginator = Paginator(payments, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'payments': page_obj,
        'total_count': Payment.objects.count(),
        'receipt_count': Payment.objects.filter(payment_type='receipt').count(),
        'payment_count': Payment.objects.filter(payment_type='payment').count(),
    }
    return render(request, 'financial/payment_list.html', context)


@login_required
def payment_create(request):
    """Create new payment/receipt voucher"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            
            # Update invoice if linked
            if payment.invoice:
                invoice = payment.invoice
                invoice.paid_amount += payment.amount
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = 'paid'
                elif invoice.paid_amount > 0:
                    invoice.status = 'partial'
                invoice.save()
            
            messages.success(request, f'Payment {payment.payment_number} created!')
            return redirect('financial:payment_detail', pk=payment.pk)
    else:
        form = PaymentForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'financial/payment_form.html', context)


@login_required
def payment_detail(request, pk):
    """Payment detail"""
    payment = get_object_or_404(Payment, pk=pk)
    
    context = {'payment': payment}
    return render(request, 'financial/payment_detail.html', context)


@login_required
def payment_print(request, pk):
    """Print payment voucher"""
    payment = get_object_or_404(Payment, pk=pk)
    
    context = {'payment': payment}
    return render(request, 'financial/payment_print.html', context)


# Financial Reports
@login_required
def report_trial_balance(request):
    """Trial Balance Report"""
    form = FinancialReportForm(request.GET or None)
    
    accounts = Account.objects.filter(is_active=True).order_by('code')
    report_data = []
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')
    
    for account in accounts:
        balance = account.get_balance()
        if balance != 0:
            if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                debit = balance if balance > 0 else 0
                credit = abs(balance) if balance < 0 else 0
            else:
                credit = balance if balance > 0 else 0
                debit = abs(balance) if balance < 0 else 0
            
            report_data.append({
                'account': account,
                'debit': debit,
                'credit': credit,
            })
            total_debit += Decimal(str(debit))
            total_credit += Decimal(str(credit))
    
    context = {
        'form': form,
        'report_data': report_data,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'is_balanced': total_debit == total_credit,
    }
    return render(request, 'financial/report_trial_balance.html', context)


@login_required
def report_profit_loss(request):
    """Profit & Loss Statement"""
    form = FinancialReportForm(request.GET or None)
    
    # Get date range
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1)
    
    # Revenue
    revenue_accounts = Account.objects.filter(account_type=AccountType.REVENUE)
    total_revenue = Decimal('0.00')
    revenue_data = []
    
    for account in revenue_accounts:
        lines = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__is_posted=True,
            journal_entry__entry_date__range=[start_date, end_date]
        )
        amount = lines.aggregate(total=Sum('credit_amount'))['total'] or 0
        if amount > 0:
            revenue_data.append({'account': account, 'amount': amount})
            total_revenue += Decimal(str(amount))
    
    # Expenses
    expense_accounts = Account.objects.filter(account_type=AccountType.EXPENSE)
    total_expenses = Decimal('0.00')
    expense_data = []
    
    for account in expense_accounts:
        lines = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__is_posted=True,
            journal_entry__entry_date__range=[start_date, end_date]
        )
        amount = lines.aggregate(total=Sum('debit_amount'))['total'] or 0
        if amount > 0:
            expense_data.append({'account': account, 'amount': amount})
            total_expenses += Decimal(str(amount))
    
    net_income = total_revenue - total_expenses
    
    context = {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'revenue_data': revenue_data,
        'expense_data': expense_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income,
    }
    return render(request, 'financial/report_profit_loss.html', context)


@login_required
def report_balance_sheet(request):
    """Balance Sheet"""
    report_date = timezone.now().date()
    
    # Assets
    asset_accounts = Account.objects.filter(account_type=AccountType.ASSET)
    total_assets = Decimal('0.00')
    asset_data = []
    
    for account in asset_accounts:
        balance = account.get_balance()
        if balance != 0:
            asset_data.append({'account': account, 'amount': balance})
            total_assets += balance
    
    # Liabilities
    liability_accounts = Account.objects.filter(account_type=AccountType.LIABILITY)
    total_liabilities = Decimal('0.00')
    liability_data = []
    
    for account in liability_accounts:
        balance = account.get_balance()
        if balance != 0:
            liability_data.append({'account': account, 'amount': balance})
            total_liabilities += balance
    
    # Equity
    equity_accounts = Account.objects.filter(account_type=AccountType.EQUITY)
    total_equity = Decimal('0.00')
    equity_data = []
    
    for account in equity_accounts:
        balance = account.get_balance()
        if balance != 0:
            equity_data.append({'account': account, 'amount': balance})
            total_equity += balance
    
    total_liabilities_equity = total_liabilities + total_equity
    
    context = {
        'report_date': report_date,
        'asset_data': asset_data,
        'liability_data': liability_data,
        'equity_data': equity_data,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'total_liabilities_equity': total_liabilities_equity,
        'is_balanced': total_assets == total_liabilities_equity,
    }
    return render(request, 'financial/report_balance_sheet.html', context)
