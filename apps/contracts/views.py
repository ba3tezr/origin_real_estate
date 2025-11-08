"""Views for Contracts app"""
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ContractForm,
    ContractPaymentForm,
    ContractRenewalForm,
    ContractSearchForm,
)
from .models import Contract, ContractPayment, ContractRenewal

@login_required
def contract_list(request):
    """List all contracts with advanced filtering and insights."""
    queryset = Contract.objects.select_related('property', 'client')

    search_form = ContractSearchForm(request.GET)
    if search_form.is_valid():
        data = search_form.cleaned_data

        if data.get('search'):
            queryset = queryset.filter(
                Q(contract_number__icontains=data['search'])
                | Q(client__name__icontains=data['search'])
                | Q(property__title__icontains=data['search'])
            )

        if data.get('status'):
            queryset = queryset.filter(status=data['status'])

        if data.get('contract_type'):
            queryset = queryset.filter(contract_type=data['contract_type'])

        if data.get('payment_frequency'):
            queryset = queryset.filter(payment_frequency=data['payment_frequency'])

        if data.get('start_from'):
            queryset = queryset.filter(start_date__gte=data['start_from'])

        if data.get('start_to'):
            queryset = queryset.filter(start_date__lte=data['start_to'])

        if data.get('end_from'):
            queryset = queryset.filter(end_date__gte=data['end_from'])

        if data.get('end_to'):
            queryset = queryset.filter(end_date__lte=data['end_to'])

    sort_option = request.GET.get('sort', 'start_desc')
    sort_mapping = {
        'start_desc': '-start_date',
        'start_asc': 'start_date',
        'end_desc': '-end_date',
        'end_asc': 'end_date',
        'rent_high': '-rent_amount',
        'rent_low': 'rent_amount',
        'created_new': '-created_at',
        'created_old': 'created_at',
    }
    queryset = queryset.order_by(sort_mapping.get(sort_option, '-start_date'))

    filtered_rent_total = queryset.aggregate(total=Sum('rent_amount'))['total'] or 0

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)
    pagination_querystring = query_params.urlencode()

    today = timezone.now().date()
    upcoming_threshold = today + timedelta(days=30)

    summary_all = Contract.objects.all()
    portfolio_rent_total = summary_all.aggregate(total=Sum('rent_amount'))['total'] or 0
    context = {
        'contracts': page_obj,
        'search_form': search_form,
        'sort_option': sort_option,
        'filter_applied': any(v for k, v in request.GET.items() if k not in ['page', 'sort']),
        'total_contracts': summary_all.count(),
        'total_count': summary_all.count(),
        'active_contracts': summary_all.filter(status='active').count(),
        'active_count': summary_all.filter(status='active').count(),
        'expiring_soon': summary_all.filter(end_date__range=(today, upcoming_threshold)).count(),
        'expiring_soon_count': summary_all.filter(end_date__range=(today, upcoming_threshold)).count(),
        'expired_contracts': summary_all.filter(status='expired').count(),
        'overdue_contracts_count': summary_all.filter(end_date__lt=today, status__in=['active', 'renewed']).count(),
        'pending_payments_count': ContractPayment.objects.filter(status='pending').count(),
        'pagination_querystring': pagination_querystring,
        'filtered_rent_value': filtered_rent_total,
        'total_monthly_rent': portfolio_rent_total,
        'total_rent_value': portfolio_rent_total,
    }
    return render(request, 'contracts/list.html', context)

@login_required
def contract_detail(request, pk):
    """Detailed view for a contract including payments and renewals."""
    contract = get_object_or_404(
        Contract.objects.select_related('property', 'client'), pk=pk
    )

    payments = contract.payments.order_by('-payment_date')
    renewals = contract.renewals.select_related('new_contract').order_by('-renewal_date')

    total_paid = contract.get_total_paid()
    duration_months = max(contract.get_duration_months(), 1)
    total_due = contract.get_total_amount() * duration_months
    outstanding = contract.get_outstanding_balance()

    today = timezone.now().date()
    days_until_end = (contract.end_date - today).days if contract.end_date else None

    context = {
        'contract': contract,
        'payments': payments,
        'renewals': renewals,
        'total_paid': total_paid,
        'total_due': total_due,
        'outstanding_balance': outstanding,
        'days_until_end': days_until_end,
        'next_payment_day': contract.payment_day,
        'duration_months': duration_months,
    }
    return render(request, 'contracts/detail.html', context)


@login_required
def contract_create(request):
    """Create new contract"""
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save()
            messages.success(request, f'Contract {contract.contract_number} created!')
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ContractForm()

    context = {'form': form, 'action': 'Create', 'contract': None}
    return render(request, 'contracts/form.html', context)

@login_required
def contract_update(request, pk):
    """Update existing contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contract {contract.contract_number} updated!')
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ContractForm(instance=contract)
    
    context = {'form': form, 'contract': contract, 'action': 'Update'}
    return render(request, 'contracts/form.html', context)

@login_required
def contract_delete(request, pk):
    """Delete contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        number = contract.contract_number
        contract.delete()
        messages.success(request, f'Contract {number} deleted!')
        return redirect('contracts:list')
    
    context = {'contract': contract}
    return render(request, 'contracts/confirm_delete.html', context)


@login_required
def contract_payment_create(request, contract_pk):
    """Record a payment for a contract."""
    contract = get_object_or_404(Contract, pk=contract_pk)

    if request.method == 'POST':
        form = ContractPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.contract = contract
            payment.save()
            messages.success(request, 'Payment recorded successfully!')
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ContractPaymentForm(initial={'payment_date': timezone.now().date()})

    context = {
        'form': form,
        'contract': contract,
        'heading': 'Record Payment',
        'action_label': 'Save Payment',
    }
    return render(request, 'contracts/related_form.html', context)


@login_required
def contract_payment_delete(request, pk):
    payment = get_object_or_404(ContractPayment, pk=pk)
    contract_pk = payment.contract.pk

    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully!')
        return redirect('contracts:detail', pk=contract_pk)

    context = {
        'object_name': f"Payment {payment.payment_date} - ${payment.amount}",
        'contract': payment.contract,
    }
    return render(request, 'contracts/related_confirm_delete.html', context)


@login_required
def contract_renewal_create(request, contract_pk):
    """Log a renewal record for a contract."""
    contract = get_object_or_404(Contract, pk=contract_pk)

    if request.method == 'POST':
        form = ContractRenewalForm(request.POST, contract=contract)
        if form.is_valid():
            renewal = form.save(commit=False)
            renewal.original_contract = contract
            renewal.save()
            messages.success(request, 'Contract renewal recorded!')
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ContractRenewalForm(initial={'renewal_date': timezone.now().date()}, contract=contract)

    context = {
        'form': form,
        'contract': contract,
        'heading': 'Record Renewal',
        'action_label': 'Save Renewal',
    }
    return render(request, 'contracts/related_form.html', context)


@login_required
def contract_renewal_delete(request, pk):
    renewal = get_object_or_404(ContractRenewal, pk=pk)
    contract_pk = renewal.original_contract.pk

    if request.method == 'POST':
        renewal.delete()
        messages.success(request, 'Renewal deleted successfully!')
        return redirect('contracts:detail', pk=contract_pk)

    context = {
        'object_name': f"Renewal {renewal.renewal_date}",
        'contract': renewal.original_contract,
    }
    return render(request, 'contracts/related_confirm_delete.html', context)
