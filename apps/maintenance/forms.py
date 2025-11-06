"""Forms for Maintenance app"""
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.properties.models import Property

from .models import (
    MaintenanceAttachment,
    MaintenanceCategory,
    MaintenanceRequest,
    MaintenanceSchedule,
)

User = get_user_model()


class MaintenanceRequestForm(forms.ModelForm):
    """Form for creating and updating maintenance requests."""

    class Meta:
        model = MaintenanceRequest
        fields = [
            'request_number', 'property', 'category', 'title', 'description',
            'priority', 'status', 'assigned_to', 'scheduled_date', 'completed_date',
            'estimated_cost', 'actual_cost', 'notes', 'resolution_notes'
        ]
        widgets = {
            'request_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left blank'}
            ),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'completed_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'actual_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['request_number'].required = False
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = User.objects.order_by('first_name', 'last_name')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.request_number:
            instance.request_number = self._generate_request_number()
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    @staticmethod
    def _generate_request_number():
        prefix = f"MAINT-{timezone.now().year}-"
        last_number = (
            MaintenanceRequest.objects.filter(request_number__startswith=prefix)
            .order_by('-request_number')
            .values_list('request_number', flat=True)
            .first()
        )
        if last_number:
            try:
                counter = int(last_number.rsplit('-', 1)[-1]) + 1
            except (ValueError, AttributeError):
                counter = 1
        else:
            counter = 1
        code = f"{prefix}{counter:04d}"
        while MaintenanceRequest.objects.filter(request_number=code).exists():
            counter += 1
            code = f"{prefix}{counter:04d}"
        return code


class MaintenanceSearchForm(forms.Form):
    """Form for searching maintenance requests."""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Search by request number, title, property...'}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + list(MaintenanceRequest.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + list(MaintenanceRequest.PRIORITY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=MaintenanceCategory.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    property = forms.ModelChoiceField(
        required=False,
        queryset=Property.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    assigned_to = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    request_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    request_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    scheduled_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    scheduled_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = MaintenanceCategory.objects.order_by('name')
        self.fields['property'].queryset = Property.objects.order_by('title')
        self.fields['assigned_to'].queryset = User.objects.order_by('first_name', 'last_name')


class MaintenanceAttachmentForm(forms.ModelForm):
    """Form for uploading maintenance attachments."""

    class Meta:
        model = MaintenanceAttachment
        fields = ['file', 'attachment_type', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'attachment_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MaintenanceScheduleForm(forms.ModelForm):
    """Form for preventive maintenance schedules."""

    class Meta:
        model = MaintenanceSchedule
        fields = [
            'property', 'category', 'title', 'description', 'frequency',
            'last_service_date', 'next_service_date', 'assigned_to',
            'estimated_cost', 'is_active', 'notes'
        ]
        widgets = {
            'property': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'last_service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = User.objects.order_by('first_name', 'last_name')
