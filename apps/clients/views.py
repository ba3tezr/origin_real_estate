"""
Views for Clients app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Client
from .forms import ClientForm, ClientSearchForm

@login_required
def client_list(request):
    """List all clients with search and filter"""
    clients = Client.objects.all()
    
    # Search and Filter
    search_form = ClientSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        city = search_form.cleaned_data.get('city')
        is_active = search_form.cleaned_data.get('is_active')
        
        if search:
            clients = clients.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(national_id__icontains=search)
            )
        
        if city:
            clients = clients.filter(city__icontains=city)
        
        if is_active is not None:
            clients = clients.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(clients, 20)
    page = request.GET.get('page')
    clients = paginator.get_page(page)
    
    context = {
        'clients': clients,
        'search_form': search_form,
        'total_count': Client.objects.count(),
        'active_count': Client.objects.filter(is_active=True).count(),
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
            return redirect('clients:list')
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
            return redirect('clients:list')
    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client': client,
        'action': 'Update'
    }
    return render(request, 'clients/form.html', context)

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
