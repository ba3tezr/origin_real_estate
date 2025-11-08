from rest_framework import serializers
from apps.sales.models import (
    Buyer,
    PropertyReservation,
    SalesContract,
    SalesPaymentPlan,
    SalesPayment
)


class BuyerSerializer(serializers.ModelSerializer):
    purchasing_power = serializers.SerializerMethodField()
    buyer_type_display = serializers.CharField(source='get_buyer_type_display', read_only=True)
    
    class Meta:
        model = Buyer
        fields = [
            'id', 'buyer_type', 'buyer_type_display', 'name', 'phone', 'email',
            'national_id', 'address', 'city', 'country', 'company_name',
            'company_registration', 'tax_id', 'annual_income', 'credit_score',
            'financing_approved', 'financing_institution', 'approved_loan_amount',
            'has_agent', 'agent_name', 'agent_phone', 'is_qualified', 'is_active',
            'purchasing_power', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_purchasing_power(self, obj):
        return float(obj.get_purchasing_power())


class PropertyReservationSerializer(serializers.ModelSerializer):
    property_code = serializers.CharField(source='property.code', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    buyer_name = serializers.CharField(source='buyer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PropertyReservation
        fields = [
            'id', 'reservation_number', 'property', 'property_code', 'property_title',
            'buyer', 'buyer_name', 'reservation_date', 'expiry_date',
            'reservation_amount', 'payment_method', 'payment_reference',
            'status', 'status_display', 'notes', 'cancellation_reason',
            'reserved_by', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reservation_number', 'reservation_date', 'created_at', 'updated_at']


class SalesPaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPaymentPlan
        fields = [
            'id', 'installment_number', 'due_date', 'amount', 'is_paid',
            'payment_date', 'payment_reference', 'is_overdue', 'late_fee',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SalesPaymentSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SalesPayment
        fields = [
            'id', 'sales_contract', 'payment_plan', 'payment_type',
            'payment_type_display', 'amount', 'payment_date', 'payment_method',
            'payment_method_display', 'reference_number', 'bank_name',
            'check_number', 'status', 'status_display', 'receipt_number',
            'receipt_file', 'notes', 'received_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['receipt_number', 'created_at', 'updated_at']


class SalesContractSerializer(serializers.ModelSerializer):
    property_code = serializers.CharField(source='property.code', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    buyer_name = serializers.CharField(source='buyer.name', read_only=True)
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_paid = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    payment_progress = serializers.SerializerMethodField()
    is_fully_paid = serializers.SerializerMethodField()
    payment_plans = SalesPaymentPlanSerializer(many=True, read_only=True)
    payments = SalesPaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = SalesContract
        fields = [
            'id', 'contract_number', 'property', 'property_code', 'property_title',
            'buyer', 'buyer_name', 'seller', 'seller_name', 'sale_price',
            'down_payment', 'financed_amount', 'has_financing',
            'financing_institution', 'financing_percentage', 'financing_years',
            'contract_date', 'signing_date', 'expected_handover_date',
            'actual_handover_date', 'has_installments', 'number_of_installments',
            'installment_frequency', 'sold_as_is', 'includes_furniture',
            'furniture_value', 'title_deed_number', 'registration_number',
            'notary_name', 'lawyer_name', 'terms_and_conditions',
            'special_conditions', 'warranty_terms', 'status', 'status_display',
            'is_registered', 'registration_date', 'contract_file',
            'signed_contract_file', 'has_agent', 'agent_name',
            'agent_commission_percentage', 'agent_commission_amount', 'notes',
            'created_by', 'approved_by', 'total_paid', 'remaining_amount',
            'payment_progress', 'is_fully_paid', 'payment_plans', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['contract_number', 'created_at', 'updated_at']
    
    def get_total_paid(self, obj):
        return float(obj.get_total_paid())
    
    def get_remaining_amount(self, obj):
        return float(obj.get_remaining_amount())
    
    def get_payment_progress(self, obj):
        return obj.get_payment_progress_percentage()
    
    def get_is_fully_paid(self, obj):
        return obj.is_fully_paid()


class BuyerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing buyers"""
    buyer_type_display = serializers.CharField(source='get_buyer_type_display', read_only=True)
    
    class Meta:
        model = Buyer
        fields = ['id', 'name', 'buyer_type', 'buyer_type_display', 'phone', 'email', 'is_qualified', 'is_active']


class SalesContractListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing contracts"""
    property_code = serializers.CharField(source='property.code', read_only=True)
    buyer_name = serializers.CharField(source='buyer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesContract
        fields = [
            'id', 'contract_number', 'property_code', 'buyer_name',
            'sale_price', 'status', 'status_display', 'contract_date',
            'payment_progress', 'created_at'
        ]
    
    def get_payment_progress(self, obj):
        return obj.get_payment_progress_percentage()
