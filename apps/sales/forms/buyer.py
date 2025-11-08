from django import forms
from django.utils.translation import gettext_lazy as _
from apps.sales.models import Buyer


class BuyerForm(forms.ModelForm):
    """
    Form for creating and updating buyers
    """
    
    class Meta:
        model = Buyer
        fields = [
            'buyer_type', 'name', 'phone', 'email', 'national_id',
            'address', 'city', 'country',
            'company_name', 'company_registration', 'tax_id',
            'annual_income', 'credit_score',
            'financing_approved', 'financing_institution', 'approved_loan_amount',
            'id_document', 'income_proof',
            'has_agent', 'agent_name', 'agent_phone', 'agent_license',
            'is_qualified', 'is_active'
        ]
        
        widgets = {
            'buyer_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Full Name'),
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+20XXXXXXXXXX',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'required': True
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('National ID / Passport'),
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Full Address')
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('City')
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Egypt'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Company Name')
            }),
            'company_registration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Registration Number')
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tax ID')
            }),
            'annual_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'credit_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '300-850',
                'min': '300',
                'max': '850'
            }),
            'financing_approved': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'financing_institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Bank Name')
            }),
            'approved_loan_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'id_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'income_proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'has_agent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'agent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Agent Name')
            }),
            'agent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+20XXXXXXXXXX'
            }),
            'agent_license': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('License Number')
            }),
            'is_qualified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'buyer_type': _('Buyer Type'),
            'name': _('Name'),
            'phone': _('Phone'),
            'email': _('Email'),
            'national_id': _('National ID'),
            'address': _('Address'),
            'city': _('City'),
            'country': _('Country'),
            'company_name': _('Company Name'),
            'company_registration': _('Company Registration'),
            'tax_id': _('Tax ID'),
            'annual_income': _('Annual Income'),
            'credit_score': _('Credit Score'),
            'financing_approved': _('Financing Approved'),
            'financing_institution': _('Financing Institution'),
            'approved_loan_amount': _('Approved Loan Amount'),
            'id_document': _('ID Document'),
            'income_proof': _('Income Proof'),
            'has_agent': _('Has Agent'),
            'agent_name': _('Agent Name'),
            'agent_phone': _('Agent Phone'),
            'agent_license': _('Agent License'),
            'is_qualified': _('Is Qualified'),
            'is_active': _('Is Active'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make company fields conditional
        if self.instance and self.instance.buyer_type != 'company':
            self.fields['company_name'].required = False
            self.fields['company_registration'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        buyer_type = cleaned_data.get('buyer_type')
        
        # Validate company fields if buyer is a company
        if buyer_type == 'company':
            if not cleaned_data.get('company_name'):
                self.add_error('company_name', _('Company name is required for company buyers'))
        
        # Validate credit score
        credit_score = cleaned_data.get('credit_score')
        if credit_score and (credit_score < 300 or credit_score > 850):
            self.add_error('credit_score', _('Credit score must be between 300 and 850'))
        
        return cleaned_data


class BuyerSearchForm(forms.Form):
    """
    Form for searching buyers
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search by name, email, phone, or ID'),
        })
    )
    
    buyer_type = forms.ChoiceField(
        required=False,
        choices=[('', _('All Types'))] + list(Buyer.BUYER_TYPE_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_qualified = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All')),
            ('true', _('Qualified')),
            ('false', _('Not Qualified'))
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_active = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All')),
            ('true', _('Active')),
            ('false', _('Inactive'))
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
