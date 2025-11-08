"""
Views for Owners app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Owner
from .forms import OwnerForm, OwnerSearchForm


@login_required
def owner_list(request):
    """List all owners with search and filter"""
    queryset = Owner.objects.annotate(properties_count=Count('properties'))
    
    search_form = OwnerSearchForm(request.GET)
    if search_form.is_valid():
        filters = search_form.cleaned_data
        search = filters.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
                | Q(national_id__icontains=search)
            )
        
        if filters.get('city'):
            queryset = queryset.filter(city__icontains=filters['city'])
        
        if filters.get('country'):
            queryset = queryset.filter(country__icontains=filters['country'])
        
        is_active = filters.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
    
    sort_option = request.GET.get('sort', 'name')
    sort_mapping = {
        'name': 'name',
        'email': 'email',
        'newest': '-created_at',
        'oldest': 'created_at',
        'properties': '-properties_count',
    }
    queryset = queryset.order_by(sort_mapping.get(sort_option, 'name'))
    
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Calculate statistics
    from apps.properties.models import Property
    total_owners = Owner.objects.count()
    active_owners = Owner.objects.filter(is_active=True).count()
    total_properties = Property.objects.count()
    portfolio_value = Property.objects.aggregate(total=Count('id'))['total'] or 0
    portfolio_value_sum = Property.objects.aggregate(total=Count('market_value'))['total'] or 0
    
    context = {
        'owners': page_obj,
        'search_form': search_form,
        'sort_option': sort_option,
        'total_owners': total_owners,
        'total_count': total_owners,
        'active_owners': active_owners,
        'active_count': active_owners,
        'total_properties': total_properties,
        'portfolio_value': portfolio_value,
    }
    return render(request, 'owners/list.html', context)


@login_required
def owner_create(request):
    """Create new owner"""
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            owner = form.save()
            messages.success(request, f'Owner {owner.name} created successfully!')
            return redirect('owners:detail', pk=owner.pk)
    else:
        form = OwnerForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'owners/form.html', context)


@login_required
def owner_update(request, pk):
    """Update existing owner"""
    owner = get_object_or_404(Owner, pk=pk)
    
    if request.method == 'POST':
        form = OwnerForm(request.POST, instance=owner)
        if form.is_valid():
            form.save()
            messages.success(request, f'Owner {owner.name} updated successfully!')
            return redirect('owners:detail', pk=owner.pk)
    else:
        form = OwnerForm(instance=owner)
    
    context = {
        'form': form,
        'owner': owner,
        'action': 'Update'
    }
    return render(request, 'owners/form.html', context)


@login_required
def owner_detail(request, pk):
    """Owner detail view with properties"""
    owner = get_object_or_404(Owner, pk=pk)
    properties = owner.properties.select_related('property_type').all()
    
    context = {
        'owner': owner,
        'properties': properties,
        'properties_count': properties.count(),
        'active_properties': properties.filter(is_active=True).count(),
        'available_properties': properties.filter(status='available').count(),
    }
    return render(request, 'owners/detail.html', context)


@login_required
def owner_delete(request, pk):
    """Delete owner"""
    owner = get_object_or_404(Owner, pk=pk)
    
    if request.method == 'POST':
        name = owner.name
        owner.delete()
        messages.success(request, f'Owner {name} deleted successfully!')
        return redirect('owners:list')
    
    context = {'owner': owner}
    return render(request, 'owners/confirm_delete.html', context)
