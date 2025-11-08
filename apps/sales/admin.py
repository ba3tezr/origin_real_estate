from django.contrib import admin
from django.utils.html import format_html
from .models import Buyer, PropertyReservation, SalesContract, SalesPaymentPlan, SalesPayment


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ['name', 'buyer_type', 'phone', 'email', 'is_qualified', 'is_active', 'created_at']
    list_filter = ['buyer_type', 'is_qualified', 'is_active', 'created_at']
    search_fields = ['name', 'email', 'phone', 'national_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('buyer_type', 'name', 'phone', 'email', 'national_id', 'address', 'city', 'country')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_registration', 'tax_id'),
            'classes': ('collapse',),
        }),
        ('Financial Information', {
            'fields': ('annual_income', 'credit_score', 'financing_approved', 'financing_institution', 'approved_loan_amount')
        }),
        ('Documents', {
            'fields': ('id_document', 'income_proof')
        }),
        ('Agent Information', {
            'fields': ('has_agent', 'agent_name', 'agent_phone', 'agent_license'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_qualified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_purchasing_power_display(self, obj):
        return f"${obj.get_purchasing_power():,.2f}"
    get_purchasing_power_display.short_description = 'Purchasing Power'


@admin.register(PropertyReservation)
class PropertyReservationAdmin(admin.ModelAdmin):
    list_display = ['reservation_number', 'property', 'buyer', 'reservation_amount', 'status', 'expiry_date', 'created_at']
    list_filter = ['status', 'payment_method', 'reservation_date', 'expiry_date']
    search_fields = ['reservation_number', 'property__code', 'buyer__name']
    readonly_fields = ['reservation_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('reservation_number', 'property', 'buyer', 'reserved_by')
        }),
        ('Dates', {
            'fields': ('reservation_date', 'expiry_date')
        }),
        ('Financial', {
            'fields': ('reservation_amount', 'payment_method', 'payment_reference')
        }),
        ('Status', {
            'fields': ('status', 'notes', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_status_display(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'cancelled': 'red',
            'converted': 'blue',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    get_status_display.short_description = 'Status'


@admin.register(SalesContract)
class SalesContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'property', 'buyer', 'sale_price', 'status', 'contract_date', 'payment_progress']
    list_filter = ['status', 'has_financing', 'has_installments', 'is_registered', 'contract_date']
    search_fields = ['contract_number', 'property__code', 'buyer__name', 'seller__name']
    readonly_fields = ['created_at', 'updated_at', 'get_payment_progress']
    date_hierarchy = 'contract_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('contract_number', 'property', 'buyer', 'seller', 'created_by')
        }),
        ('Price & Payment', {
            'fields': ('sale_price', 'down_payment', 'financed_amount')
        }),
        ('Financing Details', {
            'fields': ('has_financing', 'financing_institution', 'financing_percentage', 'financing_years'),
            'classes': ('collapse',),
        }),
        ('Dates', {
            'fields': ('contract_date', 'signing_date', 'expected_handover_date', 'actual_handover_date')
        }),
        ('Payment Plan', {
            'fields': ('has_installments', 'number_of_installments', 'installment_frequency')
        }),
        ('Property Condition', {
            'fields': ('sold_as_is', 'includes_furniture', 'furniture_value'),
            'classes': ('collapse',),
        }),
        ('Legal & Documents', {
            'fields': ('title_deed_number', 'registration_number', 'notary_name', 'lawyer_name'),
            'classes': ('collapse',),
        }),
        ('Terms & Conditions', {
            'fields': ('terms_and_conditions', 'special_conditions', 'warranty_terms'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('status', 'is_registered', 'registration_date', 'approved_by')
        }),
        ('Files', {
            'fields': ('contract_file', 'signed_contract_file'),
            'classes': ('collapse',),
        }),
        ('Agent Commission', {
            'fields': ('has_agent', 'agent_name', 'agent_commission_percentage', 'agent_commission_amount'),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def payment_progress(self, obj):
        progress = obj.get_payment_progress_percentage()
        color = 'green' if progress == 100 else 'orange' if progress > 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            progress
        )
    payment_progress.short_description = 'Payment Progress'
    
    def get_payment_progress(self, obj):
        return f"{obj.get_payment_progress_percentage():.2f}% (${obj.get_total_paid():,.2f} / ${obj.sale_price:,.2f})"
    get_payment_progress.short_description = 'Payment Progress'


@admin.register(SalesPaymentPlan)
class SalesPaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['sales_contract', 'installment_number', 'due_date', 'amount', 'is_paid', 'is_overdue']
    list_filter = ['is_paid', 'is_overdue', 'due_date']
    search_fields = ['sales_contract__contract_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contract', {
            'fields': ('sales_contract',)
        }),
        ('Installment Details', {
            'fields': ('installment_number', 'due_date', 'amount')
        }),
        ('Status', {
            'fields': ('is_paid', 'payment_date', 'payment_reference', 'is_overdue', 'late_fee')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(SalesPayment)
class SalesPaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'sales_contract', 'payment_type', 'amount', 'payment_date', 'payment_method', 'status']
    list_filter = ['payment_type', 'payment_method', 'status', 'payment_date']
    search_fields = ['receipt_number', 'sales_contract__contract_number', 'reference_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Contract', {
            'fields': ('sales_contract', 'payment_plan')
        }),
        ('Payment Details', {
            'fields': ('payment_type', 'amount', 'payment_date', 'payment_method')
        }),
        ('References', {
            'fields': ('reference_number', 'bank_name', 'check_number')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Receipt', {
            'fields': ('receipt_number', 'receipt_file')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Staff', {
            'fields': ('received_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
