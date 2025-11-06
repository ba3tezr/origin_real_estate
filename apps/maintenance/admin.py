"""
Admin configuration for Maintenance app
"""
from django.contrib import admin
from .models import (
    MaintenanceCategory, MaintenanceRequest,
    MaintenanceAttachment, MaintenanceSchedule
)

class MaintenanceAttachmentInline(admin.TabularInline):
    model = MaintenanceAttachment
    extra = 1
    fields = ['file', 'description']

@admin.register(MaintenanceCategory)
class MaintenanceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_number', 'property', 'category',
        'priority', 'status', 'request_date'
    ]
    list_filter = ['status', 'priority', 'category', 'request_date']
    search_fields = ['request_number', 'property__code', 'description']
    readonly_fields = ['request_number', 'created_at', 'updated_at']
    inlines = [MaintenanceAttachmentInline]
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'property', 'category')
        }),
        ('Details', {
            'fields': ('description', 'priority', 'status')
        }),
        ('Dates', {
            'fields': ('request_date', 'scheduled_date', 'completed_date')
        }),
        ('Financial', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'property', 'title', 'frequency',
        'last_service_date', 'next_service_date'
    ]
    list_filter = ['frequency', 'is_active']
    search_fields = ['property__code', 'title']
