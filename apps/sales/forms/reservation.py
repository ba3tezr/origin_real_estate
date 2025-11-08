from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from apps.sales.models import PropertyReservation
from apps.properties.models import Property
from apps.sales.models import Buyer


class PropertyReservationForm(forms.ModelForm):
    """
    Form for creating and updating property reservations
    """
    
    class Meta:
        model = PropertyReservation
        fields = [
            'property', 'buyer', 'expiry_date',
            'reservation_amount', 'payment_method', 'payment_reference',
            'notes'
        ]
        
        widgets = {
            'property': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'buyer': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'reservation_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': True
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'payment_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Transaction Reference'),
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Additional Notes')
            }),
        }
        
        labels = {
            'property': _('Property'),
            'buyer': _('Buyer'),
            'expiry_date': _('Expiry Date'),
            'reservation_amount': _('Reservation Amount'),
            'payment_method': _('Payment Method'),
            'payment_reference': _('Payment Reference'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter only available properties for sale
        self.fields['property'].queryset = Property.objects.filter(
            status='available',
            is_for_sale=True
        ) if hasattr(Property, 'is_for_sale') else Property.objects.filter(status='available')
        
        # Filter only qualified and active buyers
        self.fields['buyer'].queryset = Buyer.objects.filter(
            is_qualified=True,
            is_active=True
        )
        
        # Set default expiry date to 7 days from now
        if not self.instance.pk:
            self.fields['expiry_date'].initial = (timezone.now() + timedelta(days=7)).date()
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date <= timezone.now().date():
            raise forms.ValidationError(_('Expiry date must be in the future'))
        return expiry_date
    
    def clean_reservation_amount(self):
        amount = self.cleaned_data.get('reservation_amount')
        if amount and amount <= 0:
            raise forms.ValidationError(_('Reservation amount must be greater than zero'))
        return amount


class ReservationCancelForm(forms.Form):
    """
    Form for cancelling a reservation
    """
    cancellation_reason = forms.CharField(
        label=_('Cancellation Reason'),
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Please provide a reason for cancellation')
        })
    )
