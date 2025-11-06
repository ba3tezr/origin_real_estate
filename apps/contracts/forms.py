"""Forms for Contracts app"""
from django import forms
from django.utils import timezone
from .models import Contract, ContractPayment, ContractRenewal

class ContractForm(forms.ModelForm):
    """Form for creating and updating contracts"""
    
    class Meta:
        model = Contract
        fields = [
            'property', 'client', 'contract_number', 'contract_type',
            'start_date', 'end_date', 'rent_amount', 'security_deposit',
            'payment_frequency', 'payment_day', 'maintenance_fee', 'utility_charges',
            'auto_renew', 'renewal_notice_days', 'status',
            'terms_and_conditions', 'special_conditions', 'notes', 'contract_file'
        ]
        widgets = {
            'property': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left blank'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'security_deposit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_frequency': forms.Select(attrs={'class': 'form-select'}),
            'payment_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 31}),
            'maintenance_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'utility_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'auto_renew': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'renewal_notice_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'special_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'contract_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract_number'].required = False

    def save(self, commit=True):
        contract = super().save(commit=False)
        if not contract.contract_number:
            contract.contract_number = self._generate_contract_number()
        if commit:
            contract.save()
            self.save_m2m()
        return contract

    @staticmethod
    def _generate_contract_number():
        year = timezone.now().year
        prefix = f"CONT-{year}-"
        last_number = (
            Contract.objects.filter(contract_number__startswith=prefix)
            .order_by('-contract_number')
            .values_list('contract_number', flat=True)
            .first()
        )
        if last_number:
            try:
                index = int(last_number.rsplit('-', 1)[-1]) + 1
            except (ValueError, AttributeError):
                index = 1
        else:
            index = 1
        new_code = f"{prefix}{index:04d}"
        while Contract.objects.filter(contract_number=new_code).exists():
            index += 1
            new_code = f"{prefix}{index:04d}"
        return new_code

class ContractSearchForm(forms.Form):
    """Form for searching contracts"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by contract number, client...'
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + list(Contract.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    contract_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + list(Contract.CONTRACT_TYPES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_frequency = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + list(Contract.PAYMENT_FREQUENCY),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    start_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

class ContractPaymentForm(forms.ModelForm):
    """Form for contract payments"""
    
    class Meta:
        model = ContractPayment
        fields = [
            'payment_date', 'amount', 'payment_method',
            'status', 'reference_number', 'notes', 'receipt_file'
        ]
        widgets = {
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'receipt_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ContractRenewalForm(forms.ModelForm):
    """Form for contract renewals"""

    class Meta:
        model = ContractRenewal
        fields = ['new_contract', 'renewal_date', 'rent_increase', 'notes']
        widgets = {
            'new_contract': forms.Select(attrs={'class': 'form-select'}),
            'renewal_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rent_increase': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        contract = kwargs.pop('contract', None)
        super().__init__(*args, **kwargs)
        if contract is not None:
            self.fields['new_contract'].queryset = Contract.objects.exclude(pk=contract.pk)
