"""
Forms for Financial app
"""
from django import forms
from django.utils import timezone
from .models import (
    Account, JournalEntry, JournalEntryLine, Invoice, InvoiceItem,
    Payment, Budget, FinancialPeriod
)


class AccountForm(forms.ModelForm):
    """Form for Account (Chart of Accounts)"""
    
    class Meta:
        model = Account
        fields = [
            'code', 'name', 'name_ar', 'account_type', 'parent',
            'description', 'opening_balance', 'opening_balance_type',
            'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'opening_balance_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JournalEntryForm(forms.ModelForm):
    """Form for Journal Entry"""
    
    class Meta:
        model = JournalEntry
        fields = [
            'entry_date', 'entry_type', 'period', 'description',
            'reference', 'property', 'contract'
        ]
        widgets = {
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'entry_type': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'contract': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['period'].required = False
        self.fields['property'].required = False
        self.fields['contract'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.entry_number:
            instance.entry_number = self._generate_entry_number()
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    @staticmethod
    def _generate_entry_number():
        prefix = f"JE-{timezone.now().year}-"
        last = JournalEntry.objects.filter(
            entry_number__startswith=prefix
        ).order_by('-entry_number').values_list('entry_number', flat=True).first()
        
        if last:
            try:
                counter = int(last.rsplit('-', 1)[-1]) + 1
            except:
                counter = 1
        else:
            counter = 1
        
        code = f"{prefix}{counter:05d}"
        while JournalEntry.objects.filter(entry_number=code).exists():
            counter += 1
            code = f"{prefix}{counter:05d}"
        return code


class JournalEntryLineForm(forms.ModelForm):
    """Form for Journal Entry Line"""
    
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'debit_amount', 'credit_amount', 'description']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'debit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'credit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InvoiceForm(forms.ModelForm):
    """Form for Invoice"""
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_type', 'invoice_date', 'due_date', 'property',
            'contract', 'subtotal', 'tax_amount', 'discount_amount',
            'total_amount', 'status', 'notes', 'terms_and_conditions'
        ]
        widgets = {
            'invoice_type': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'contract': forms.Select(attrs={'class': 'form-select'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.invoice_number:
            instance.invoice_number = self._generate_invoice_number()
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    @staticmethod
    def _generate_invoice_number():
        prefix = f"INV-{timezone.now().year}-"
        last = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').values_list('invoice_number', flat=True).first()
        
        if last:
            try:
                counter = int(last.rsplit('-', 1)[-1]) + 1
            except:
                counter = 1
        else:
            counter = 1
        
        code = f"{prefix}{counter:05d}"
        while Invoice.objects.filter(invoice_number=code).exists():
            counter += 1
            code = f"{prefix}{counter:05d}"
        return code


class PaymentForm(forms.ModelForm):
    """Form for Payment (Receipt/Payment Voucher)"""
    
    class Meta:
        model = Payment
        fields = [
            'payment_type', 'payment_date', 'payment_method',
            'amount', 'invoice', 'reference_number', 'notes'
        ]
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'invoice': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.payment_number:
            instance.payment_number = self._generate_payment_number(instance.payment_type)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    @staticmethod
    def _generate_payment_number(payment_type):
        prefix_map = {
            'receipt': f"RCV-{timezone.now().year}-",
            'payment': f"PAY-{timezone.now().year}-",
        }
        prefix = prefix_map.get(payment_type, f"PMT-{timezone.now().year}-")
        
        last = Payment.objects.filter(
            payment_number__startswith=prefix
        ).order_by('-payment_number').values_list('payment_number', flat=True).first()
        
        if last:
            try:
                counter = int(last.rsplit('-', 1)[-1]) + 1
            except:
                counter = 1
        else:
            counter = 1
        
        code = f"{prefix}{counter:05d}"
        while Payment.objects.filter(payment_number=code).exists():
            counter += 1
            code = f"{prefix}{counter:05d}"
        return code


class BudgetForm(forms.ModelForm):
    """Form for Budget"""
    
    class Meta:
        model = Budget
        fields = ['name', 'period', 'account', 'budgeted_amount', 'property', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'budgeted_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FinancialPeriodForm(forms.ModelForm):
    """Form for Financial Period"""
    
    class Meta:
        model = FinancialPeriod
        fields = ['name', 'start_date', 'end_date', 'is_closed', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FinancialReportForm(forms.Form):
    """Form for Financial Reports"""
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='End Date'
    )
    property = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Property'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.properties.models import Property
        self.fields['property'].queryset = Property.objects.filter(is_active=True)
