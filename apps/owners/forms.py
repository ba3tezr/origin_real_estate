"""
Forms for Owners app
"""
from django import forms
from .models import Owner


class OwnerForm(forms.ModelForm):
    """Form for creating and updating owners"""
    
    class Meta:
        model = Owner
        fields = [
            'name', 'national_id', 'phone', 'email',
            'address', 'city', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OwnerSearchForm(forms.Form):
    """Form for searching owners"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, phone, email...'
        })
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=[('', 'All'), ('true', 'Active'), ('false', 'Inactive')],
            attrs={'class': 'form-select'}
        )
    )
