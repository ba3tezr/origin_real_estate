"""
Admin configuration for Financial app
"""
from django.contrib import admin
from .models import (
    Account, FinancialPeriod, JournalEntry, JournalEntryLine,
    Invoice, InvoiceItem, Payment, Budget
)


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2
    fields = ['account', 'debit_amount', 'credit_amount', 'description']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'tax_rate', 'discount_rate', 'total', 'account']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'parent', 'is_active', 'get_balance']
    list_filter = ['account_type', 'is_active', 'is_system']
    search_fields = ['code', 'name', 'name_ar']
    ordering = ['code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('code', 'name', 'name_ar', 'account_type', 'parent')
        }),
        ('Opening Balance', {
            'fields': ('opening_balance', 'opening_balance_type')
        }),
        ('Settings', {
            'fields': ('description', 'is_active', 'is_system')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FinancialPeriod)
class FinancialPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_closed']
    list_filter = ['is_closed']
    search_fields = ['name']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'entry_date', 'entry_type', 'is_posted', 'get_total_debit', 'get_total_credit']
    list_filter = ['entry_type', 'is_posted', 'entry_date']
    search_fields = ['entry_number', 'description', 'reference']
    readonly_fields = ['entry_number', 'created_at', 'updated_at', 'posted_at']
    inlines = [JournalEntryLineInline]
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('entry_number', 'entry_date', 'entry_type', 'period')
        }),
        ('Details', {
            'fields': ('description', 'reference')
        }),
        ('Related Entities', {
            'fields': ('property', 'contract')
        }),
        ('Status', {
            'fields': ('is_posted', 'posted_at', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'invoice_type', 'invoice_date', 'due_date', 'total_amount', 'paid_amount', 'status']
    list_filter = ['invoice_type', 'status', 'invoice_date']
    search_fields = ['invoice_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'invoice_type', 'invoice_date', 'due_date')
        }),
        ('Related Entities', {
            'fields': ('property', 'contract')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes', 'terms_and_conditions')
        }),
        ('Accounting', {
            'fields': ('journal_entry',)
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'payment_type', 'payment_date', 'payment_method', 'amount', 'invoice']
    list_filter = ['payment_type', 'payment_method', 'payment_date']
    search_fields = ['payment_number', 'reference_number']
    readonly_fields = ['created_at']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'period', 'account', 'budgeted_amount', 'property']
    list_filter = ['period', 'account__account_type']
    search_fields = ['name', 'account__name']
