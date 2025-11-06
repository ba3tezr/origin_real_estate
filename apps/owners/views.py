"""
Views for Owners app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Owner
from .forms import OwnerForm, OwnerSearchForm


@login_required
def owner_list(request):
    """List all owners with search and filter"""
    owners = Owner.objects.all()
    
    # Search and Filter
    search_form = OwnerSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        city = search_form.cleaned_data.get('city')
        is_active = search_form.cleaned_data.get('is_active')
        
        if search:
            owners = owners.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(national_id__icontains=search)
            )
        
        if city:
            owners = owners.filter(city__icontains=city)
        
        if is_active is not None:
            owners = owners.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(owners, 20)
    page = request.GET.get('page')
    owners = paginator.get_page(page)
    
    context = {
        'owners': owners,
        'search_form': search_form,
        'total_count': Owner.objects.count(),
        'active_count': Owner.objects.filter(is_active=True).count(),
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
            return redirect('owners:list')
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
            return redirect('owners:list')
    else:
        form = OwnerForm(instance=owner)
    
    context = {
        'form': form,
        'owner': owner,
        'action': 'Update'
    }
    return render(request, 'owners/form.html', context)


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
