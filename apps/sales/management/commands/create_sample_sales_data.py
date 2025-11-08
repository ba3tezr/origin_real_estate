from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.sales.models import Buyer, PropertyReservation, SalesContract, SalesPaymentPlan, SalesPayment
from apps.properties.models import Property
from apps.owners.models import Owner
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample sales data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating sample sales data...'))
        
        # Get or create a user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING('No users found. Please create a superuser first.'))
            return
        
        # Get some properties
        properties = Property.objects.filter(status='available')[:3]
        if not properties:
            self.stdout.write(self.style.WARNING('No available properties found.'))
            return
        
        # Get an owner
        owner = Owner.objects.first()
        if not owner:
            self.stdout.write(self.style.WARNING('No owners found.'))
            return
        
        # Create Buyers
        buyers_data = [
            {
                'buyer_type': 'individual',
                'name': 'Ahmed Mohamed',
                'phone': '+201234567890',
                'email': 'ahmed.mohamed@example.com',
                'national_id': '29012010101234',
                'address': '15 Tahrir Street',
                'city': 'Cairo',
                'country': 'Egypt',
                'annual_income': Decimal('250000'),
                'credit_score': 720,
                'is_qualified': True,
            },
            {
                'buyer_type': 'investor',
                'name': 'Sarah Johnson',
                'phone': '+201987654321',
                'email': 'sarah.johnson@example.com',
                'national_id': '29203020202345',
                'address': '25 Nile Street',
                'city': 'Giza',
                'country': 'Egypt',
                'annual_income': Decimal('500000'),
                'credit_score': 780,
                'financing_approved': True,
                'financing_institution': 'National Bank of Egypt',
                'approved_loan_amount': Decimal('1000000'),
                'is_qualified': True,
            },
            {
                'buyer_type': 'company',
                'name': 'Tech Innovations Ltd',
                'phone': '+201555444333',
                'email': 'contact@techinnovations.com',
                'national_id': '12345678901234',
                'address': 'Smart Village',
                'city': '6th October',
                'country': 'Egypt',
                'company_name': 'Tech Innovations Ltd',
                'company_registration': 'CR-2020-12345',
                'tax_id': 'TAX-67890',
                'annual_income': Decimal('2000000'),
                'credit_score': 800,
                'is_qualified': True,
            }
        ]
        
        buyers = []
        for buyer_data in buyers_data:
            buyer, created = Buyer.objects.get_or_create(
                national_id=buyer_data['national_id'],
                defaults=buyer_data
            )
            buyers.append(buyer)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created buyer: {buyer.name}'))
        
        # Create Reservations
        if len(properties) > 0 and len(buyers) > 0:
            reservation, created = PropertyReservation.objects.get_or_create(
                property=properties[0],
                buyer=buyers[0],
                defaults={
                    'expiry_date': timezone.now().date() + timedelta(days=7),
                    'reservation_amount': Decimal('10000'),
                    'payment_method': 'bank_transfer',
                    'payment_reference': 'TRX-2024-001',
                    'status': 'approved',
                    'reserved_by': user,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created reservation: {reservation.reservation_number}'))
        
        # Create Sales Contract
        if len(properties) > 1 and len(buyers) > 1:
            contract, created = SalesContract.objects.get_or_create(
                property=properties[1],
                buyer=buyers[1],
                defaults={
                    'seller': owner,
                    'sale_price': Decimal('2500000'),
                    'down_payment': Decimal('500000'),
                    'financed_amount': Decimal('1000000'),
                    'has_financing': True,
                    'financing_institution': 'National Bank of Egypt',
                    'financing_percentage': Decimal('40'),
                    'financing_years': 15,
                    'contract_date': timezone.now().date(),
                    'expected_handover_date': timezone.now().date() + timedelta(days=90),
                    'has_installments': True,
                    'number_of_installments': 24,
                    'installment_frequency': 'monthly',
                    'status': 'signed',
                    'created_by': user,
                    'terms_and_conditions': 'Standard terms and conditions apply.',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created contract: {contract.contract_number}'))
                
                # Create Payment Plans
                remaining_amount = contract.sale_price - contract.down_payment - contract.financed_amount
                installment_amount = remaining_amount / contract.number_of_installments
                
                for i in range(1, contract.number_of_installments + 1):
                    due_date = timezone.now().date() + timedelta(days=30*i)
                    SalesPaymentPlan.objects.get_or_create(
                        sales_contract=contract,
                        installment_number=i,
                        defaults={
                            'due_date': due_date,
                            'amount': installment_amount,
                        }
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Created {contract.number_of_installments} payment plans'))
                
                # Create Down Payment
                payment, created = SalesPayment.objects.get_or_create(
                    sales_contract=contract,
                    payment_type='down_payment',
                    defaults={
                        'amount': contract.down_payment,
                        'payment_date': timezone.now().date(),
                        'payment_method': 'bank_transfer',
                        'reference_number': 'PAY-2024-001',
                        'status': 'completed',
                        'received_by': user,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created payment: {payment.receipt_number}'))
        
        self.stdout.write(self.style.SUCCESS('Sample sales data created successfully!'))
