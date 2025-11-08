"""
Property Serializers for REST API
"""
from rest_framework import serializers
from apps.properties.models import (
    PropertyType,
    Property,
    PropertyImage,
    PropertyDocument,
    PropertyValuation,
    PropertyAmenity,
    PropertyInspection,
    PropertyExpense,
    PropertyRevenue,
)


class PropertyTypeSerializer(serializers.ModelSerializer):
    """Serializer for PropertyType model"""
    properties_count = serializers.SerializerMethodField()

    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'description', 'is_active', 'properties_count']
        read_only_fields = ['id']

    def get_properties_count(self, obj):
        return obj.properties.count()


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for PropertyImage model"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = [
            'id', 'property', 'image', 'image_url', 'title', 'caption',
            'description', 'is_primary', 'order', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PropertyDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PropertyDocument model"""
    file_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = PropertyDocument
        fields = [
            'id', 'property', 'document_type', 'title', 'file', 'file_url',
            'description', 'expiry_date', 'uploaded_by', 'uploaded_by_name',
            'uploaded_at', 'is_expired'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return None


class PropertyValuationSerializer(serializers.ModelSerializer):
    """Serializer for PropertyValuation model"""
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyValuation
        fields = [
            'id', 'property', 'valuation_date', 'valuation_amount',
            'valuation_type', 'valuator_name', 'notes', 'document',
            'document_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_document_url(self, obj):
        if obj.document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.document.url)
            return obj.document.url
        return None


class PropertyAmenitySerializer(serializers.ModelSerializer):
    """Serializer for PropertyAmenity model"""

    class Meta:
        model = PropertyAmenity
        fields = [
            'id', 'property', 'amenity_type', 'name', 'description',
            'is_available', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PropertyInspectionSerializer(serializers.ModelSerializer):
    """Serializer for PropertyInspection model"""
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyInspection
        fields = [
            'id', 'property', 'inspection_date', 'inspector_name',
            'inspection_type', 'overall_condition', 'notes',
            'recommendations', 'next_inspection_date', 'document',
            'document_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_document_url(self, obj):
        if obj.document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.document.url)
            return obj.document.url
        return None


class PropertyExpenseSerializer(serializers.ModelSerializer):
    """Serializer for PropertyExpense model"""
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyExpense
        fields = [
            'id', 'property', 'expense_date', 'expense_type', 'amount',
            'vendor', 'description', 'receipt', 'receipt_url',
            'is_recurring', 'recurrence_frequency', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_receipt_url(self, obj):
        if obj.receipt:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt.url)
            return obj.receipt.url
        return None


class PropertyRevenueSerializer(serializers.ModelSerializer):
    """Serializer for PropertyRevenue model"""
    contract_number = serializers.CharField(source='contract.contract_number', read_only=True)

    class Meta:
        model = PropertyRevenue
        fields = [
            'id', 'property', 'revenue_date', 'revenue_type', 'amount',
            'source', 'description', 'contract', 'contract_number', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PropertyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for property list"""
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'code', 'title', 'property_type', 'property_type_name',
            'owner', 'owner_name', 'city', 'area_sqm', 'bedrooms',
            'bathrooms', 'rental_price_monthly', 'status', 'is_active',
            'primary_image', 'created_at'
        ]
        read_only_fields = ['id', 'code', 'created_at']

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None


class PropertySerializer(serializers.ModelSerializer):
    """Full serializer for Property model"""
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'code', 'title', 'property_type', 'property_type_name',
            'owner', 'owner_name', 'address', 'city', 'district',
            'postal_code', 'latitude', 'longitude', 'virtual_tour_url',
            'video_url', 'area_sqm', 'bedrooms', 'bathrooms', 'floors',
            'parking_spaces', 'year_built', 'floor_number', 'total_floors',
            'purchase_price', 'market_value', 'rental_price_monthly',
            'has_elevator', 'has_garden', 'has_pool', 'has_security',
            'is_furnished', 'pets_allowed', 'energy_rating', 'description',
            'notes', 'last_renovation_date', 'occupancy_rate', 'average_roi',
            'status', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with related data"""
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    valuations = PropertyValuationSerializer(many=True, read_only=True)
    amenities = PropertyAmenitySerializer(many=True, read_only=True)
    inspections = PropertyInspectionSerializer(many=True, read_only=True)
    expenses = PropertyExpenseSerializer(many=True, read_only=True)
    revenues = PropertyRevenueSerializer(many=True, read_only=True)
    
    total_expenses = serializers.SerializerMethodField()
    total_revenues = serializers.SerializerMethodField()
    net_income = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'code', 'title', 'property_type', 'property_type_name',
            'owner', 'owner_name', 'address', 'city', 'district',
            'postal_code', 'latitude', 'longitude', 'virtual_tour_url',
            'video_url', 'area_sqm', 'bedrooms', 'bathrooms', 'floors',
            'parking_spaces', 'year_built', 'floor_number', 'total_floors',
            'purchase_price', 'market_value', 'rental_price_monthly',
            'has_elevator', 'has_garden', 'has_pool', 'has_security',
            'is_furnished', 'pets_allowed', 'energy_rating', 'description',
            'notes', 'last_renovation_date', 'occupancy_rate', 'average_roi',
            'status', 'is_active', 'created_at', 'updated_at',
            'images', 'documents', 'valuations', 'amenities', 'inspections',
            'expenses', 'revenues', 'total_expenses', 'total_revenues',
            'net_income'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def get_total_expenses(self, obj):
        total = obj.expenses.aggregate(total=serializers.Sum('amount'))['total']
        return float(total) if total else 0.0

    def get_total_revenues(self, obj):
        total = obj.revenues.aggregate(total=serializers.Sum('amount'))['total']
        return float(total) if total else 0.0

    def get_net_income(self, obj):
        return self.get_total_revenues(obj) - self.get_total_expenses(obj)
