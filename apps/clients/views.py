"""
Views for Clients app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum

from .models import Client
from .forms import ClientForm, ClientSearchForm


@login_required
def client_list(request):
    """List all clients with search and filter"""
    queryset = Client.objects.annotate(contracts_count=Count('contracts'))
    
    search_form = ClientSearchForm(request.GET)
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
        'contracts': '-contracts_count',
    }
    queryset = queryset.order_by(sort_mapping.get(sort_option, 'name'))
    
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Calculate statistics
    from apps.contracts.models import Contract
    total_count = Client.objects.count()
    active_count = Client.objects.filter(is_active=True).count()
    active_contracts = Contract.objects.filter(status='active').count()
    monthly_revenue = Contract.objects.filter(status='active').aggregate(
        total=Sum('rent_amount')
    )['total'] or 0
    
    context = {
        'clients': page_obj,
        'search_form': search_form,
        'sort_option': sort_option,
        'total_count': total_count,
        'active_count': active_count,
        'active_contracts': active_contracts,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'clients/list.html', context)


@login_required
def client_create(request):
    """Create new client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client {client.name} created successfully!')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = ClientForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'clients/form.html', context)


@login_required
def client_update(request, pk):
    """Update existing client"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client {client.name} updated successfully!')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client': client,
        'action': 'Update'
    }
    return render(request, 'clients/form.html', context)


@login_required
def client_detail(request, pk):
    """Client detail view with contracts"""
    client = get_object_or_404(Client, pk=pk)
    contracts = client.contracts.select_related('property').all()
    
    context = {
        'client': client,
        'contracts': contracts,
        'contracts_count': contracts.count(),
        'active_contracts': contracts.filter(status='active').count(),
    }
    return render(request, 'clients/detail.html', context)


@login_required
def client_delete(request, pk):
    """Delete client"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        name = client.name
        client.delete()
        messages.success(request, f'Client {name} deleted successfully!')
        return redirect('clients:list')
    
    context = {'client': client}
    return render(request, 'clients/confirm_delete.html', context)
