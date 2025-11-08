"""
Admin configuration for Owners app
"""
from django.contrib import admin
from .models import Owner


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    """Admin configuration for Owner model"""
    list_display = ['name', 'email', 'phone', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'country', 'created_at']
    search_fields = ['name', 'email', 'phone', 'national_id', 'tax_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'mobile')
        }),
        ('Address', {
            'fields': ('address', 'city', 'country')
        }),
        ('Legal Information', {
            'fields': ('national_id', 'tax_id')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
