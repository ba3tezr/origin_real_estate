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
    help = 'Fix and create realistic sample sales data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Fixing sample sales data...'))
        
        # Clear existing test data
        self.stdout.write('Clearing existing test data...')
        PropertyReservation.objects.all().delete()
        SalesPayment.objects.all().delete()
        SalesPaymentPlan.objects.all().delete()
        SalesContract.objects.all().delete()
        Buyer.objects.all().delete()
        
        # Get or create a user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING('No users found. Please create a superuser first.'))
            return
        
        # Get some properties for sale (including rented ones that can be sold)
        properties = Property.objects.filter(is_for_sale=True)[:5]
        if not properties.exists() or properties.count() < 5:
            self.stdout.write(self.style.WARNING('Not enough properties for sale. Marking some properties as for sale...'))
            # Mark some properties as for sale (can be available OR rented - owners can sell rented properties)
            for prop in Property.objects.all()[:5]:
                prop.is_for_sale = True
                # Set realistic sale price based on property type
                if prop.property_type.name in ['Apartment', 'Villa', 'Studio']:
                    prop.sale_price = Decimal(str(prop.rental_price_monthly * 200))  # ~16 years rent
                elif prop.property_type.name in ['Office', 'Shop']:
                    prop.sale_price = Decimal(str(prop.rental_price_monthly * 150))  # ~12 years rent
                elif prop.property_type.name in ['Warehouse', 'Land']:
                    prop.sale_price = Decimal(str(prop.rental_price_monthly * 250))  # ~20 years rent
                else:
                    prop.sale_price = Decimal(str(prop.rental_price_monthly * 180))
                prop.save()
                self.stdout.write(f'  Marked {prop.code} for sale at {prop.sale_price} EGP')
            properties = Property.objects.filter(is_for_sale=True)[:5]
        
        # Get an owner
        owner = Owner.objects.first()
        if not owner:
            self.stdout.write(self.style.WARNING('No owners found.'))
            return
        
        # Create Realistic Buyers
        buyers_data = [
            {
                'buyer_type': 'individual',
                'name': 'محمد أحمد السيد',
                'phone': '+201012345678',
                'email': 'mohamed.ahmed@example.com',
                'national_id': '29012011234567',
                'address': '15 شارع الجامعة، المعادي',
                'city': 'القاهرة',
                'country': 'مصر',
                'annual_income': Decimal('300000'),
                'credit_score': 750,
                'is_qualified': True,
            },
            {
                'buyer_type': 'investor',
                'name': 'سارة عبدالله حسن',
                'phone': '+201098765432',
                'email': 'sara.abdallah@example.com',
                'national_id': '29203021112233',
                'address': '42 شارع النيل، المهندسين',
                'city': 'الجيزة',
                'country': 'مصر',
                'annual_income': Decimal('600000'),
                'credit_score': 800,
                'financing_approved': True,
                'financing_institution': 'البنك الأهلي المصري',
                'approved_loan_amount': Decimal('2000000'),
                'is_qualified': True,
            },
            {
                'buyer_type': 'company',
                'name': 'شركة المستقبل للاستثمار العقاري',
                'phone': '+201555444333',
                'email': 'info@future-invest.com',
                'national_id': '12345678909876',
                'address': 'مدينة نصر، القاهرة',
                'city': 'القاهرة',
                'country': 'مصر',
                'company_name': 'شركة المستقبل للاستثمار العقاري',
                'company_registration': 'CR-2020-98765',
                'tax_id': 'TAX-12345',
                'annual_income': Decimal('5000000'),
                'credit_score': 820,
                'is_qualified': True,
            },
            {
                'buyer_type': 'individual',
                'name': 'خالد محمود عثمان',
                'phone': '+201123456789',
                'email': 'khaled.mahmoud@example.com',
                'national_id': '28905011234568',
                'address': '8 شارع الشهداء، الإسكندرية',
                'city': 'الإسكندرية',
                'country': 'مصر',
                'annual_income': Decimal('450000'),
                'credit_score': 710,
                'is_qualified': True,
            },
        ]
        
        buyers = []
        for buyer_data in buyers_data:
            buyer = Buyer.objects.create(**buyer_data)
            buyers.append(buyer)
            self.stdout.write(self.style.SUCCESS(f'Created buyer: {buyer.name}'))
        
        # Create Realistic Reservations (10% of sale price)
        if properties.exists() and buyers:
            for i, prop in enumerate(properties[:3]):
                buyer = buyers[i % len(buyers)]
                reservation_amount = (prop.sale_price * Decimal('0.10')).quantize(Decimal('0.01'))
                
                reservation = PropertyReservation.objects.create(
                    property=prop,
                    buyer=buyer,
                    expiry_date=timezone.now().date() + timedelta(days=14),
                    reservation_amount=reservation_amount,
                    payment_method='bank_transfer',
                    payment_reference=f'TRX-2025-{str(i+1).zfill(3)}',
                    status='pending' if i == 0 else 'approved',
                    reserved_by=user,
                    notes=f'حجز عقار {prop.code} بمبلغ {reservation_amount} جنيه (10% من سعر البيع)'
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Created reservation: {reservation.reservation_number} - '
                    f'{prop.code} - {reservation_amount} EGP'
                ))
        
        # Create Realistic Sales Contract
        if len(properties) > 3 and len(buyers) > 1:
            prop = properties[3]
            buyer = buyers[1]
            sale_price = prop.sale_price
            down_payment = (sale_price * Decimal('0.20')).quantize(Decimal('0.01'))  # 20%
            financed_amount = (sale_price * Decimal('0.50')).quantize(Decimal('0.01'))  # 50%
            remaining_amount = sale_price - down_payment - financed_amount  # 30%
            
            contract = SalesContract.objects.create(
                property=prop,
                buyer=buyer,
                seller=owner,
                sale_price=sale_price,
                down_payment=down_payment,
                financed_amount=financed_amount,
                has_financing=True,
                financing_institution='البنك الأهلي المصري',
                financing_percentage=Decimal('50'),
                financing_years=15,
                contract_date=timezone.now().date(),
                signing_date=timezone.now().date(),
                expected_handover_date=timezone.now().date() + timedelta(days=120),
                has_installments=True,
                number_of_installments=36,  # 3 years
                installment_frequency='monthly',
                status='signed',
                created_by=user,
                terms_and_conditions='شروط وأحكام عقد بيع عقار قياسية',
                special_conditions='تم الاتفاق على تسليم العقار خلال 4 أشهر من توقيع العقد'
            )
            self.stdout.write(self.style.SUCCESS(f'Created contract: {contract.contract_number}'))
            self.stdout.write(self.style.SUCCESS(
                f'  Sale Price: {sale_price} EGP\n'
                f'  Down Payment (20%): {down_payment} EGP\n'
                f'  Financed (50%): {financed_amount} EGP\n'
                f'  Installments (30%): {remaining_amount} EGP over 36 months'
            ))
            
            # Create Payment Plans
            installment_amount = (remaining_amount / contract.number_of_installments).quantize(Decimal('0.01'))
            
            for i in range(1, contract.number_of_installments + 1):
                due_date = timezone.now().date() + timedelta(days=30*i)
                SalesPaymentPlan.objects.create(
                    sales_contract=contract,
                    installment_number=i,
                    due_date=due_date,
                    amount=installment_amount,
                )
            
            self.stdout.write(self.style.SUCCESS(
                f'Created {contract.number_of_installments} payment plans of {installment_amount} EGP each'
            ))
            
            # Create Down Payment
            payment = SalesPayment.objects.create(
                sales_contract=contract,
                payment_type='down_payment',
                amount=down_payment,
                payment_date=timezone.now().date(),
                payment_method='bank_transfer',
                reference_number='PAY-2025-001',
                status='completed',
                received_by=user,
                notes=f'دفعة مقدمة 20% من إجمالي سعر العقار {sale_price} جنيه'
            )
            self.stdout.write(self.style.SUCCESS(f'Created down payment: {payment.receipt_number} - {down_payment} EGP'))
            
            # Create first 2 installment payments
            payment_plans = SalesPaymentPlan.objects.filter(
                sales_contract=contract
            ).order_by('installment_number')[:2]
            
            for idx, plan in enumerate(payment_plans):
                payment = SalesPayment.objects.create(
                    sales_contract=contract,
                    payment_plan=plan,
                    payment_type='installment',
                    amount=plan.amount,
                    payment_date=timezone.now().date() - timedelta(days=(2-idx)*30),
                    payment_method='bank_transfer',
                    reference_number=f'PAY-2025-{str(idx+2).zfill(3)}',
                    status='completed',
                    received_by=user,
                    notes=f'القسط رقم {plan.installment_number} من أصل {contract.number_of_installments}'
                )
                plan.is_paid = True
                plan.payment_date = payment.payment_date
                plan.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Created installment payment #{plan.installment_number}: {payment.receipt_number} - {plan.amount} EGP'
                ))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Realistic sample sales data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nSummary:'))
        self.stdout.write(f'  - Buyers: {Buyer.objects.count()}')
        self.stdout.write(f'  - Reservations: {PropertyReservation.objects.count()}')
        self.stdout.write(f'  - Contracts: {SalesContract.objects.count()}')
        self.stdout.write(f'  - Payment Plans: {SalesPaymentPlan.objects.count()}')
        self.stdout.write(f'  - Payments: {SalesPayment.objects.count()}')
