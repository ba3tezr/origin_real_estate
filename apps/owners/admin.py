"""
Admin configuration for Owners app
"""
from django.contrib import admin
from .models import Owner

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'phone', 'email', 'national_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'phone', 'email', 'national_id')
        }),
        ('Additional Information', {
            'fields': ('address', 'notes', 'is_active')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
