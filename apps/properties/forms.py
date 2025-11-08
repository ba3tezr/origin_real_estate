"""
Forms for Properties app
"""
from django import forms
from django.utils import timezone
from .models import (
    PropertyType,
    Property,
    PropertyDocument,
    PropertyImage,
    PropertyValuation,
    PropertyAmenity,
    PropertyInspection,
    PropertyExpense,
    PropertyRevenue,
)
from apps.contracts.models import Contract


def _coerce_optional_bool(value):
    """Convert string form values to optional boolean."""
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    value_str = str(value).lower()
    if value_str == 'true':
        return True
    if value_str == 'false':
        return False
    return None

class PropertyTypeForm(forms.ModelForm):
    """Form for PropertyType model"""
    
    class Meta:
        model = PropertyType
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PropertyForm(forms.ModelForm):
    """Form for Property model"""
    
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'owner', 'address', 'city',
            'district', 'postal_code', 'latitude', 'longitude',
            'virtual_tour_url', 'video_url',
            'area_sqm', 'bedrooms', 'bathrooms', 'floors', 'floor_number',
            'total_floors', 'parking_spaces', 'year_built', 'is_furnished',
            'pets_allowed', 'energy_rating',
            'rental_price_monthly', 'purchase_price', 'market_value',
            'occupancy_rate', 'average_roi',
            'status', 'is_active', 'description', 'notes',
            'last_renovation_date',
            'has_elevator', 'has_garden', 'has_pool', 'has_security'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'virtual_tour_url': forms.URLInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'area_sqm': forms.NumberInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'parking_spaces': forms.NumberInput(attrs={'class': 'form-control'}),
            'year_built': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_furnished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pets_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'energy_rating': forms.TextInput(attrs={'class': 'form-control'}),
            'rental_price_monthly': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'market_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'occupancy_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'average_roi': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'last_renovation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'has_elevator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_garden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        """Assign auto-generated code when creating a property."""
        property_obj = super().save(commit=False)
        if not property_obj.code:
            property_obj.code = self._generate_unique_code()
        if commit:
            property_obj.save()
            self.save_m2m()
        return property_obj

    @staticmethod
    def _generate_unique_code():
        """Generate a unique property code with yearly prefix."""
        year = timezone.now().year
        prefix = f"PROP-{year}-"
        last_code = (
            Property.objects
            .filter(code__startswith=prefix)
            .order_by('-code')
            .values_list('code', flat=True)
            .first()
        )
        if last_code:
            try:
                last_number = int(last_code.rsplit('-', 1)[-1])
            except (ValueError, AttributeError):
                last_number = 0
        else:
            last_number = 0

        next_number = last_number + 1
        new_code = f"{prefix}{next_number:04d}"
        while Property.objects.filter(code=new_code).exists():
            next_number += 1
            new_code = f"{prefix}{next_number:04d}"
        return new_code

class PropertyDocumentForm(forms.ModelForm):
    """Form for PropertyDocument model"""
    
    class Meta:
        model = PropertyDocument
        fields = ['title', 'document_type', 'file', 'description', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class PropertyImageForm(forms.ModelForm):
    """Form for PropertyImage model"""
    
    class Meta:
        model = PropertyImage
        fields = ['image', 'title', 'caption', 'description', 'is_primary', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PropertyValuationForm(forms.ModelForm):
    """Form for PropertyValuation model"""

    class Meta:
        model = PropertyValuation
        fields = [
            'valuation_date', 'valuation_amount', 'valuation_type',
            'valuator_name', 'notes', 'document'
        ]
        widgets = {
            'valuation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valuation_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valuation_type': forms.Select(attrs={'class': 'form-select'}),
            'valuator_name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PropertyAmenityForm(forms.ModelForm):
    """Form for PropertyAmenity model"""

    class Meta:
        model = PropertyAmenity
        fields = ['amenity_type', 'name', 'description', 'is_available']
        widgets = {
            'amenity_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PropertyInspectionForm(forms.ModelForm):
    """Form for PropertyInspection model"""

    class Meta:
        model = PropertyInspection
        fields = [
            'inspection_date', 'inspection_type', 'inspector_name',
            'overall_condition', 'notes', 'recommendations',
            'next_inspection_date', 'document'
        ]
        widgets = {
            'inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inspection_type': forms.Select(attrs={'class': 'form-select'}),
            'inspector_name': forms.TextInput(attrs={'class': 'form-control'}),
            'overall_condition': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PropertyExpenseForm(forms.ModelForm):
    """Form for PropertyExpense model"""

    class Meta:
        model = PropertyExpense
        fields = [
            'expense_date', 'expense_type', 'amount', 'vendor',
            'description', 'receipt', 'is_recurring', 'recurrence_frequency'
        ]
        widgets = {
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expense_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence_frequency': forms.Select(attrs={'class': 'form-select'}),
        }


class PropertyRevenueForm(forms.ModelForm):
    """Form for PropertyRevenue model"""

    class Meta:
        model = PropertyRevenue
        fields = ['revenue_date', 'revenue_type', 'amount', 'source', 'description', 'contract']
        widgets = {
            'revenue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'revenue_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contract': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        property_instance = kwargs.pop('property_instance', None)
        super().__init__(*args, **kwargs)
        if property_instance:
            self.fields['contract'].queryset = (
                Contract.objects.filter(property=property_instance)
            )
        else:
            self.fields['contract'].queryset = Contract.objects.none()

class PropertySearchForm(forms.Form):
    """Form for searching/filtering properties"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by code, title, address...'
        })
    )
    
    property_type = forms.ModelChoiceField(
        queryset=PropertyType.objects.filter(is_active=True),
        required=False,
        empty_label='All Types',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Property.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    
    min_rent = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min rent', 'step': '0.01'})
    )
    
    max_rent = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max rent', 'step': '0.01'})
    )
    
    bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min bedrooms'})
    )
    
    is_furnished = forms.TypedChoiceField(
        required=False,
        choices=[('', 'Any'), ('true', 'Furnished'), ('false', 'Unfurnished')],
        coerce=_coerce_optional_bool,
        empty_value=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
