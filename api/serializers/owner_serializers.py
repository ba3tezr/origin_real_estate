"""
Owner Serializers for REST API
"""
from rest_framework import serializers
from apps.owners.models import Owner


class OwnerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for owner list"""
    properties_count = serializers.SerializerMethodField()

    class Meta:
        model = Owner
        fields = [
            'id', 'name', 'email', 'phone', 'address',
            'properties_count', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_properties_count(self, obj):
        return obj.properties.count()


class OwnerSerializer(serializers.ModelSerializer):
    """Full serializer for Owner model"""
    properties_count = serializers.SerializerMethodField()
    active_properties = serializers.SerializerMethodField()

    class Meta:
        model = Owner
        fields = [
            'id', 'name', 'email', 'phone', 'mobile', 'address',
            'city', 'country', 'national_id', 'tax_id', 'notes',
            'is_active', 'created_at', 'updated_at',
            'properties_count', 'active_properties'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_properties_count(self, obj):
        return obj.properties.count()

    def get_active_properties(self, obj):
        return obj.properties.filter(is_active=True).count()
