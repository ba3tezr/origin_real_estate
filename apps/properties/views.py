"""
Views for Properties app
"""
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from urllib.parse import urlencode
from django.http import JsonResponse
from .models import (
    Property,
    PropertyType,
    PropertyDocument,
    PropertyImage,
    PropertyValuation,
    PropertyAmenity,
    PropertyInspection,
    PropertyExpense,
    PropertyRevenue,
)
from .forms import (
    PropertyForm,
    PropertyTypeForm,
    PropertySearchForm,
    PropertyDocumentForm,
    PropertyImageForm,
    PropertyValuationForm,
    PropertyAmenityForm,
    PropertyInspectionForm,
    PropertyExpenseForm,
    PropertyRevenueForm,
)

@login_required
def property_list(request):
    """List all properties with advanced filtering and display options."""
    queryset = Property.objects.select_related('property_type', 'owner')

    # Search and filter
    search_form = PropertySearchForm(request.GET)
    if search_form.is_valid():
        filters = search_form.cleaned_data
        search = filters.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(title__icontains=search)
                | Q(address__icontains=search)
                | Q(city__icontains=search)
            )

        if filters.get('property_type'):
            queryset = queryset.filter(property_type=filters['property_type'])

        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])

        if filters.get('city'):
            queryset = queryset.filter(city__icontains=filters['city'])

        if filters.get('min_rent') is not None:
            queryset = queryset.filter(rental_price_monthly__gte=filters['min_rent'])

        if filters.get('max_rent') is not None:
            queryset = queryset.filter(rental_price_monthly__lte=filters['max_rent'])

        if filters.get('bedrooms') is not None:
            queryset = queryset.filter(bedrooms__gte=filters['bedrooms'])

        if filters.get('is_furnished') is not None:
            queryset = queryset.filter(is_furnished=filters['is_furnished'])

    # Sorting
    sort_option = request.GET.get('sort', '-created_at')
    sort_mapping = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'code': 'code',
        'title': 'title',
        'rent_high': '-rental_price_monthly',
        'rent_low': 'rental_price_monthly',
        'area_high': '-area_sqm',
        'area_low': 'area_sqm',
    }
    queryset = queryset.order_by(sort_mapping.get(sort_option, '-created_at'))

    # Display mode (table/grid)
    display_mode = request.GET.get('display', 'table')
    per_page = 12 if display_mode == 'grid' else 20

    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params_table = query_params.copy()
    query_params_table['display'] = 'table'
    query_params_grid = query_params.copy()
    query_params_grid['display'] = 'grid'

    pagination_query = query_params.copy()

    # Statistics for summary cards
    total_properties = Property.objects.count()
    available_count = Property.objects.filter(status='available').count()
    rented_count = Property.objects.filter(status='rented').count()
    maintenance_count = Property.objects.filter(status='maintenance').count()
    total_value = Property.objects.aggregate(total=Sum('market_value'))['total'] or 0
    
    # Property types for filter dropdown
    property_types = PropertyType.objects.filter(is_active=True)

    context = {
        'properties': page_obj,
        'search_form': search_form,
        'display_mode': display_mode,
        'sort_option': sort_option,
        'total_properties': total_properties,
        'total_count': total_properties,
        'active_count': Property.objects.filter(is_active=True).count(),
        'available_count': available_count,
        'rented_count': rented_count,
        'maintenance_count': maintenance_count,
        'total_value': total_value,
        'property_types': property_types,
        'filter_applied': any(v for k, v in request.GET.items() if k not in ['page']),
        'table_querystring': query_params_table.urlencode(),
        'grid_querystring': query_params_grid.urlencode(),
        'pagination_querystring': pagination_query.urlencode(),
    }
    return render(request, 'properties/list.html', context)


@login_required
def property_dashboard(request):
    """Analytics dashboard for properties."""
    properties = Property.objects.all()

    status_breakdown_qs = (
        properties.values('status').annotate(total=Count('id')).order_by('-total')
    )
    status_breakdown = list(status_breakdown_qs)
    status_labels = dict(Property.STATUS_CHOICES)
    for item in status_breakdown:
        item['label'] = status_labels.get(item['status'], item['status'].title())

    type_distribution_qs = (
        properties.values('property_type__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:6]
    )
    type_distribution = list(type_distribution_qs)

    average_occupancy = properties.aggregate(avg=Avg('occupancy_rate'))['avg'] or 0
    average_roi = properties.aggregate(avg=Avg('average_roi'))['avg'] or 0

    # Revenue trend (last 6 months)
    six_months_ago = timezone.now().date().replace(day=1)
    monthly_revenue_qs = (
        PropertyRevenue.objects.filter(revenue_date__gte=six_months_ago - timedelta(days=180))
        .values('revenue_date__year', 'revenue_date__month')
        .annotate(total=Sum('amount'))
        .order_by('revenue_date__year', 'revenue_date__month')
    )
    monthly_revenue = [
        {
            'revenue_date__year': item['revenue_date__year'],
            'revenue_date__month': item['revenue_date__month'],
            'total': float(item['total']) if item['total'] is not None else 0,
        }
        for item in monthly_revenue_qs
    ]

    top_roi_properties_qs = (
        properties.filter(average_roi__isnull=False)
        .order_by('-average_roi')
        .values('code', 'title', 'average_roi', 'rental_price_monthly')[:5]
    )
    top_roi_properties = list(top_roi_properties_qs)

    upcoming_inspections = (
        PropertyInspection.objects.filter(next_inspection_date__isnull=False)
        .order_by('next_inspection_date')[:5]
    )

    total_properties = properties.count()
    active_properties = properties.filter(is_active=True).count()
    available_properties = properties.filter(status='available').count()

    context = {
        'total_properties': total_properties,
        'active_properties': active_properties,
        'available_properties': available_properties,
        'status_breakdown': status_breakdown,
        'type_distribution': type_distribution,
        'average_occupancy': round(average_occupancy, 2) if average_occupancy else 0,
        'average_roi': round(average_roi, 2) if average_roi else 0,
        'monthly_revenue': monthly_revenue,
        'top_roi_properties': top_roi_properties,
        'upcoming_inspections': upcoming_inspections,
        'total_revenue': float(PropertyRevenue.objects.aggregate(total=Sum('amount'))['total'] or 0),
        'total_expenses': float(PropertyExpense.objects.aggregate(total=Sum('amount'))['total'] or 0),
        'active_percentage': round((active_properties / total_properties) * 100, 1) if total_properties else 0,
        'available_percentage': round((available_properties / total_properties) * 100, 1) if total_properties else 0,
    }
    return render(request, 'properties/dashboard.html', context)


@login_required
def property_map(request):
    """Interactive map view for properties."""
    properties = (
        Property.objects.select_related('property_type', 'owner')
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
    )

    property_markers = [
        {
            'id': prop.pk,
            'code': prop.code,
            'title': prop.title,
            'type': prop.property_type.name,
            'owner': prop.owner.name,
            'status': prop.get_status_display(),
            'rent': float(prop.rental_price_monthly or 0),
            'city': prop.city,
            'latitude': float(prop.latitude),
            'longitude': float(prop.longitude),
            'url': request.build_absolute_uri(prop.get_absolute_url()) if hasattr(prop, 'get_absolute_url') else None,
        }
        for prop in properties
    ]

    import json
    
    context = {
        'property_markers': json.dumps(property_markers),
        'total_with_coordinates': properties.count(),
        'total_properties': Property.objects.count(),
    }
    return render(request, 'properties/map.html', context)

@login_required
def property_create(request):
    """Create new property"""
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_obj = form.save()
            messages.success(request, f'Property {property_obj.code} created successfully!')
            return redirect('properties:detail', pk=property_obj.pk)
    else:
        form = PropertyForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'properties/form.html', context)

@login_required
def property_update(request, pk):
    """Update existing property"""
    property_obj = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Property {property_obj.code} updated successfully!')
            return redirect('properties:detail', pk=property_obj.pk)
    else:
        form = PropertyForm(instance=property_obj)
    
    context = {
        'form': form,
        'property': property_obj,
        'action': 'Update'
    }
    return render(request, 'properties/form.html', context)

@login_required
def property_detail(request, pk):
    """Property detail view"""
    property_obj = get_object_or_404(
        Property.objects.select_related('property_type', 'owner'),
        pk=pk
    )
    
    images = property_obj.images.all()
    documents = property_obj.documents.select_related('uploaded_by').all()
    contracts = property_obj.contracts.select_related('client').all()
    valuations = property_obj.valuations.all()
    amenities = property_obj.amenities.all()
    inspections = property_obj.inspections.all()
    expenses = property_obj.expenses.all()
    revenues = property_obj.revenues.all()
    
    context = {
        'property': property_obj,
        'images': images,
        'documents': documents,
        'contracts': contracts,
        'valuations': valuations,
        'amenities': amenities,
        'inspections': inspections,
        'expenses': expenses,
        'revenues': revenues,
    }
    return render(request, 'properties/detail.html', context)

@login_required
def property_delete(request, pk):
    """Delete property"""
    property_obj = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        code = property_obj.code
        property_obj.delete()
        messages.success(request, f'Property {code} deleted successfully!')
        return redirect('properties:list')
    
    context = {'property': property_obj}
    return render(request, 'properties/confirm_delete.html', context)

# HTMX Partials

@login_required
def property_form_partial(request, pk=None):
    """HTMX partial for property form"""
    if pk:
        property_obj = get_object_or_404(Property, pk=pk)
        form = PropertyForm(instance=property_obj)
        action = 'Update'
    else:
        form = PropertyForm()
        action = 'Create'
    
    context = {
        'form': form,
        'property': property_obj if pk else None,
        'action': action
    }
    return render(request, 'properties/partials/form_partial.html', context)

@login_required
def property_row_partial(request, pk):
    """HTMX partial for property table row"""
    property_obj = get_object_or_404(Property, pk=pk)
    return render(request, 'properties/partials/row_partial.html', {
        'property': property_obj
    })

# Property Images

@login_required
def property_image_upload(request, property_pk):
    """Upload property image"""
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    if request.method == 'POST':
        form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.property = property_obj
            image.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect('properties:detail', pk=property_pk)
    else:
        form = PropertyImageForm()
    
    context = {'form': form, 'property': property_obj}
    return render(request, 'properties/image_form.html', context)

@login_required
def property_image_delete(request, pk):
    """Delete property image"""
    image = get_object_or_404(PropertyImage, pk=pk)
    property_pk = image.property.pk
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('properties:detail', pk=property_pk)
    
    return redirect('properties:detail', pk=property_pk)

# Property Documents

@login_required
def property_document_upload(request, property_pk):
    """Upload property document"""
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    if request.method == 'POST':
        form = PropertyDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.property = property_obj
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('properties:detail', pk=property_pk)
    else:
        form = PropertyDocumentForm()
    
    context = {'form': form, 'property': property_obj}
    return render(request, 'properties/document_form.html', context)

@login_required
def property_document_delete(request, pk):
    """Delete property document"""
    document = get_object_or_404(PropertyDocument, pk=pk)
    property_pk = document.property.pk
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('properties:detail', pk=property_pk)
    
    return redirect('properties:detail', pk=property_pk)


# Property Valuations


@login_required
def property_valuation_create(request, property_pk):
    """Create a valuation entry for a property."""
    property_obj = get_object_or_404(Property, pk=property_pk)

    if request.method == 'POST':
        form = PropertyValuationForm(request.POST, request.FILES)
        if form.is_valid():
            valuation = form.save(commit=False)
            valuation.property = property_obj
            valuation.save()
            messages.success(request, 'Valuation added successfully!')
            return redirect('properties:detail', pk=property_pk)
    else:
        form = PropertyValuationForm()

    context = {
        'form': form,
        'property': property_obj,
        'heading': 'Add Valuation',
        'action_label': 'Save Valuation',
    }
    return render(request, 'properties/related_form.html', context)


@login_required
def property_valuation_delete(request, pk):
    """Delete a valuation record."""
    valuation = get_object_or_404(PropertyValuation, pk=pk)
    property_pk = valuation.property.pk

    if request.method == 'POST':
        valuation.delete()
        messages.success(request, 'Valuation deleted successfully!')
        return redirect('properties:detail', pk=property_pk)

    context = {
        'object_name': str(valuation),
        'property': valuation.property,
        'cancel_url': 'properties:detail',
        'cancel_kwargs': {'pk': property_pk},
    }
    return render(request, 'properties/related_confirm_delete.html', context)


# Property Amenities


@login_required
def property_amenity_create(request, property_pk):
    """Create an amenity entry for a property."""
    property_obj = get_object_or_404(Property, pk=property_pk)

    if request.method == 'POST':
        form = PropertyAmenityForm(request.POST)
        if form.is_valid():
            amenity = form.save(commit=False)
            amenity.property = property_obj
            amenity.save()
            messages.success(request, 'Amenity added successfully!')
            return redirect('properties:detail', pk=property_pk)
    else:
        form = PropertyAmenityForm()

    context = {
        'form': form,
        'property': property_obj,
        'heading': 'Add Amenity',
        'action_label': 'Save Amenity',
    }
    return render(request, 'properties/related_form.html', context)


@login_required
def property_amenity_delete(request, pk):
    """Delete an amenity record."""
    amenity = get_object_or_404(PropertyAmenity, pk=pk)
    property_pk = amenity.property.pk

    if request.method == 'POST':
        amenity.delete()
        messages.success(request, 'Amenity deleted successfully!')
        return redirect('properties:detail', pk=property_pk)

    context = {
        'object_name': amenity.name,
        'property': amenity.property,
        'cancel_url': 'properties:detail',
        'cancel_kwargs': {'pk': property_pk},
    }
    return render(request, 'properties/related_confirm_delete.html', context)


# Property Inspections


@login_required
def property_inspection_create(request, property_pk):
    """Create an inspection record for a property."""
    property_obj = get_object_or_404(Property, pk=property_pk)

    if request.method == 'POST':
        form = PropertyInspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.property = property_obj
            inspection.save()
            messages.success(request, 'Inspection recorded successfully!')
            return redirect('properties:detail', pk=property_pk)
    else:
        form = PropertyInspectionForm()

    context = {
        'form': form,
        'property': property_obj,
        'heading': 'Record Inspection',
        'action_label': 'Save Inspection',
    }
    return render(request, 'properties/related_form.html', context)


@login_required
def property_inspection_delete(request, pk):
    """Delete an inspection record."""
    inspection = get_object_or_404(PropertyInspection, pk=pk)
    property_pk = inspection.property.pk

    if request.method == 'POST':
        inspection.delete()
        messages.success(request, 'Inspection deleted successfully!')
        return redirect('properties:detail', pk=property_pk)

    context = {
        'object_name': f"Inspection on {inspection.inspection_date}",
        'property': inspection.property,
        'cancel_url': 'properties:detail',
        'cancel_kwargs': {'pk': property_pk},
    }
    return render(request, 'properties/related_confirm_delete.html', context)


# Property Expenses


@login_required
def property_expense_create(request, property_pk):
    """Create an expense record for a property."""
    property_obj = get_object_or_404(Property, pk=property_pk)

    if request.method == 'POST':
        form = PropertyExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.property = property_obj
            expense.save()
            messages.success(request, 'Expense recorded successfully!')
            return redirect('properties:detail', pk=property_pk)
    else:
        form = PropertyExpenseForm()

    context = {
        'form': form,
        'property': property_obj,
        'heading': 'Record Expense',
        'action_label': 'Save Expense',
    }
    return render(request, 'properties/related_form.html', context)


@login_required
def property_expense_delete(request, pk):
    """Delete an expense record."""
    expense = get_object_or_404(PropertyExpense, pk=pk)
    property_pk = expense.property.pk

    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('properties:detail', pk=property_pk)

    context = {
        'object_name': f"Expense {expense.get_expense_type_display()} on {expense.expense_date}",
        'property': expense.property,
        'cancel_url': 'properties:detail',
        'cancel_kwargs': {'pk': property_pk},
    }
    return render(request, 'properties/related_confirm_delete.html', context)


# Property Revenues


@login_required
def property_revenue_create(request, property_pk):
    """Create a revenue record for a property."""
    property_obj = get_object_or_404(Property, pk=property_pk)

    if request.method == 'POST':
        form = PropertyRevenueForm(request.POST, property_instance=property_obj)
        if form.is_valid():
            revenue = form.save(commit=False)
            revenue.property = property_obj
            revenue.save()
            messages.success(request, 'Revenue recorded successfully!')
            return redirect('properties:detail', pk=property_pk)
    else:
        form = PropertyRevenueForm(property_instance=property_obj)

    context = {
        'form': form,
        'property': property_obj,
        'heading': 'Record Revenue',
        'action_label': 'Save Revenue',
    }
    return render(request, 'properties/related_form.html', context)


@login_required
def property_revenue_delete(request, pk):
    """Delete a revenue record."""
    revenue = get_object_or_404(PropertyRevenue, pk=pk)
    property_pk = revenue.property.pk

    if request.method == 'POST':
        revenue.delete()
        messages.success(request, 'Revenue deleted successfully!')
        return redirect('properties:detail', pk=property_pk)

    context = {
        'object_name': f"Revenue {revenue.get_revenue_type_display()} on {revenue.revenue_date}",
        'property': revenue.property,
        'cancel_url': 'properties:detail',
        'cancel_kwargs': {'pk': property_pk},
    }
    return render(request, 'properties/related_confirm_delete.html', context)

# Property Types

@login_required
def property_type_list(request):
    """List all property types"""
    property_types = PropertyType.objects.all()
    context = {'property_types': property_types}
    return render(request, 'properties/type_list.html', context)

@login_required
def property_type_create(request):
    """Create property type"""
    if request.method == 'POST':
        form = PropertyTypeForm(request.POST)
        if form.is_valid():
            property_type = form.save()
            messages.success(request, f'Property type {property_type.name} created!')
            return redirect('properties:type_list')
    else:
        form = PropertyTypeForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'properties/type_form.html', context)

@login_required
def property_type_update(request, pk):
    """Update property type"""
    property_type = get_object_or_404(PropertyType, pk=pk)
    
    if request.method == 'POST':
        form = PropertyTypeForm(request.POST, instance=property_type)
        if form.is_valid():
            form.save()
            messages.success(request, f'Property type {property_type.name} updated!')
            return redirect('properties:type_list')
    else:
        form = PropertyTypeForm(instance=property_type)
    
    context = {'form': form, 'property_type': property_type, 'action': 'Update'}
    return render(request, 'properties/type_form.html', context)

@login_required
def property_type_delete(request, pk):
    """Delete property type"""
    property_type = get_object_or_404(PropertyType, pk=pk)
    
    if request.method == 'POST':
        name = property_type.name
        property_type.delete()
        messages.success(request, f'Property type {name} deleted!')
        return redirect('properties:type_list')
    
    context = {'property_type': property_type}
    return render(request, 'properties/type_confirm_delete.html', context)

# AJAX/API Views

@login_required
def property_status_toggle(request, pk):
    """Toggle property active status via AJAX"""
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, pk=pk)
        property_obj.is_active = not property_obj.is_active
        property_obj.save()
        
        return JsonResponse({
            'success': True,
            'is_active': property_obj.is_active,
            'message': f'Property {property_obj.code} is now {"active" if property_obj.is_active else "inactive"}'
        })
    
    return JsonResponse({'success': False}, status=400)


# Advanced Views - Phase 2

@login_required
def property_gallery(request, pk):
    """Professional image gallery view for a property."""
    property_obj = get_object_or_404(Property, pk=pk)
    images = property_obj.images.all().order_by('order', '-uploaded_at')
    
    # Primary image first
    primary_image = images.filter(is_primary=True).first()
    other_images = images.exclude(is_primary=True) if primary_image else images
    
    context = {
        'property': property_obj,
        'primary_image': primary_image,
        'images': other_images,
        'total_images': images.count(),
    }
    return render(request, 'properties/gallery.html', context)


@login_required
def property_financial_report(request, pk):
    """Comprehensive financial report for a property."""
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Calculate date ranges
    today = timezone.now().date()
    current_year_start = today.replace(month=1, day=1)
    last_year_start = current_year_start.replace(year=current_year_start.year - 1)
    last_year_end = current_year_start - timedelta(days=1)
    
    # Current year financial data
    current_year_revenues = PropertyRevenue.objects.filter(
        property=property_obj,
        revenue_date__gte=current_year_start
    )
    current_year_expenses = PropertyExpense.objects.filter(
        property=property_obj,
        expense_date__gte=current_year_start
    )
    
    # Last year financial data
    last_year_revenues = PropertyRevenue.objects.filter(
        property=property_obj,
        revenue_date__gte=last_year_start,
        revenue_date__lte=last_year_end
    )
    last_year_expenses = PropertyExpense.objects.filter(
        property=property_obj,
        expense_date__gte=last_year_start,
        expense_date__lte=last_year_end
    )
    
    # All-time totals
    total_revenue = PropertyRevenue.objects.filter(property=property_obj).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_expenses = PropertyExpense.objects.filter(property=property_obj).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Current year totals
    current_year_revenue_total = current_year_revenues.aggregate(total=Sum('amount'))['total'] or 0
    current_year_expense_total = current_year_expenses.aggregate(total=Sum('amount'))['total'] or 0
    current_year_profit = current_year_revenue_total - current_year_expense_total
    
    # Last year totals
    last_year_revenue_total = last_year_revenues.aggregate(total=Sum('amount'))['total'] or 0
    last_year_expense_total = last_year_expenses.aggregate(total=Sum('amount'))['total'] or 0
    last_year_profit = last_year_revenue_total - last_year_expense_total
    
    # ROI Calculation
    investment = property_obj.purchase_price or property_obj.market_value or 0
    if investment > 0:
        current_roi = (float(current_year_profit) / float(investment)) * 100
        lifetime_roi = ((float(total_revenue) - float(total_expenses)) / float(investment)) * 100
    else:
        current_roi = 0
        lifetime_roi = 0
    
    # Monthly breakdown for current year
    monthly_data = []
    for month in range(1, 13):
        month_revenues = current_year_revenues.filter(
            revenue_date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expenses = current_year_expenses.filter(
            expense_date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month,
            'revenue': float(month_revenues),
            'expense': float(month_expenses),
            'profit': float(month_revenues - month_expenses),
        })
    
    # Expense breakdown by type
    expense_by_type = PropertyExpense.objects.filter(
        property=property_obj,
        expense_date__gte=current_year_start
    ).values('expense_type').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Revenue breakdown by type
    revenue_by_type = PropertyRevenue.objects.filter(
        property=property_obj,
        revenue_date__gte=current_year_start
    ).values('revenue_type').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'property': property_obj,
        'total_revenue': float(total_revenue),
        'total_expenses': float(total_expenses),
        'total_profit': float(total_revenue - total_expenses),
        'current_year_revenue': float(current_year_revenue_total),
        'current_year_expense': float(current_year_expense_total),
        'current_year_profit': float(current_year_profit),
        'last_year_revenue': float(last_year_revenue_total),
        'last_year_expense': float(last_year_expense_total),
        'last_year_profit': float(last_year_profit),
        'current_roi': round(current_roi, 2),
        'lifetime_roi': round(lifetime_roi, 2),
        'monthly_data': monthly_data,
        'expense_by_type': expense_by_type,
        'revenue_by_type': revenue_by_type,
        'current_year': today.year,
        'last_year': today.year - 1,
    }
    return render(request, 'properties/financial_report.html', context)


@login_required
def property_comparison(request):
    """Compare multiple properties side by side."""
    # Get selected property IDs from GET parameters
    property_ids = request.GET.getlist('properties')
    
    if property_ids:
        properties = Property.objects.filter(pk__in=property_ids).select_related(
            'property_type', 'owner'
        )[:4]  # Limit to 4 properties for comparison
    else:
        properties = []
    
    # All properties for selection
    all_properties = Property.objects.filter(is_active=True).select_related(
        'property_type', 'owner'
    ).order_by('code')
    
    context = {
        'properties': properties,
        'all_properties': all_properties,
        'selected_ids': [int(pid) for pid in property_ids],
    }
    return render(request, 'properties/comparison.html', context)


@login_required
def property_occupancy_history(request, pk):
    """View occupancy history and timeline for a property."""
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Get all contracts for this property
    from apps.contracts.models import Contract
    contracts = Contract.objects.filter(
        property=property_obj
    ).select_related('client').order_by('-start_date')
    
    # Calculate occupancy metrics
    total_days = 0
    occupied_days = 0
    
    for contract in contracts:
        start = contract.start_date
        end = contract.end_date or timezone.now().date()
        duration = (end - start).days
        total_days += duration
        if contract.status in ['active', 'expired']:
            occupied_days += duration
    
    if total_days > 0:
        occupancy_rate = (occupied_days / total_days) * 100
    else:
        occupancy_rate = 0
    
    # Calculate vacancy periods
    vacancy_periods = []
    sorted_contracts = list(contracts.order_by('start_date'))
    
    for i, contract in enumerate(sorted_contracts):
        if i < len(sorted_contracts) - 1:
            next_contract = sorted_contracts[i + 1]
            end_date = contract.end_date or timezone.now().date()
            
            if end_date < next_contract.start_date:
                vacancy_days = (next_contract.start_date - end_date).days
                vacancy_periods.append({
                    'start': end_date,
                    'end': next_contract.start_date,
                    'days': vacancy_days,
                })
    
    context = {
        'property': property_obj,
        'contracts': contracts,
        'occupancy_rate': round(occupancy_rate, 2),
        'total_contracts': contracts.count(),
        'active_contracts': contracts.filter(status='active').count(),
        'vacancy_periods': vacancy_periods,
        'total_vacancy_days': sum(v['days'] for v in vacancy_periods),
    }
    return render(request, 'properties/occupancy_history.html', context)


@login_required
def property_maintenance_history(request, pk):
    """Complete maintenance history for a property."""
    property_obj = get_object_or_404(Property, pk=pk)
    
    from apps.maintenance.models import MaintenanceRequest
    maintenance_requests = MaintenanceRequest.objects.filter(
        property=property_obj
    ).select_related('category', 'reported_by', 'assigned_to').order_by('-request_date')
    
    # Statistics
    total_requests = maintenance_requests.count()
    completed = maintenance_requests.filter(status='completed').count()
    pending = maintenance_requests.filter(status='pending').count()
    in_progress = maintenance_requests.filter(status='in_progress').count()
    
    total_cost = maintenance_requests.aggregate(
        estimated=Sum('estimated_cost'),
        actual=Sum('actual_cost')
    )
    
    # Cost by category
    cost_by_category = maintenance_requests.values(
        'category__name'
    ).annotate(
        total=Sum('actual_cost')
    ).order_by('-total')
    
    context = {
        'property': property_obj,
        'maintenance_requests': maintenance_requests[:20],  # Latest 20
        'total_requests': total_requests,
        'completed_count': completed,
        'pending_count': pending,
        'in_progress_count': in_progress,
        'completion_rate': round((completed / total_requests * 100), 2) if total_requests > 0 else 0,
        'total_estimated_cost': total_cost['estimated'] or 0,
        'total_actual_cost': total_cost['actual'] or 0,
        'cost_by_category': cost_by_category,
    }
    return render(request, 'properties/maintenance_history.html', context)
