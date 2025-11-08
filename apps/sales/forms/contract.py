from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from apps.sales.models import SalesContract, SalesPayment
from apps.properties.models import Property
from apps.sales.models import Buyer
from apps.owners.models import Owner


class SalesContractForm(forms.ModelForm):
    """
    Form for creating and updating sales contracts
    """
    
    class Meta:
        model = SalesContract
        fields = [
            'property', 'buyer', 'seller',
            'sale_price', 'down_payment', 'financed_amount',
            'has_financing', 'financing_institution', 'financing_percentage', 'financing_years',
            'contract_date', 'expected_handover_date',
            'has_installments', 'number_of_installments', 'installment_frequency',
            'sold_as_is', 'includes_furniture', 'furniture_value',
            'title_deed_number', 'notary_name', 'lawyer_name',
            'terms_and_conditions', 'special_conditions',
            'has_agent', 'agent_name', 'agent_commission_percentage',
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
            'seller': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': True
            }),
            'down_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': True
            }),
            'financed_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'has_financing': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'financing_institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Bank Name')
            }),
            'financing_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'financing_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'contract_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'expected_handover_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'has_installments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'number_of_installments': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'installment_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sold_as_is': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'includes_furniture': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'furniture_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'title_deed_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Title Deed Number')
            }),
            'notary_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Notary Name')
            }),
            'lawyer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Lawyer Name')
            }),
            'terms_and_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Terms and Conditions')
            }),
            'special_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Special Conditions')
            }),
            'has_agent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'agent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Agent Name')
            }),
            'agent_commission_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
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
            'seller': _('Seller'),
            'sale_price': _('Sale Price'),
            'down_payment': _('Down Payment'),
            'financed_amount': _('Financed Amount'),
            'has_financing': _('Has Financing'),
            'financing_institution': _('Financing Institution'),
            'financing_percentage': _('Financing Percentage'),
            'financing_years': _('Financing Years'),
            'contract_date': _('Contract Date'),
            'expected_handover_date': _('Expected Handover Date'),
            'has_installments': _('Has Installments'),
            'number_of_installments': _('Number of Installments'),
            'installment_frequency': _('Installment Frequency'),
            'sold_as_is': _('Sold As Is'),
            'includes_furniture': _('Includes Furniture'),
            'furniture_value': _('Furniture Value'),
            'title_deed_number': _('Title Deed Number'),
            'notary_name': _('Notary Name'),
            'lawyer_name': _('Lawyer Name'),
            'terms_and_conditions': _('Terms and Conditions'),
            'special_conditions': _('Special Conditions'),
            'has_agent': _('Has Agent'),
            'agent_name': _('Agent Name'),
            'agent_commission_percentage': _('Agent Commission %'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter available properties
        self.fields['property'].queryset = Property.objects.filter(status='available')
        
        # Filter qualified buyers
        self.fields['buyer'].queryset = Buyer.objects.filter(
            is_qualified=True,
            is_active=True
        )
        
        # Set default dates
        if not self.instance.pk:
            self.fields['contract_date'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        sale_price = cleaned_data.get('sale_price')
        down_payment = cleaned_data.get('down_payment')
        financed_amount = cleaned_data.get('financed_amount', Decimal('0'))
        has_installments = cleaned_data.get('has_installments')
        number_of_installments = cleaned_data.get('number_of_installments', 0)
        
        # Validate down payment
        if sale_price and down_payment:
            if down_payment > sale_price:
                self.add_error('down_payment', _('Down payment cannot exceed sale price'))
            
            # Check if remaining amount needs installments
            remaining = sale_price - down_payment - financed_amount
            if remaining > 0 and not has_installments:
                self.add_error('has_installments', 
                    _('Installments required as remaining amount is %(amount)s') % {
                        'amount': f'{remaining:,.2f}'
                    })
        
        # Validate installments
        if has_installments and number_of_installments <= 0:
            self.add_error('number_of_installments', 
                _('Number of installments must be greater than zero'))
        
        # Validate dates
        contract_date = cleaned_data.get('contract_date')
        expected_handover = cleaned_data.get('expected_handover_date')
        if contract_date and expected_handover:
            if expected_handover <= contract_date:
                self.add_error('expected_handover_date',
                    _('Handover date must be after contract date'))
        
        return cleaned_data


class SalesPaymentForm(forms.ModelForm):
    """
    Form for recording sales payments
    """
    
    class Meta:
        model = SalesPayment
        fields = [
            'sales_contract', 'payment_type', 'amount', 'payment_date',
            'payment_method', 'reference_number', 'bank_name', 'check_number',
            'notes'
        ]
        
        widgets = {
            'sales_contract': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': True
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Transaction Reference'),
                'required': True
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Bank Name')
            }),
            'check_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Check Number')
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Payment Notes')
            }),
        }
        
        labels = {
            'sales_contract': _('Sales Contract'),
            'payment_type': _('Payment Type'),
            'amount': _('Amount'),
            'payment_date': _('Payment Date'),
            'payment_method': _('Payment Method'),
            'reference_number': _('Reference Number'),
            'bank_name': _('Bank Name'),
            'check_number': _('Check Number'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args, **kwargs):
        self.contract = kwargs.pop('contract', None)
        super().__init__(*args, **kwargs)
        
        if self.contract:
            self.fields['sales_contract'].initial = self.contract
            self.fields['sales_contract'].widget.attrs['readonly'] = True
        
        # Set default payment date
        if not self.instance.pk:
            self.fields['payment_date'].initial = timezone.now().date()
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError(_('Payment amount must be greater than zero'))
        return amount
