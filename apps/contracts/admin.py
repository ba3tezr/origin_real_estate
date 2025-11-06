"""
Admin configuration for Contracts app
"""
from django.contrib import admin
from .models import Contract, ContractPayment, ContractRenewal

class ContractPaymentInline(admin.TabularInline):
    model = ContractPayment
    extra = 1
    fields = ['payment_date', 'amount', 'payment_method', 'status']

class ContractRenewalInline(admin.TabularInline):
    model = ContractRenewal
    fk_name = 'original_contract'
    extra = 0
    fields = ['renewal_date', 'new_contract']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'property', 'client', 'start_date', 'end_date', 'status', 'rent_amount']
    list_filter = ['status', 'contract_type', 'start_date', 'end_date']
    search_fields = ['contract_number', 'property__code', 'client__name']
    readonly_fields = ['contract_number', 'created_at', 'updated_at']
    inlines = [ContractPaymentInline, ContractRenewalInline]
    
    fieldsets = (
        ('Contract Information', {
            'fields': ('contract_number', 'property', 'client', 'contract_type')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date')
        }),
        ('Financial', {
            'fields': ('rent_amount', 'deposit_amount', 'payment_frequency')
        }),
        ('Status', {
            'fields': ('status', 'terms_conditions', 'notes')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContractPayment)
class ContractPaymentAdmin(admin.ModelAdmin):
    list_display = ['contract', 'payment_date', 'amount', 'payment_method', 'status']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['contract__contract_number', 'reference_number']

@admin.register(ContractRenewal)
class ContractRenewalAdmin(admin.ModelAdmin):
    list_display = ['original_contract', 'renewal_date', 'new_contract']
    list_filter = ['renewal_date']
    search_fields = ['original_contract__contract_number', 'new_contract__contract_number']
