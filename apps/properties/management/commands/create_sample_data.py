"""
Management command to create sample data for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.owners.models import Owner
from apps.clients.models import Client
from apps.properties.models import (
    PropertyType,
    Property,
    PropertyAmenity,
    PropertyValuation,
    PropertyInspection,
    PropertyExpense,
    PropertyRevenue,
)
from decimal import Decimal
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create Owners
        owners = []
        owner_data = [
            {'name': 'Ahmed Ali', 'phone': '+20123456789', 'email': 'ahmed@example.com', 'national_id': '29901010101234'},
            {'name': 'Mohamed Hassan', 'phone': '+20123456788', 'email': 'mohamed@example.com', 'national_id': '29902020202345'},
            {'name': 'Sara Ibrahim', 'phone': '+20123456787', 'email': 'sara@example.com', 'national_id': '29903030303456'},
        ]
        
        for data in owner_data:
            owner, created = Owner.objects.get_or_create(
                national_id=data['national_id'],
                defaults=data
            )
            owners.append(owner)
            if created:
                self.stdout.write(f'  Created owner: {owner.name}')

        # Create Clients
        clients = []
        client_data = [
            {'name': 'Khaled Mahmoud', 'phone': '+20123456786', 'email': 'khaled@example.com', 'national_id': '12345678901234'},
            {'name': 'Fatima Youssef', 'phone': '+20123456785', 'email': 'fatima@example.com', 'national_id': '12345678901235'},
            {'name': 'Omar Saeed', 'phone': '+20123456784', 'email': 'omar@example.com', 'national_id': '12345678901236'},
        ]
        
        for data in client_data:
            client, created = Client.objects.get_or_create(
                national_id=data['national_id'],
                defaults=data
            )
            clients.append(client)
            if created:
                self.stdout.write(f'  Created client: {client.name}')

        # Create Property Types
        types = []
        type_data = [
            {'name': 'Apartment', 'description': 'Residential apartment units'},
            {'name': 'Villa', 'description': 'Standalone villa properties'},
            {'name': 'Commercial', 'description': 'Commercial office spaces'},
            {'name': 'Studio', 'description': 'Studio apartments'},
        ]
        
        for data in type_data:
            ptype, created = PropertyType.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            types.append(ptype)
            if created:
                self.stdout.write(f'  Created property type: {ptype.name}')

        # Create Properties
        properties_data = [
            {
                'title': 'Luxury Apartment in Downtown',
                'property_type': types[0],
                'owner': owners[0],
                'address': '123 Main Street, Building A',
                'city': 'Cairo',
                'district': 'Zamalek',
                'latitude': Decimal('30.061952'),
                'longitude': Decimal('31.219231'),
                'area_sqm': Decimal('120.50'),
                'bedrooms': 2,
                'bathrooms': 2,
                'rental_price_monthly': Decimal('5000.00'),
                'purchase_price': Decimal('750000.00'),
                'market_value': Decimal('820000.00'),
                'year_built': 2015,
                'floor_number': 7,
                'total_floors': 15,
                'is_furnished': True,
                'has_elevator': True,
                'has_security': True,
                'energy_rating': 'A+',
                'pets_allowed': False,
                'occupancy_rate': Decimal('92.5'),
                'average_roi': Decimal('8.2'),
                'status': 'available',
            },
            {
                'title': 'Modern Villa with Garden',
                'property_type': types[1],
                'owner': owners[1],
                'address': '456 Palm Avenue',
                'city': 'Cairo',
                'district': 'New Cairo',
                'latitude': Decimal('30.027381'),
                'longitude': Decimal('31.483078'),
                'area_sqm': Decimal('350.00'),
                'bedrooms': 4,
                'bathrooms': 3,
                'parking_spaces': 2,
                'floors': 2,
                'has_garden': True,
                'has_pool': True,
                'has_security': True,
                'purchase_price': Decimal('4200000.00'),
                'market_value': Decimal('4800000.00'),
                'year_built': 2018,
                'energy_rating': 'A',
                'pets_allowed': True,
                'occupancy_rate': Decimal('87.0'),
                'average_roi': Decimal('9.5'),
                'rental_price_monthly': Decimal('15000.00'),
                'status': 'available',
            },
            {
                'title': 'Commercial Office Space',
                'property_type': types[2],
                'owner': owners[2],
                'address': '789 Business District',
                'city': 'Cairo',
                'district': 'Nasr City',
                'latitude': Decimal('30.051112'),
                'longitude': Decimal('31.368332'),
                'area_sqm': Decimal('200.00'),
                'floors': 1,
                'parking_spaces': 5,
                'purchase_price': Decimal('1100000.00'),
                'market_value': Decimal('1300000.00'),
                'energy_rating': 'B+',
                'occupancy_rate': Decimal('95.0'),
                'average_roi': Decimal('10.1'),
                'rental_price_monthly': Decimal('8000.00'),
                'status': 'rented',
            },
            {
                'title': 'Cozy Studio Apartment',
                'property_type': types[3],
                'owner': owners[0],
                'address': '321 Student Area',
                'city': 'Alexandria',
                'district': 'Smouha',
                'latitude': Decimal('31.207918'),
                'longitude': Decimal('29.934562'),
                'area_sqm': Decimal('45.00'),
                'bedrooms': 1,
                'bathrooms': 1,
                'is_furnished': True,
                'purchase_price': Decimal('350000.00'),
                'market_value': Decimal('410000.00'),
                'year_built': 2020,
                'energy_rating': 'A+',
                'pets_allowed': True,
                'occupancy_rate': Decimal('98.0'),
                'average_roi': Decimal('12.4'),
                'rental_price_monthly': Decimal('2500.00'),
                'status': 'available',
            },
        ]

        created_properties = []
        for index, data in enumerate(properties_data, start=1):
            # Generate unique code
            code = f"PROP-{date.today().year}-{Property.objects.count() + 1:04d}"
            property_obj, created = Property.objects.get_or_create(
                code=code,
                defaults=data
            )
            if created:
                self.stdout.write(f'  Created property: {property_obj.title}')
            created_properties.append(property_obj)

        # Create amenities, valuations, inspections, expenses, revenues
        today = date.today()
        for prop in created_properties:
            # Amenities
            PropertyAmenity.objects.get_or_create(
                property=prop,
                name='High-speed Internet',
                defaults={'amenity_type': 'technology', 'description': 'Fiber internet available'}
            )
            PropertyAmenity.objects.get_or_create(
                property=prop,
                name='24/7 Security',
                defaults={'amenity_type': 'security', 'description': 'Security guards and CCTV'}
            )

            # Valuations
            PropertyValuation.objects.get_or_create(
                property=prop,
                valuation_date=today - timedelta(days=120),
                valuation_amount=prop.market_value or Decimal('500000.00'),
                valuation_type='market',
                defaults={'valuator_name': 'Prime Valuators', 'notes': 'Quarterly valuation review'}
            )

            # Inspections
            PropertyInspection.objects.get_or_create(
                property=prop,
                inspection_date=today - timedelta(days=60),
                inspector_name='Facility Team',
                defaults={
                    'inspection_type': 'maintenance',
                    'overall_condition': 'good',
                    'notes': 'Routine inspection completed with minor observations.',
                    'recommendations': 'Check HVAC filters next visit.',
                    'next_inspection_date': today + timedelta(days=120),
                }
            )

            # Expenses
            PropertyExpense.objects.get_or_create(
                property=prop,
                expense_date=today - timedelta(days=30),
                amount=Decimal('750.00'),
                expense_type='maintenance',
                defaults={
                    'vendor': 'CleanCo Services',
                    'description': 'Monthly deep cleaning and maintenance',
                    'is_recurring': True,
                    'recurrence_frequency': 'monthly',
                }
            )

            # Revenues
            PropertyRevenue.objects.get_or_create(
                property=prop,
                revenue_date=today - timedelta(days=15),
                amount=prop.rental_price_monthly or Decimal('4500.00'),
                revenue_type='rent',
                defaults={'source': 'Tenant Payment'}
            )

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(f'  Owners: {Owner.objects.count()}')
        self.stdout.write(f'  Clients: {Client.objects.count()}')
        self.stdout.write(f'  Property Types: {PropertyType.objects.count()}')
        self.stdout.write(f'  Properties: {Property.objects.count()}')
