"""
Forms for Clients app
"""
from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    """Form for Client model"""
    
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'address', 'city',
            'country', 'national_id', 'occupation', 'employer',
            'monthly_income', 'emergency_contact_name',
            'emergency_contact_phone', 'notes', 'is_active',
            'credit_score'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'occupation': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'employer': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_income': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'emergency_contact_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'emergency_contact_phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'notes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'credit_score': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
        }


class ClientSearchForm(forms.Form):
    """Form for searching/filtering clients"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, phone...'
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )
    
    is_active = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('true', 'Active'), ('false', 'Inactive')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
