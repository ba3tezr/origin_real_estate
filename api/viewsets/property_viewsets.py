"""
Property ViewSets for REST API
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count, Q

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
from api.serializers import (
    PropertyTypeSerializer,
    PropertySerializer,
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyImageSerializer,
    PropertyDocumentSerializer,
    PropertyValuationSerializer,
    PropertyAmenitySerializer,
    PropertyInspectionSerializer,
    PropertyExpenseSerializer,
    PropertyRevenueSerializer,
)


class PropertyTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for PropertyType model"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    ordering = ['name']


class PropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for Property model with advanced features"""
    queryset = Property.objects.select_related('property_type', 'owner').prefetch_related('images')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'title', 'address', 'city', 'district']
    ordering_fields = ['created_at', 'rental_price_monthly', 'area_sqm', 'code']
    ordering = ['-created_at']
    filterset_fields = {
        'property_type': ['exact'],
        'status': ['exact'],
        'city': ['exact', 'icontains'],
        'bedrooms': ['exact', 'gte', 'lte'],
        'bathrooms': ['exact', 'gte', 'lte'],
        'is_furnished': ['exact'],
        'is_active': ['exact'],
        'rental_price_monthly': ['gte', 'lte'],
        'area_sqm': ['gte', 'lte'],
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        elif self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertySerializer

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall property statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_properties': queryset.count(),
            'active_properties': queryset.filter(is_active=True).count(),
            'status_breakdown': list(
                queryset.values('status')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'type_distribution': list(
                queryset.values('property_type__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'average_rent': queryset.aggregate(avg=Avg('rental_price_monthly'))['avg'],
            'total_area': queryset.aggregate(total=Sum('area_sqm'))['total'],
            'average_occupancy': queryset.aggregate(avg=Avg('occupancy_rate'))['avg'],
            'average_roi': queryset.aggregate(avg=Avg('average_roi'))['avg'],
        }
        
        return Response(stats)

    @action(detail=True, methods=['get'])
    def financial_summary(self, request, pk=None):
        """Get financial summary for a property"""
        property_obj = self.get_object()
        
        total_revenues = property_obj.revenues.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = property_obj.expenses.aggregate(total=Sum('amount'))['total'] or 0
        net_income = total_revenues - total_expenses
        
        summary = {
            'property_code': property_obj.code,
            'total_revenues': float(total_revenues),
            'total_expenses': float(total_expenses),
            'net_income': float(net_income),
            'rental_price_monthly': float(property_obj.rental_price_monthly or 0),
            'market_value': float(property_obj.market_value or 0),
            'purchase_price': float(property_obj.purchase_price or 0),
            'occupancy_rate': float(property_obj.occupancy_rate or 0),
            'average_roi': float(property_obj.average_roi or 0),
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Get properties with coordinates for map display"""
        properties = self.get_queryset().exclude(
            Q(latitude__isnull=True) | Q(longitude__isnull=True)
        )
        
        map_data = [
            {
                'id': prop.id,
                'code': prop.code,
                'title': prop.title,
                'latitude': float(prop.latitude),
                'longitude': float(prop.longitude),
                'status': prop.status,
                'rent': float(prop.rental_price_monthly or 0),
                'city': prop.city,
            }
            for prop in properties
        ]
        
        return Response(map_data)


class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticated]


class PropertyDocumentViewSet(viewsets.ModelViewSet):
    queryset = PropertyDocument.objects.all()
    serializer_class = PropertyDocumentSerializer
    permission_classes = [IsAuthenticated]


class PropertyValuationViewSet(viewsets.ModelViewSet):
    queryset = PropertyValuation.objects.all()
    serializer_class = PropertyValuationSerializer
    permission_classes = [IsAuthenticated]


class PropertyAmenityViewSet(viewsets.ModelViewSet):
    queryset = PropertyAmenity.objects.all()
    serializer_class = PropertyAmenitySerializer
    permission_classes = [IsAuthenticated]


class PropertyInspectionViewSet(viewsets.ModelViewSet):
    queryset = PropertyInspection.objects.all()
    serializer_class = PropertyInspectionSerializer
    permission_classes = [IsAuthenticated]


class PropertyExpenseViewSet(viewsets.ModelViewSet):
    queryset = PropertyExpense.objects.all()
    serializer_class = PropertyExpenseSerializer
    permission_classes = [IsAuthenticated]


class PropertyRevenueViewSet(viewsets.ModelViewSet):
    queryset = PropertyRevenue.objects.all()
    serializer_class = PropertyRevenueSerializer
    permission_classes = [IsAuthenticated]
