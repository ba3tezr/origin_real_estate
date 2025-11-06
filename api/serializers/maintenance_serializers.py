"""
Maintenance Serializers for REST API
"""
from rest_framework import serializers
from apps.maintenance.models import (
    MaintenanceCategory,
    MaintenanceRequest,
    MaintenanceAttachment,
    MaintenanceSchedule,
)


class MaintenanceCategorySerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceCategory model"""
    requests_count = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceCategory
        fields = ['id', 'name', 'description', 'is_active', 'requests_count']
        read_only_fields = ['id']

    def get_requests_count(self, obj):
        return obj.maintenance_requests.count()


class MaintenanceAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceAttachment model"""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceAttachment
        fields = [
            'id', 'maintenance_request', 'file', 'file_url',
            'description', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceSchedule model"""

    class Meta:
        model = MaintenanceSchedule
        fields = [
            'id', 'maintenance_request', 'scheduled_date', 'technician_name',
            'estimated_cost', 'actual_cost', 'notes', 'status',
            'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MaintenanceRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for maintenance request list"""
    property_code = serializers.CharField(source='property.code', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'request_number', 'property', 'property_code',
            'category', 'category_name', 'title', 'priority',
            'status', 'request_date', 'created_at'
        ]
        read_only_fields = ['id', 'request_number', 'created_at']


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Full serializer for MaintenanceRequest model"""
    property_code = serializers.CharField(source='property.code', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    requested_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    attachments = MaintenanceAttachmentSerializer(many=True, read_only=True)
    schedules = MaintenanceScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'request_number', 'property', 'property_code',
            'property_title', 'category', 'category_name', 'title',
            'description', 'priority', 'status', 'request_date',
            'completion_date', 'estimated_cost', 'actual_cost',
            'requested_by', 'requested_by_name', 'assigned_to',
            'assigned_to_name', 'notes', 'created_at', 'updated_at',
            'attachments', 'schedules'
        ]
        read_only_fields = ['id', 'request_number', 'created_at', 'updated_at']

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.get_full_name() or obj.requested_by.username
        return None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None
