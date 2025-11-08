from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.db.models import Q

from apps.sales.models import Buyer
from apps.sales.forms import BuyerForm, BuyerSearchForm


@login_required
def buyer_list(request):
    """List all buyers with search and filter"""
    buyers = Buyer.objects.all()
    
    # Search and filter
    form = BuyerSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        buyer_type = form.cleaned_data.get('buyer_type')
        is_qualified = form.cleaned_data.get('is_qualified')
        is_active = form.cleaned_data.get('is_active')
        
        if search:
            buyers = buyers.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(national_id__icontains=search)
            )
        
        if buyer_type:
            buyers = buyers.filter(buyer_type=buyer_type)
        
        if is_qualified == 'true':
            buyers = buyers.filter(is_qualified=True)
        elif is_qualified == 'false':
            buyers = buyers.filter(is_qualified=False)
        
        if is_active == 'true':
            buyers = buyers.filter(is_active=True)
        elif is_active == 'false':
            buyers = buyers.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(buyers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': form,
        'total_buyers': buyers.count(),
    }
    
    return render(request, 'sales/buyer_list.html', context)


@login_required
def buyer_detail(request, pk):
    """Display buyer details"""
    buyer = get_object_or_404(Buyer, pk=pk)
    
    # Get buyer's reservations and purchases
    reservations = buyer.reservations.all()[:5]
    purchases = buyer.purchases.all()[:5]
    
    context = {
        'buyer': buyer,
        'reservations': reservations,
        'purchases': purchases,
        'purchasing_power': buyer.get_purchasing_power(),
    }
    
    return render(request, 'sales/buyer_detail.html', context)


@login_required
def buyer_create(request):
    """Create a new buyer"""
    if request.method == 'POST':
        form = BuyerForm(request.POST, request.FILES)
        if form.is_valid():
            buyer = form.save()
            messages.success(request, _('Buyer created successfully'))
            return redirect('sales:buyer_detail', pk=buyer.pk)
    else:
        form = BuyerForm()
    
    context = {
        'form': form,
        'title': _('Create Buyer'),
    }
    
    return render(request, 'sales/buyer_form.html', context)


@login_required
def buyer_update(request, pk):
    """Update buyer information"""
    buyer = get_object_or_404(Buyer, pk=pk)
    
    if request.method == 'POST':
        form = BuyerForm(request.POST, request.FILES, instance=buyer)
        if form.is_valid():
            form.save()
            messages.success(request, _('Buyer updated successfully'))
            return redirect('sales:buyer_detail', pk=buyer.pk)
    else:
        form = BuyerForm(instance=buyer)
    
    context = {
        'form': form,
        'buyer': buyer,
        'title': _('Update Buyer'),
    }
    
    return render(request, 'sales/buyer_form.html', context)


@login_required
def buyer_delete(request, pk):
    """Delete a buyer"""
    buyer = get_object_or_404(Buyer, pk=pk)
    
    if request.method == 'POST':
        buyer.delete()
        messages.success(request, _('Buyer deleted successfully'))
        return redirect('sales:buyer_list')
    
    context = {
        'buyer': buyer,
    }
    
    return render(request, 'sales/buyer_confirm_delete.html', context)


@login_required
def buyer_qualify(request, pk):
    """Qualify a buyer"""
    buyer = get_object_or_404(Buyer, pk=pk)
    
    if buyer.qualify_buyer():
        messages.success(request, _('Buyer qualified successfully'))
    else:
        messages.error(request, _('Buyer does not meet qualification criteria'))
    
    return redirect('sales:buyer_detail', pk=buyer.pk)
