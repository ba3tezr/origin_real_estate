from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator

from apps.sales.models import PropertyReservation
from apps.sales.forms import PropertyReservationForm, ReservationCancelForm


@login_required
def reservation_list(request):
    """List all property reservations"""
    # Get all reservations (before filtering)
    all_reservations = PropertyReservation.objects.select_related(
        'property', 'buyer', 'reserved_by'
    ).all()
    
    # Calculate statistics from ALL reservations (not filtered)
    total_reservations = all_reservations.count()
    approved_reservations = all_reservations.filter(status='approved').count()
    pending_reservations = all_reservations.filter(status='pending').count()
    expired_count = sum(1 for r in all_reservations if r.is_expired)  # Now it's a property
    
    # Now apply filter for display
    reservations = all_reservations
    status_filter = request.GET.get('status')
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(reservations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_reservations': total_reservations,
        'active_reservations': approved_reservations,  # Active = Approved
        'pending_reservations': pending_reservations,
        'expired_reservations': expired_count,
    }
    
    return render(request, 'sales/reservation_list.html', context)


@login_required
def reservation_detail(request, pk):
    """Display reservation details"""
    reservation = get_object_or_404(
        PropertyReservation.objects.select_related('property', 'buyer', 'reserved_by'),
        pk=pk
    )
    
    context = {
        'reservation': reservation,
    }
    
    return render(request, 'sales/reservation_detail.html', context)


@login_required
def reservation_create(request):
    """Create a new property reservation"""
    if request.method == 'POST':
        form = PropertyReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.reserved_by = request.user
            reservation.save()
            messages.success(request, _('Reservation created successfully'))
            return redirect('sales:reservation_detail', pk=reservation.pk)
    else:
        form = PropertyReservationForm()
    
    context = {
        'form': form,
        'title': _('Create Reservation'),
    }
    
    return render(request, 'sales/reservation_form.html', context)


@login_required
def reservation_update(request, pk):
    """Update reservation"""
    reservation = get_object_or_404(PropertyReservation, pk=pk)
    
    if reservation.status in ['cancelled', 'converted']:
        messages.error(request, _('Cannot update this reservation'))
        return redirect('sales:reservation_detail', pk=reservation.pk)
    
    if request.method == 'POST':
        form = PropertyReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, _('Reservation updated successfully'))
            return redirect('sales:reservation_detail', pk=reservation.pk)
    else:
        form = PropertyReservationForm(instance=reservation)
    
    context = {
        'form': form,
        'reservation': reservation,
        'title': _('Update Reservation'),
    }
    
    return render(request, 'sales/reservation_form.html', context)


@login_required
def reservation_approve(request, pk):
    """Approve a reservation"""
    reservation = get_object_or_404(PropertyReservation, pk=pk)
    
    if reservation.status == 'pending':
        reservation.status = 'approved'
        reservation.save()
        messages.success(request, _('Reservation approved successfully'))
    else:
        messages.error(request, _('Reservation cannot be approved'))
    
    return redirect('sales:reservation_detail', pk=reservation.pk)


@login_required
def reservation_cancel(request, pk):
    """Cancel a reservation"""
    reservation = get_object_or_404(PropertyReservation, pk=pk)
    
    if reservation.status in ['cancelled', 'converted']:
        messages.error(request, _('Reservation already processed'))
        return redirect('sales:reservation_detail', pk=reservation.pk)
    
    if request.method == 'POST':
        form = ReservationCancelForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['cancellation_reason']
            reservation.cancel_reservation(reason)
            messages.success(request, _('Reservation cancelled successfully'))
            return redirect('sales:reservation_detail', pk=reservation.pk)
    else:
        form = ReservationCancelForm()
    
    context = {
        'form': form,
        'reservation': reservation,
    }
    
    return render(request, 'sales/reservation_cancel.html', context)


@login_required
def reservation_convert(request, pk):
    """Convert reservation to sales contract"""
    reservation = get_object_or_404(PropertyReservation, pk=pk)
    
    if reservation.convert_to_sale():
        messages.success(request, _('Reservation converted. Please create sales contract.'))
        # Redirect to contract creation with property and buyer pre-filled
        from django.urls import reverse
        url = reverse('sales:contract_create')
        return redirect(f'{url}?property={reservation.property.pk}&buyer={reservation.buyer.pk}')
    else:
        messages.error(request, _('Cannot convert. Reservation must be approved first.'))
        return redirect('sales:reservation_detail', pk=reservation.pk)
