"""Views for Maintenance app"""
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Q, Sum, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    MaintenanceAttachmentForm,
    MaintenanceRequestForm,
    MaintenanceScheduleForm,
    MaintenanceSearchForm,
)
from .models import MaintenanceAttachment, MaintenanceRequest, MaintenanceSchedule, MaintenanceCategory


@login_required
def maintenance_list(request):
    """Advanced list of maintenance requests with filtering and insights."""

    queryset = MaintenanceRequest.objects.select_related('property', 'category', 'assigned_to')

    search_form = MaintenanceSearchForm(request.GET or None)
    if search_form.is_valid():
        data = search_form.cleaned_data

        if data.get('search'):
            term = data['search']
            queryset = queryset.filter(
                Q(request_number__icontains=term)
                | Q(title__icontains=term)
                | Q(description__icontains=term)
                | Q(property__title__icontains=term)
                | Q(property__code__icontains=term)
            )

        if data.get('status'):
            queryset = queryset.filter(status=data['status'])

        if data.get('priority'):
            queryset = queryset.filter(priority=data['priority'])

        if data.get('category'):
            queryset = queryset.filter(category=data['category'])

        if data.get('property'):
            queryset = queryset.filter(property=data['property'])

        if data.get('assigned_to'):
            queryset = queryset.filter(assigned_to=data['assigned_to'])

        if data.get('request_from'):
            queryset = queryset.filter(request_date__date__gte=data['request_from'])

        if data.get('request_to'):
            queryset = queryset.filter(request_date__date__lte=data['request_to'])

        if data.get('scheduled_from'):
            queryset = queryset.filter(scheduled_date__date__gte=data['scheduled_from'])

        if data.get('scheduled_to'):
            queryset = queryset.filter(scheduled_date__date__lte=data['scheduled_to'])

        if data.get('overdue_only'):
            now = timezone.now()
            queryset = queryset.filter(
                status__in=['pending', 'in_progress'],
                scheduled_date__isnull=False,
                scheduled_date__lt=now,
            )

    sort_option = request.GET.get('sort', 'recent')
    priority_order = Case(
        When(priority='urgent', then=0),
        When(priority='high', then=1),
        When(priority='medium', then=2),
        default=3,
        output_field=IntegerField(),
    )

    sort_mapping = {
        'recent': ('-request_date',),
        'oldest': ('request_date',),
        'scheduled_soon': ('scheduled_date', '-priority'),
        'scheduled_latest': ('-scheduled_date',),
        'priority': ('priority_order', '-request_date'),
        'cost_high': ('-estimated_cost', '-request_date'),
        'cost_low': ('estimated_cost', 'request_date'),
    }

    if sort_option == 'priority':
        queryset = queryset.annotate(priority_order=priority_order).order_by(*sort_mapping['priority'])
    else:
        queryset = queryset.order_by(*sort_mapping.get(sort_option, ('-request_date',)))

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)
    pagination_querystring = query_params.urlencode()

    all_requests = MaintenanceRequest.objects.all()
    now = timezone.now()

    status_summary = list(
        all_requests.values('status').annotate(total=Count('id')).order_by('-total')
    )
    priority_summary = list(
        all_requests.values('priority').annotate(total=Count('id')).order_by('-total')
    )
    overdue_count = all_requests.filter(
        status__in=['pending', 'in_progress'],
        scheduled_date__isnull=False,
        scheduled_date__lt=now,
    ).count()
    upcoming_within_week = all_requests.filter(
        scheduled_date__isnull=False,
        scheduled_date__gte=now,
        scheduled_date__lte=now + timedelta(days=7),
    ).count()

    filtered_estimated_total = queryset.aggregate(total=Sum('estimated_cost'))['total'] or 0
    filtered_actual_total = queryset.aggregate(total=Sum('actual_cost'))['total'] or 0

    context = {
        'requests': page_obj,
        'search_form': search_form,
        'sort_option': sort_option,
        'filter_applied': any(v for k, v in request.GET.items() if k not in ['page']),
        'pagination_querystring': pagination_querystring,
        'total_count': all_requests.count(),
        'pending_count': all_requests.filter(status='pending').count(),
        'in_progress_count': all_requests.filter(status='in_progress').count(),
        'completed_count': all_requests.filter(status='completed').count(),
        'overdue_count': overdue_count,
        'upcoming_count': upcoming_within_week,
        'status_summary': status_summary,
        'priority_summary': priority_summary,
        'filtered_estimated_total': filtered_estimated_total,
        'filtered_actual_total': filtered_actual_total,
        'total_requests': all_requests.count(),
        'total_cost': filtered_actual_total,
        'categories': MaintenanceCategory.objects.filter(is_active=True),
    }
    return render(request, 'maintenance/list.html', context)


@login_required
def maintenance_detail(request, pk):
    """Detail view for a maintenance request."""

    maintenance = get_object_or_404(
        MaintenanceRequest.objects.select_related(
            'property', 'category', 'assigned_to', 'reported_by'
        ),
        pk=pk,
    )

    attachments = maintenance.attachments.select_related('uploaded_by').order_by('-uploaded_at')
    property_schedules = MaintenanceSchedule.objects.filter(
        property=maintenance.property
    ).order_by('next_service_date')[:5]

    cost_delta = None
    if maintenance.estimated_cost and maintenance.actual_cost:
        cost_delta = maintenance.actual_cost - maintenance.estimated_cost

    timeline = [
        {
            'label': 'Reported',
            'timestamp': maintenance.request_date,
            'description': maintenance.title,
        }
    ]
    if maintenance.scheduled_date:
        timeline.append(
            {
                'label': 'Scheduled',
                'timestamp': maintenance.scheduled_date,
                'description': 'Work scheduled',
            }
        )
    if maintenance.completed_date:
        timeline.append(
            {
                'label': 'Completed',
                'timestamp': maintenance.completed_date,
                'description': maintenance.resolution_notes or 'Completed',
            }
        )

    related_requests = (
        MaintenanceRequest.objects.filter(property=maintenance.property)
        .exclude(pk=maintenance.pk)
        .order_by('-request_date')[:5]
    )

    context = {
        'maintenance': maintenance,
        'attachments': attachments,
        'schedules': property_schedules,
        'attachment_form': MaintenanceAttachmentForm(),
        'timeline': timeline,
        'cost_delta': cost_delta,
        'related_requests': related_requests,
    }
    return render(request, 'maintenance/detail.html', context)


@login_required
def maintenance_create(request):
    """Create new maintenance request."""

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.reported_by = request.user
            if maintenance.status == 'completed' and not maintenance.completed_date:
                maintenance.completed_date = timezone.now()
            maintenance.save()
            form.save_m2m()
            messages.success(request, f'Request {maintenance.request_number} created!')
            return redirect('maintenance:detail', pk=maintenance.pk)
    else:
        form = MaintenanceRequestForm()

    context = {'form': form, 'action': 'Create', 'maintenance': None}
    return render(request, 'maintenance/form.html', context)


@login_required
def maintenance_update(request, pk):
    """Update existing maintenance request."""

    maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=maintenance)
        if form.is_valid():
            maintenance = form.save(commit=False)
            if maintenance.status == 'completed' and not maintenance.completed_date:
                maintenance.completed_date = timezone.now()
            if maintenance.status != 'completed':
                maintenance.completed_date = None
            maintenance.save()
            form.save_m2m()
            messages.success(request, f'Request {maintenance.request_number} updated!')
            return redirect('maintenance:detail', pk=maintenance.pk)
    else:
        form = MaintenanceRequestForm(instance=maintenance)

    context = {'form': form, 'maintenance': maintenance, 'action': 'Update'}
    return render(request, 'maintenance/form.html', context)


@login_required
def maintenance_delete(request, pk):
    """Delete maintenance request."""

    maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

    if request.method == 'POST':
        number = maintenance.request_number
        maintenance.delete()
        messages.success(request, f'Request {number} deleted!')
        return redirect('maintenance:list')

    context = {'maintenance': maintenance}
    return render(request, 'maintenance/confirm_delete.html', context)


@login_required
def maintenance_attachment_create(request, pk):
    """Upload an attachment for a maintenance request."""

    maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

    if request.method == 'POST':
        form = MaintenanceAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.maintenance_request = maintenance
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, 'Attachment uploaded successfully!')
            return redirect('maintenance:detail', pk=maintenance.pk)
    else:
        form = MaintenanceAttachmentForm()

    context = {
        'form': form,
        'maintenance': maintenance,
        'heading': 'Upload Attachment',
        'action_label': 'Upload',
    }
    return render(request, 'maintenance/related_form.html', context)


@login_required
def maintenance_attachment_delete(request, pk):
    """Delete a maintenance attachment."""

    attachment = get_object_or_404(MaintenanceAttachment, pk=pk)
    maintenance = attachment.maintenance_request

    if request.method == 'POST':
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully!')
        return redirect('maintenance:detail', pk=maintenance.pk)

    context = {
        'maintenance': maintenance,
        'object_name': attachment.description or attachment.file.name,
    }
    return render(request, 'maintenance/related_confirm_delete.html', context)


@login_required
def maintenance_schedule_create(request, pk):
    """Create a preventive maintenance schedule for the request's property."""

    maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

    if request.method == 'POST':
        form = MaintenanceScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.property = maintenance.property
            schedule.save()
            messages.success(request, 'Maintenance schedule created!')
            return redirect('maintenance:detail', pk=maintenance.pk)
    else:
        form = MaintenanceScheduleForm(initial={'property': maintenance.property})

    context = {
        'form': form,
        'maintenance': maintenance,
        'heading': 'Create Schedule',
        'action_label': 'Save Schedule',
    }
    return render(request, 'maintenance/related_form.html', context)


@login_required
def maintenance_schedule_update(request, pk):
    """Update a maintenance schedule."""

    schedule = get_object_or_404(MaintenanceSchedule, pk=pk)
    related_request = schedule.property.maintenance_requests.order_by('-request_date').first()

    if request.method == 'POST':
        form = MaintenanceScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance schedule updated!')
            if related_request:
                return redirect('maintenance:detail', pk=related_request.pk)
            return redirect('maintenance:list')
    else:
        form = MaintenanceScheduleForm(instance=schedule)

    context = {
        'form': form,
        'maintenance': related_request,
        'heading': 'Update Schedule',
        'action_label': 'Save Changes',
    }
    return render(request, 'maintenance/related_form.html', context)


@login_required
def maintenance_schedule_delete(request, pk):
    """Delete a maintenance schedule."""

    schedule = get_object_or_404(MaintenanceSchedule, pk=pk)
    related_request = schedule.property.maintenance_requests.order_by('-request_date').first()

    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Maintenance schedule removed!')
        if related_request:
            return redirect('maintenance:detail', pk=related_request.pk)
        return redirect('maintenance:list')

    context = {
        'maintenance': related_request,
        'object_name': schedule.title,
    }
    return render(request, 'maintenance/related_confirm_delete.html', context)
