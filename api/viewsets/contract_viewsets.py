"""
Contract ViewSets for REST API
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.contracts.models import Contract, ContractPayment, ContractRenewal
from api.serializers import (
    ContractSerializer,
    ContractListSerializer,
    ContractPaymentSerializer,
    ContractRenewalSerializer,
)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related('property', 'client')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['contract_number', 'property__code', 'client__name']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContractListSerializer
        return ContractSerializer


class ContractPaymentViewSet(viewsets.ModelViewSet):
    queryset = ContractPayment.objects.all()
    serializer_class = ContractPaymentSerializer
    permission_classes = [IsAuthenticated]


class ContractRenewalViewSet(viewsets.ModelViewSet):
    queryset = ContractRenewal.objects.all()
    serializer_class = ContractRenewalSerializer
    permission_classes = [IsAuthenticated]
