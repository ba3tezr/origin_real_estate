"""
Management command to create realistic, fully integrated data
Usage: python manage.py create_realistic_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from apps.properties.models import (
    Property, PropertyType, PropertyImage, PropertyValuation,
    PropertyExpense, PropertyRevenue
)
from apps.owners.models import Owner
from apps.clients.models import Client
from apps.contracts.models import Contract, ContractPayment
from apps.maintenance.models import MaintenanceRequest, MaintenanceCategory
from apps.financial.models import (
    Account, FinancialPeriod, JournalEntry, JournalEntryLine,
    Invoice, InvoiceItem, Payment
)


class Command(BaseCommand):
    help = 'Create realistic, fully integrated data for the system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creating realistic data...'))

        # Create Financial Period
        self.stdout.write('Creating Financial Period...')
        period = FinancialPeriod.objects.create(
            name='FY 2025',
            start_date=datetime(2025, 1, 1).date(),
            end_date=datetime(2025, 12, 31).date(),
            is_closed=False
        )
        self.stdout.write(self.style.SUCCESS('✓ Financial Period created'))

        # Create Chart of Accounts
        self.stdout.write('Creating Chart of Accounts...')
        accounts = self._create_chart_of_accounts()
        self.stdout.write(self.style.SUCCESS(f'✓ {len(accounts)} accounts created'))

        # Create Property Types
        self.stdout.write('Creating Property Types...')
        property_types = self._create_property_types()
        self.stdout.write(self.style.SUCCESS(f'✓ {len(property_types)} property types created'))

        # Create Owners
        self.stdout.write('Creating Owners...')
        owners = self._create_owners()
        self.stdout.write(self.style.SUCCESS(f'✓ {len(owners)} owners created'))

        # Create Properties
        self.stdout.write('Creating Properties...')
        properties = self._create_properties(owners, property_types)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(properties)} properties created'))

        # Create Property Financial Records
        self.stdout.write('Creating Property Financial Records...')
        self._create_property_financials(properties, accounts, period)
        self.stdout.write(self.style.SUCCESS('✓ Property financial records created'))

        # Create Clients
        self.stdout.write('Creating Clients/Tenants...')
        clients = self._create_clients()
        self.stdout.write(self.style.SUCCESS(f'✓ {len(clients)} clients created'))

        # Create Contracts
        self.stdout.write('Creating Contracts...')
        contracts = self._create_contracts(properties, clients, accounts, period)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(contracts)} contracts created'))

        # Create Maintenance Categories
        self.stdout.write('Creating Maintenance Categories...')
        maintenance_categories = self._create_maintenance_categories()
        self.stdout.write(self.style.SUCCESS(f'✓ {len(maintenance_categories)} categories created'))

        # Create Maintenance Requests
        self.stdout.write('Creating Maintenance Requests...')
        maintenance_requests = self._create_maintenance_requests(
            properties, maintenance_categories, accounts, period
        )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(maintenance_requests)} maintenance requests created'))

        # Create Invoices
        self.stdout.write('Creating Invoices...')
        invoices = self._create_invoices(properties, clients, accounts, period)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(invoices)} invoices created'))

        # Create Payments
        self.stdout.write('Creating Payments...')
        payments = self._create_payments(invoices, accounts, period)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(payments)} payments created'))

        self.stdout.write(self.style.SUCCESS('\n✅ Realistic data created successfully!'))
        self.stdout.write(self.style.SUCCESS('🎉 System is fully populated with integrated data!'))

    def _create_chart_of_accounts(self):
        """Create comprehensive chart of accounts"""
        accounts = []
        
        # Assets
        cash = Account.objects.create(
            code='1110', name='Cash', account_type='asset',
            opening_balance=Decimal('50000.00'), is_system=True
        )
        bank = Account.objects.create(
            code='1120', name='Bank Account', account_type='asset',
            opening_balance=Decimal('150000.00'), is_system=True
        )
        accounts_receivable = Account.objects.create(
            code='1130', name='Accounts Receivable', account_type='asset',
            opening_balance=Decimal('0.00'), is_system=True
        )
        buildings = Account.objects.create(
            code='1210', name='Buildings', account_type='asset',
            opening_balance=Decimal('2000000.00'), is_system=True
        )
        
        # Liabilities
        accounts_payable = Account.objects.create(
            code='2110', name='Accounts Payable', account_type='liability',
            opening_balance=Decimal('0.00'), is_system=True
        )
        
        # Equity
        owners_equity = Account.objects.create(
            code='3100', name="Owner's Equity", account_type='equity',
            opening_balance=Decimal('2200000.00'), is_system=True
        )
        
        # Revenue
        rental_revenue = Account.objects.create(
            code='4100', name='Rental Revenue', account_type='revenue',
            opening_balance=Decimal('0.00'), is_system=True
        )
        service_revenue = Account.objects.create(
            code='4200', name='Service Revenue', account_type='revenue',
            opening_balance=Decimal('0.00'), is_system=True
        )
        
        # Expenses
        maintenance_expense = Account.objects.create(
            code='5100', name='Maintenance Expense', account_type='expense',
            opening_balance=Decimal('0.00'), is_system=True
        )
        utilities_expense = Account.objects.create(
            code='5200', name='Utilities Expense', account_type='expense',
            opening_balance=Decimal('0.00'), is_system=True
        )
        insurance_expense = Account.objects.create(
            code='5300', name='Insurance Expense', account_type='expense',
            opening_balance=Decimal('0.00'), is_system=True
        )
        
        accounts = [cash, bank, accounts_receivable, buildings, accounts_payable,
                   owners_equity, rental_revenue, service_revenue, maintenance_expense,
                   utilities_expense, insurance_expense]
        
        return accounts

    def _create_property_types(self):
        """Create property types"""
        types_data = [
            {'name': 'Apartment', 'description': 'Residential apartment units'},
            {'name': 'Villa', 'description': 'Standalone residential villas'},
            {'name': 'Office', 'description': 'Commercial office spaces'},
            {'name': 'Shop', 'description': 'Retail shop spaces'},
            {'name': 'Warehouse', 'description': 'Industrial warehouse spaces'},
        ]
        
        types = []
        for data in types_data:
            types.append(PropertyType.objects.create(**data))
        
        return types

    def _create_owners(self):
        """Create property owners"""
        owners_data = [
            {
                'name': 'Michael Johnson',
                'email': 'michael.johnson@email.com',
                'phone': '+1-555-0101',
                'national_id': 'US-123456789',
                'address': '123 Park Avenue, New York, NY 10001',
                'city': 'New York',
                'country': 'United States',
            },
            {
                'name': 'Sarah Williams',
                'email': 'sarah.williams@email.com',
                'phone': '+1-555-0201',
                'national_id': 'US-234567890',
                'address': '456 Oak Street, Los Angeles, CA 90001',
                'city': 'Los Angeles',
                'country': 'United States',
            },
            {
                'name': 'David Brown',
                'email': 'david.brown@email.com',
                'phone': '+1-555-0301',
                'national_id': 'US-345678901',
                'address': '789 Maple Road, Chicago, IL 60601',
                'city': 'Chicago',
                'country': 'United States',
            },
            {
                'name': 'Emma Davis',
                'email': 'emma.davis@email.com',
                'phone': '+1-555-0401',
                'national_id': 'US-456789012',
                'address': '321 Pine Avenue, Houston, TX 77001',
                'city': 'Houston',
                'country': 'United States',
            },
        ]
        
        owners = []
        for data in owners_data:
            owners.append(Owner.objects.create(**data))
        
        return owners

    def _create_properties(self, owners, property_types):
        """Create properties"""
        properties_data = [
            {
                'title': 'Skyline Tower Apartment 501',
                'code': 'PROP-001',
                'property_type': property_types[0],  # Apartment
                'owner': owners[0],
                'address': '100 Skyline Drive, Unit 501, Manhattan, NY 10001',
                'city': 'New York',
                'district': 'Manhattan',
                'postal_code': '10001',
                'area_sqm': Decimal('111.48'),  # 1200 sqft = 111.48 sqm
                'bedrooms': 2,
                'bathrooms': 2,
                'purchase_price': Decimal('450000.00'),
                'market_value': Decimal('460000.00'),
                'rental_price_monthly': Decimal('3500.00'),
                'status': 'rented',
                'description': 'Luxury 2-bedroom apartment with city views',
                'latitude': Decimal('40.7589'),
                'longitude': Decimal('-73.9851'),
            },
            {
                'title': 'Beverly Hills Villa',
                'code': 'PROP-002',
                'property_type': property_types[1],  # Villa
                'owner': owners[1],
                'address': '234 Beverly Road, Beverly Hills, CA 90210',
                'city': 'Los Angeles',
                'district': 'Beverly Hills',
                'postal_code': '90210',
                'area_sqm': Decimal('418.06'),  # 4500 sqft
                'bedrooms': 5,
                'bathrooms': 4,
                'purchase_price': Decimal('2500000.00'),
                'market_value': Decimal('2550000.00'),
                'rental_price_monthly': Decimal('15000.00'),
                'status': 'rented',
                'description': 'Stunning luxury villa with pool and garden',
                'latitude': Decimal('34.0736'),
                'longitude': Decimal('-118.4004'),
                'has_pool': True,
                'has_garden': True,
            },
            {
                'title': 'Downtown Office Suite 1200',
                'code': 'PROP-003',
                'property_type': property_types[2],  # Office
                'owner': owners[0],
                'address': '555 Business Plaza, Suite 1200, Chicago, IL 60601',
                'city': 'Chicago',
                'district': 'Downtown',
                'postal_code': '60601',
                'area_sqm': Decimal('232.26'),  # 2500 sqft
                'purchase_price': Decimal('1200000.00'),
                'market_value': Decimal('1220000.00'),
                'rental_price_monthly': Decimal('8000.00'),
                'status': 'rented',
                'description': 'Premium office space in downtown business district',
                'latitude': Decimal('41.8781'),
                'longitude': Decimal('-87.6298'),
            },
            {
                'title': 'Riverside Retail Shop',
                'code': 'PROP-004',
                'property_type': property_types[3],  # Shop
                'owner': owners[2],
                'address': '789 Riverside Mall, Unit 45, Houston, TX 77001',
                'city': 'Houston',
                'district': 'Riverside',
                'postal_code': '77001',
                'area_sqm': Decimal('74.32'),  # 800 sqft
                'purchase_price': Decimal('350000.00'),
                'market_value': Decimal('360000.00'),
                'rental_price_monthly': Decimal('4500.00'),
                'status': 'rented',
                'description': 'High-traffic retail space in popular mall',
                'latitude': Decimal('29.7604'),
                'longitude': Decimal('-95.3698'),
            },
            {
                'title': 'Industrial Warehouse Unit B',
                'code': 'PROP-005',
                'property_type': property_types[4],  # Warehouse
                'owner': owners[3],
                'address': '1001 Industrial Park, Unit B, Phoenix, AZ 85001',
                'city': 'Phoenix',
                'district': 'Industrial Park',
                'postal_code': '85001',
                'area_sqm': Decimal('464.52'),  # 5000 sqft
                'purchase_price': Decimal('800000.00'),
                'market_value': Decimal('820000.00'),
                'rental_price_monthly': Decimal('6000.00'),
                'status': 'available',
                'description': 'Large warehouse with loading dock',
                'latitude': Decimal('33.4484'),
                'longitude': Decimal('-112.0740'),
            },
            {
                'title': 'Garden View Apartment 203',
                'code': 'PROP-006',
                'property_type': property_types[0],  # Apartment
                'owner': owners[1],
                'address': '456 Garden Street, Unit 203, San Francisco, CA 94102',
                'city': 'San Francisco',
                'district': 'Downtown',
                'postal_code': '94102',
                'area_sqm': Decimal('88.26'),  # 950 sqft
                'bedrooms': 1,
                'bathrooms': 1,
                'purchase_price': Decimal('380000.00'),
                'market_value': Decimal('390000.00'),
                'rental_price_monthly': Decimal('2800.00'),
                'status': 'rented',
                'description': 'Cozy 1-bedroom with garden access',
                'latitude': Decimal('37.7749'),
                'longitude': Decimal('-122.4194'),
                'has_garden': True,
            },
        ]
        
        properties = []
        for data in properties_data:
            properties.append(Property.objects.create(**data))
        
        return properties

    def _create_property_financials(self, properties, accounts, period):
        """Create property expenses and revenues"""
        # Get accounts
        maintenance_account = Account.objects.get(code='5100')
        utilities_account = Account.objects.get(code='5200')
        insurance_account = Account.objects.get(code='5300')
        rental_revenue_account = Account.objects.get(code='4100')
        cash_account = Account.objects.get(code='1110')
        
        for prop in properties[:4]:  # For rented properties
            # Create expenses
            PropertyExpense.objects.create(
                property=prop,
                expense_date=(timezone.now() - timedelta(days=15)).date(),
                expense_type='maintenance',
                amount=Decimal('500.00'),
                vendor='ABC Maintenance Co.',
                description='Monthly maintenance service'
            )
            
            PropertyExpense.objects.create(
                property=prop,
                expense_date=(timezone.now() - timedelta(days=10)).date(),
                expense_type='utilities',
                amount=Decimal('200.00'),
                vendor='City Utilities',
                description='Monthly utilities'
            )
            
            # Create revenue
            PropertyRevenue.objects.create(
                property=prop,
                revenue_date=(timezone.now() - timedelta(days=5)).date(),
                revenue_type='rent',
                amount=prop.rental_price_monthly,
                source='Monthly Rent',
                description=f'Rent payment for {prop.title}'
            )

    def _create_clients(self):
        """Create clients/tenants"""
        clients_data = [
            {
                'name': 'John Anderson',
                'email': 'john.anderson@email.com',
                'phone': '+1-555-1001',
                'national_id': 'US-567890123',
                'address': '111 Client Street, Apt 5, New York, NY 10002',
                'city': 'New York',
                'country': 'United States',
            },
            {
                'name': 'Lisa Martinez',
                'email': 'lisa.martinez@email.com',
                'phone': '+1-555-2001',
                'national_id': 'US-678901234',
                'address': '222 Tenant Avenue, Los Angeles, CA 90002',
                'city': 'Los Angeles',
                'country': 'United States',
            },
            {
                'name': 'Robert Taylor',
                'email': 'robert.taylor@email.com',
                'phone': '+1-555-3001',
                'national_id': 'US-789012345',
                'address': '333 Renter Road, Chicago, IL 60602',
                'city': 'Chicago',
                'country': 'United States',
            },
            {
                'name': 'Jennifer Wilson',
                'email': 'jennifer.wilson@email.com',
                'phone': '+1-555-4001',
                'national_id': 'US-890123456',
                'address': '444 Lessee Lane, Houston, TX 77002',
                'city': 'Houston',
                'country': 'United States',
            },
            {
                'name': 'Tech Solutions Inc.',
                'email': 'contact@techsolutions.com',
                'phone': '+1-555-5001',
                'national_id': 'COMPANY-901234567',
                'address': '555 Business Center, San Francisco, CA 94103',
                'city': 'San Francisco',
                'country': 'United States',
            },
        ]
        
        clients = []
        for data in clients_data:
            clients.append(Client.objects.create(**data))
        
        return clients

    def _create_contracts(self, properties, clients, accounts, period):
        """Create rental contracts with payments"""
        contracts_data = [
            {
                'contract_number': 'CNT-2025-001',
                'property': properties[0],  # Skyline Tower Apartment
                'client': clients[0],  # John Anderson
                'start_date': (timezone.now() - timedelta(days=180)).date(),
                'end_date': (timezone.now() + timedelta(days=185)).date(),
                'rent_amount': properties[0].rental_price_monthly,
                'security_deposit': properties[0].rental_price_monthly * 2,
                'payment_frequency': 'monthly',
            },
            {
                'contract_number': 'CNT-2025-002',
                'property': properties[1],  # Beverly Hills Villa
                'client': clients[1],  # Lisa Martinez
                'start_date': (timezone.now() - timedelta(days=90)).date(),
                'end_date': (timezone.now() + timedelta(days=275)).date(),
                'rent_amount': properties[1].rental_price_monthly,
                'security_deposit': properties[1].rental_price_monthly * 2,
                'payment_frequency': 'monthly',
            },
            {
                'contract_number': 'CNT-2025-003',
                'property': properties[2],  # Downtown Office
                'client': clients[4],  # Tech Solutions Inc.
                'start_date': (timezone.now() - timedelta(days=60)).date(),
                'end_date': (timezone.now() + timedelta(days=305)).date(),
                'rent_amount': properties[2].rental_price_monthly,
                'security_deposit': properties[2].rental_price_monthly * 3,
                'payment_frequency': 'monthly',
            },
            {
                'contract_number': 'CNT-2025-004',
                'property': properties[3],  # Riverside Retail Shop
                'client': clients[3],  # Jennifer Wilson
                'start_date': (timezone.now() - timedelta(days=150)).date(),
                'end_date': (timezone.now() + timedelta(days=215)).date(),
                'rent_amount': properties[3].rental_price_monthly,
                'security_deposit': properties[3].rental_price_monthly * 2,
                'payment_frequency': 'monthly',
            },
            {
                'contract_number': 'CNT-2025-005',
                'property': properties[5],  # Garden View Apartment
                'client': clients[2],  # Robert Taylor
                'start_date': (timezone.now() - timedelta(days=30)).date(),
                'end_date': (timezone.now() + timedelta(days=335)).date(),
                'rent_amount': properties[5].rental_price_monthly,
                'security_deposit': properties[5].rental_price_monthly * 2,
                'payment_frequency': 'monthly',
            },
        ]
        
        contracts = []
        rental_revenue_account = Account.objects.get(code='4100')
        accounts_receivable = Account.objects.get(code='1130')
        cash_account = Account.objects.get(code='1110')
        
        for data in contracts_data:
            contract = Contract.objects.create(**data)
            contracts.append(contract)
            
            # Create contract payments (2 months paid)
            for i in range(2):
                payment_date = contract.start_date + timedelta(days=30 * i)
                ContractPayment.objects.create(
                    contract=contract,
                    payment_date=payment_date,
                    amount=contract.rent_amount,
                    payment_method='bank_transfer',
                    status='paid'
                )
                
                # Create journal entry for rent payment
                entry = JournalEntry.objects.create(
                    entry_number=f'JE-2025-{1000 + len(contracts) * 2 + i}',
                    entry_date=payment_date,
                    entry_type='automated',
                    description=f'Rent payment - {contract.property.title}',
                    is_posted=True,
                    property=contract.property,
                    contract=contract,
                    period=period
                )
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=cash_account,
                    debit_amount=contract.rent_amount,
                    credit_amount=Decimal('0.00'),
                    description='Cash received'
                )
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=rental_revenue_account,
                    debit_amount=Decimal('0.00'),
                    credit_amount=contract.rent_amount,
                    description='Rental revenue'
                )
        
        return contracts

    def _create_maintenance_categories(self):
        """Create maintenance categories"""
        categories_data = [
            {'name': 'Plumbing', 'description': 'Plumbing repairs and services'},
            {'name': 'Electrical', 'description': 'Electrical repairs and installations'},
            {'name': 'HVAC', 'description': 'Heating, ventilation, and air conditioning'},
            {'name': 'Painting', 'description': 'Interior and exterior painting'},
            {'name': 'Carpentry', 'description': 'Wood work and repairs'},
            {'name': 'Cleaning', 'description': 'General cleaning and sanitation'},
        ]
        
        categories = []
        for data in categories_data:
            categories.append(MaintenanceCategory.objects.create(**data))
        
        return categories

    def _create_maintenance_requests(self, properties, categories, accounts, period):
        """Create maintenance requests"""
        maintenance_expense_account = Account.objects.get(code='5100')
        cash_account = Account.objects.get(code='1110')
        
        requests_data = [
            {
                'property': properties[0],
                'category': categories[0],  # Plumbing
                'title': 'Leaking Kitchen Faucet',
                'description': 'Kitchen faucet is dripping continuously',
                'priority': 'high',
                'status': 'completed',
                'estimated_cost': Decimal('150.00'),
                'actual_cost': Decimal('175.00'),
            },
            {
                'request_number': 'MNT-2025-002',
                'property': properties[1],
                'category': categories[2],  # HVAC
                'title': 'AC Unit Not Cooling',
                'description': 'Air conditioning unit not cooling properly',
                'priority': 'urgent',
                'status': 'in_progress',
                'estimated_cost': Decimal('500.00'),
            },
            {
                'request_number': 'MNT-2025-003',
                'property': properties[2],
                'category': categories[1],  # Electrical
                'title': 'Office Light Fixtures',
                'description': 'Replace fluorescent bulbs in conference room',
                'priority': 'medium',
                'status': 'completed',
                'estimated_cost': Decimal('200.00'),
                'actual_cost': Decimal('185.00'),
            },
            {
                'request_number': 'MNT-2025-004',
                'property': properties[3],
                'category': categories[3],  # Painting
                'title': 'Exterior Wall Repaint',
                'description': 'Shop exterior needs repainting',
                'priority': 'low',
                'status': 'pending',
                'estimated_cost': Decimal('800.00'),
            },
            {
                'request_number': 'MNT-2025-005',
                'property': properties[0],
                'category': categories[5],  # Cleaning
                'title': 'Deep Cleaning Service',
                'description': 'Post-renovation deep cleaning',
                'priority': 'medium',
                'status': 'completed',
                'estimated_cost': Decimal('300.00'),
                'actual_cost': Decimal('300.00'),
            },
        ]
        
        requests = []
        for data in requests_data:
            request = MaintenanceRequest.objects.create(**data)
            requests.append(request)
            
            # Create journal entry for completed maintenance
            if request.status == 'completed' and request.actual_cost:
                entry = JournalEntry.objects.create(
                    entry_number=f'JE-2025-{2000 + len(requests)}',
                    entry_date=timezone.now().date(),
                    entry_type='automated',
                    description=f'Maintenance expense - {request.title}',
                    is_posted=True,
                    property=request.property,
                    period=period
                )
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=maintenance_expense_account,
                    debit_amount=request.actual_cost,
                    credit_amount=Decimal('0.00'),
                    description='Maintenance expense'
                )
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=cash_account,
                    debit_amount=Decimal('0.00'),
                    credit_amount=request.actual_cost,
                    description='Cash paid'
                )
        
        return requests

    def _create_invoices(self, properties, clients, accounts, period):
        """Create invoices"""
        accounts_receivable = Account.objects.get(code='1130')
        rental_revenue_account = Account.objects.get(code='4100')
        service_revenue_account = Account.objects.get(code='4200')
        
        invoices_data = [
            {
                'property': properties[0],
                'invoice_type': 'rent',
                'status': 'paid',
                'invoice_date': (timezone.now() - timedelta(days=30)).date(),
                'due_date': (timezone.now() - timedelta(days=25)).date(),
            },
            {
                'property': properties[1],
                'invoice_type': 'rent',
                'status': 'issued',
                'invoice_date': timezone.now().date(),
                'due_date': (timezone.now() + timedelta(days=15)).date(),
            },
            {
                'property': properties[2],
                'invoice_type': 'service',
                'status': 'partial',
                'invoice_date': (timezone.now() - timedelta(days=20)).date(),
                'due_date': (timezone.now() - timedelta(days=5)).date(),
            },
        ]
        
        invoices = []
        for idx, data in enumerate(invoices_data):
            invoice = Invoice.objects.create(
                invoice_number=f'INV-2025-{1001 + idx}',
                **data,
                subtotal=Decimal('0.00'),
                tax_amount=Decimal('0.00'),
                discount_amount=Decimal('0.00'),
                total_amount=Decimal('0.00'),
                paid_amount=Decimal('0.00')
            )
            
            # Add invoice items
            if data['invoice_type'] == 'rent':
                amount = data['property'].rental_price_monthly
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=f"Monthly rent - {data['property'].title}",
                    quantity=1,
                    unit_price=amount,
                    tax_rate=Decimal('0.00'),
                    discount_rate=Decimal('0.00'),
                    total=amount
                )
            else:
                amount = Decimal('1000.00')
                tax = amount * Decimal('0.10')
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description='Facility management services',
                    quantity=1,
                    unit_price=amount,
                    tax_rate=Decimal('10.00'),
                    discount_rate=Decimal('0.00'),
                    total=amount + tax
                )
            
            # Calculate totals
            items = invoice.items.all()
            subtotal = sum(item.quantity * item.unit_price for item in items)
            tax = sum(item.quantity * item.unit_price * (item.tax_rate / 100) for item in items)
            
            invoice.subtotal = subtotal
            invoice.tax_amount = tax
            invoice.total_amount = subtotal + tax - invoice.discount_amount
            
            if data['status'] == 'paid':
                invoice.paid_amount = invoice.total_amount
            elif data['status'] == 'partial':
                invoice.paid_amount = invoice.total_amount / 2
            
            invoice.save()
            invoices.append(invoice)
        
        return invoices

    def _create_payments(self, invoices, accounts, period):
        """Create payments for invoices"""
        cash_account = Account.objects.get(code='1110')
        accounts_receivable = Account.objects.get(code='1130')
        
        payments = []
        payment_num = 1001
        
        for invoice in invoices:
            if invoice.status in ['paid', 'partial']:
                payment = Payment.objects.create(
                    payment_number=f'RCV-2025-{payment_num}',
                    payment_type='receipt',
                    payment_date=invoice.invoice_date + timedelta(days=5),
                    payment_method='bank_transfer',
                    amount=invoice.paid_amount,
                    invoice=invoice
                )
                payments.append(payment)
                payment_num += 1
                
                # Create journal entry
                entry = JournalEntry.objects.create(
                    entry_number=f'JE-2025-{3000 + len(payments)}',
                    entry_date=payment.payment_date,
                    entry_type='automated',
                    description=f'Payment received - {invoice.invoice_number}',
                    is_posted=True,
                    property=invoice.property,
                    period=period
                )
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=cash_account,
                    debit_amount=payment.amount,
                    credit_amount=Decimal('0.00'),
                    description='Cash received'
                )
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=accounts_receivable,
                    debit_amount=Decimal('0.00'),
                    credit_amount=payment.amount,
                    description='Accounts receivable'
                )
        
        return payments
