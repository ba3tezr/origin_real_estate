"""
Client Serializers for REST API
"""
from rest_framework import serializers
from apps.clients.models import Client


class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for client list"""
    contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'address',
            'contracts_count', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_contracts_count(self, obj):
        return obj.contracts.count()


class ClientSerializer(serializers.ModelSerializer):
    """Full serializer for Client model"""
    contracts_count = serializers.SerializerMethodField()
    active_contracts = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'mobile', 'address',
            'city', 'country', 'national_id', 'date_of_birth',
            'occupation', 'notes', 'is_active', 'created_at',
            'updated_at', 'contracts_count', 'active_contracts'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_contracts_count(self, obj):
        return obj.contracts.count()

    def get_active_contracts(self, obj):
        return obj.contracts.filter(status='active').count()
