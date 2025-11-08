"""
Admin configuration for Properties app
"""
from django.contrib import admin
from .models import (
    PropertyType,
    Property,
    PropertyDocument,
    PropertyImage,
    PropertyValuation,
    PropertyAmenity,
    PropertyInspection,
    PropertyExpense,
    PropertyRevenue,
)


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']


class PropertyDocumentInline(admin.TabularInline):
    model = PropertyDocument
    extra = 1
    fields = ['title', 'document_type', 'file', 'expiry_date']
    readonly_fields = ['uploaded_at', 'uploaded_by']


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'title', 'caption', 'is_primary', 'order']
    readonly_fields = ['uploaded_at']


class PropertyValuationInline(admin.TabularInline):
    model = PropertyValuation
    extra = 0
    fields = ['valuation_date', 'valuation_amount', 'valuation_type', 'valuator_name']
    readonly_fields = ['created_at']


class PropertyAmenityInline(admin.TabularInline):
    model = PropertyAmenity
    extra = 0
    fields = ['amenity_type', 'name', 'is_available']
    readonly_fields = ['created_at']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'title', 'property_type', 'owner', 'city',
        'status', 'area_sqm', 'rental_price_monthly', 'is_active'
    ]
    list_filter = [
        'status', 'property_type', 'is_active', 
        'city', 'is_furnished', 'pets_allowed', 'created_at'
    ]
    search_fields = [
        'code', 'title', 'address', 'city', 
        'owner__name', 'description'
    ]
    readonly_fields = ['code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'title', 'property_type', 'owner')
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'district', 'postal_code',
                'latitude', 'longitude', 'virtual_tour_url', 'video_url'
            )
        }),
        ('Details', {
            'fields': (
                'area_sqm', 'bedrooms', 'bathrooms', 'floors',
                'floor_number', 'total_floors', 'parking_spaces',
                'year_built', 'is_furnished', 'pets_allowed', 'energy_rating'
            )
        }),
        ('Financial', {
            'fields': (
                'rental_price_monthly', 'purchase_price', 'market_value',
                'occupancy_rate', 'average_roi'
            )
        }),
        ('Features', {
            'fields': ('has_elevator', 'has_garden', 'has_pool', 'has_security')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Description', {
            'fields': ('description', 'notes', 'last_renovation_date')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        PropertyImageInline,
        PropertyDocumentInline,
        PropertyAmenityInline,
        PropertyValuationInline,
    ]


@admin.register(PropertyDocument)
class PropertyDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'property', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'property__code', 'property__title']
    readonly_fields = ['uploaded_at', 'uploaded_by']


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'title', 'is_primary', 'order', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['title', 'caption', 'property__code', 'property__title']
    readonly_fields = ['uploaded_at']


@admin.register(PropertyValuation)
class PropertyValuationAdmin(admin.ModelAdmin):
    list_display = ['property', 'valuation_date', 'valuation_amount', 'valuation_type']
    list_filter = ['valuation_type', 'valuation_date']
    search_fields = ['property__code', 'property__title', 'valuator_name']
    readonly_fields = ['created_at']


@admin.register(PropertyAmenity)
class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = ['property', 'amenity_type', 'name', 'is_available']
    list_filter = ['amenity_type', 'is_available']
    search_fields = ['name', 'property__code', 'property__title']
    readonly_fields = ['created_at']


@admin.register(PropertyInspection)
class PropertyInspectionAdmin(admin.ModelAdmin):
    list_display = ['property', 'inspection_date', 'inspection_type', 'overall_condition']
    list_filter = ['inspection_type', 'overall_condition', 'inspection_date']
    search_fields = ['property__code', 'property__title', 'inspector_name']
    readonly_fields = ['created_at']


@admin.register(PropertyExpense)
class PropertyExpenseAdmin(admin.ModelAdmin):
    list_display = ['property', 'expense_date', 'expense_type', 'amount', 'is_recurring']
    list_filter = ['expense_type', 'is_recurring', 'recurrence_frequency']
    search_fields = ['property__code', 'property__title', 'vendor']
    readonly_fields = ['created_at']


@admin.register(PropertyRevenue)
class PropertyRevenueAdmin(admin.ModelAdmin):
    list_display = ['property', 'revenue_date', 'revenue_type', 'amount']
    list_filter = ['revenue_type', 'revenue_date']
    search_fields = ['property__code', 'property__title', 'source']
    readonly_fields = ['created_at']
