from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.db.models import Sum

from apps.sales.models import SalesContract, SalesPayment, SalesPaymentPlan
from apps.sales.forms import SalesContractForm, SalesPaymentForm


@login_required
def contract_list(request):
    """List all sales contracts"""
    contracts = SalesContract.objects.select_related(
        'property', 'buyer', 'seller', 'created_by'
    ).all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        contracts = contracts.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(contracts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_value = contracts.aggregate(total=Sum('sale_price'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_contracts': contracts.count(),
        'total_value': total_value,
    }
    
    return render(request, 'sales/contract_list.html', context)


@login_required
def contract_detail(request, pk):
    """Display contract details"""
    contract = get_object_or_404(
        SalesContract.objects.select_related(
            'property', 'buyer', 'seller', 'created_by', 'approved_by'
        ).prefetch_related('payment_plans', 'payments'),
        pk=pk
    )
    
    # Payment summary
    total_paid = contract.get_total_paid()
    remaining = contract.get_remaining_amount()
    progress = contract.get_payment_progress_percentage()
    
    # Recent payments
    recent_payments = contract.payments.order_by('-payment_date')[:5]
    
    # Payment plans
    payment_plans = contract.payment_plans.order_by('due_date')
    
    context = {
        'contract': contract,
        'total_paid': total_paid,
        'remaining': remaining,
        'progress': progress,
        'recent_payments': recent_payments,
        'payment_plans': payment_plans,
    }
    
    return render(request, 'sales/contract_detail.html', context)


@login_required
def contract_create(request):
    """Create a new sales contract"""
    if request.method == 'POST':
        form = SalesContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.save()
            
            # Generate payment plan if has installments
            if contract.has_installments and contract.number_of_installments > 0:
                from datetime import timedelta
                from decimal import Decimal
                
                remaining_amount = contract.sale_price - contract.down_payment - contract.financed_amount
                installment_amount = remaining_amount / contract.number_of_installments
                
                for i in range(1, contract.number_of_installments + 1):
                    if contract.installment_frequency == 'monthly':
                        due_date = contract.contract_date + timedelta(days=30*i)
                    elif contract.installment_frequency == 'quarterly':
                        due_date = contract.contract_date + timedelta(days=90*i)
                    elif contract.installment_frequency == 'semi_annual':
                        due_date = contract.contract_date + timedelta(days=180*i)
                    else:  # annual
                        due_date = contract.contract_date + timedelta(days=365*i)
                    
                    SalesPaymentPlan.objects.create(
                        sales_contract=contract,
                        installment_number=i,
                        due_date=due_date,
                        amount=installment_amount
                    )
            
            messages.success(request, _('Sales contract created successfully'))
            return redirect('sales:contract_detail', pk=contract.pk)
    else:
        # Pre-fill from reservation if provided
        property_id = request.GET.get('property')
        buyer_id = request.GET.get('buyer')
        
        initial = {}
        if property_id:
            initial['property'] = property_id
        if buyer_id:
            initial['buyer'] = buyer_id
        
        form = SalesContractForm(initial=initial)
    
    context = {
        'form': form,
        'title': _('Create Sales Contract'),
    }
    
    return render(request, 'sales/contract_form.html', context)


@login_required
def contract_update(request, pk):
    """Update sales contract"""
    contract = get_object_or_404(SalesContract, pk=pk)
    
    if contract.status in ['completed', 'cancelled']:
        messages.error(request, _('Cannot update this contract'))
        return redirect('sales:contract_detail', pk=contract.pk)
    
    if request.method == 'POST':
        form = SalesContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, _('Contract updated successfully'))
            return redirect('sales:contract_detail', pk=contract.pk)
    else:
        form = SalesContractForm(instance=contract)
    
    context = {
        'form': form,
        'contract': contract,
        'title': _('Update Contract'),
    }
    
    return render(request, 'sales/contract_form.html', context)


@login_required
def payment_create(request, contract_pk):
    """Record a new payment for a contract"""
    contract = get_object_or_404(SalesContract, pk=contract_pk)
    
    if request.method == 'POST':
        form = SalesPaymentForm(request.POST, request.FILES, contract=contract)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user
            payment.status = 'completed'
            payment.save()
            
            messages.success(request, _('Payment recorded successfully'))
            return redirect('sales:contract_detail', pk=contract.pk)
    else:
        form = SalesPaymentForm(contract=contract)
    
    context = {
        'form': form,
        'contract': contract,
        'title': _('Record Payment'),
    }
    
    return render(request, 'sales/payment_form.html', context)


@login_required
def payment_list(request):
    """List all payments"""
    payments = SalesPayment.objects.select_related(
        'sales_contract', 'received_by'
    ).all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(payments, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_amount = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_payments': payments.count(),
        'total_amount': total_amount,
    }
    
    return render(request, 'sales/payment_list.html', context)
