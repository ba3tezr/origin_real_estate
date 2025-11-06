"""
Contract Serializers for REST API
"""
from rest_framework import serializers
from apps.contracts.models import Contract, ContractPayment, ContractRenewal


class ContractPaymentSerializer(serializers.ModelSerializer):
    """Serializer for ContractPayment model"""

    class Meta:
        model = ContractPayment
        fields = [
            'id', 'contract', 'payment_date', 'amount', 'payment_type',
            'payment_method', 'reference_number', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractRenewalSerializer(serializers.ModelSerializer):
    """Serializer for ContractRenewal model"""

    class Meta:
        model = ContractRenewal
        fields = [
            'id', 'contract', 'renewal_date', 'new_rent_amount',
            'new_start_date', 'new_end_date', 'terms_changed',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for contract list"""
    property_code = serializers.CharField(source='property.code', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'property', 'property_code',
            'client', 'client_name', 'start_date', 'end_date',
            'rent_amount', 'status', 'days_remaining', 'created_at'
        ]
        read_only_fields = ['id', 'contract_number', 'created_at']

    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.end_date:
            delta = obj.end_date - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return None


class ContractSerializer(serializers.ModelSerializer):
    """Full serializer for Contract model"""
    property_code = serializers.CharField(source='property.code', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    payments = ContractPaymentSerializer(many=True, read_only=True)
    renewals = ContractRenewalSerializer(many=True, read_only=True)
    total_paid = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'property', 'property_code',
            'property_title', 'client', 'client_name', 'start_date',
            'end_date', 'rent_amount', 'payment_frequency', 'deposit_amount',
            'terms_and_conditions', 'status', 'is_active', 'created_at',
            'updated_at', 'payments', 'renewals', 'total_paid',
            'remaining_amount'
        ]
        read_only_fields = ['id', 'contract_number', 'created_at', 'updated_at']

    def get_total_paid(self, obj):
        total = obj.payments.aggregate(total=serializers.Sum('amount'))['total']
        return float(total) if total else 0.0

    def get_remaining_amount(self, obj):
        from datetime import datetime
        if obj.rent_amount and obj.start_date and obj.end_date:
            months = (obj.end_date.year - obj.start_date.year) * 12 + (
                obj.end_date.month - obj.start_date.month
            )
            total_expected = float(obj.rent_amount) * max(months, 1)
            return total_expected - self.get_total_paid(obj)
        return 0.0
