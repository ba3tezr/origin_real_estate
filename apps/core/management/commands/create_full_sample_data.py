"""
Django management command to create comprehensive sample data for all modules
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import random

from apps.owners.models import Owner
from apps.clients.models import Client
from apps.properties.models import Property, PropertyType
from apps.contracts.models import Contract
from apps.maintenance.models import MaintenanceRequest, MaintenanceCategory


class Command(BaseCommand):
    help = 'Creates comprehensive sample data for all modules'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data creation...'))
        
        # Create superuser if not exists
        self.create_users()
        
        # Create owners
        owners = self.create_owners()
        
        # Create clients
        clients = self.create_clients()
        
        # Create property types
        property_types = self.create_property_types()
        
        # Create properties
        properties = self.create_properties(owners, property_types)
        
        # Create maintenance categories
        maintenance_categories = self.create_maintenance_categories()
        
        # Create contracts
        contracts = self.create_contracts(properties, clients)
        
        # Create maintenance requests
        self.create_maintenance_requests(properties, maintenance_categories)
        
        self.stdout.write(self.style.SUCCESS('✅ All sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Created:'))
        self.stdout.write(f'  - {len(owners)} Owners')
        self.stdout.write(f'  - {len(clients)} Clients')
        self.stdout.write(f'  - {len(property_types)} Property Types')
        self.stdout.write(f'  - {len(properties)} Properties')
        self.stdout.write(f'  - {len(contracts)} Contracts')
        self.stdout.write(f'  - {len(maintenance_categories)} Maintenance Categories')
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')

    def create_users(self):
        """Create admin user"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@originapp.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
        else:
            self.stdout.write('✓ Admin user already exists')

    def create_owners(self):
        """Create sample owners"""
        self.stdout.write('Creating owners...')
        
        owners_data = [
            {
                'name': 'محمد أحمد حسن',
                'phone': '+201012345678',
                'email': 'mohammed.ahmed@email.com',
                'national_id': '28501012345678',
                'address': 'القاهرة، مدينة نصر، شارع عباس العقاد',
                'city': 'القاهرة',
                'notes': 'مالك موثوق، يفضل التواصل الهاتفي'
            },
            {
                'name': 'فاطمة علي محمود',
                'phone': '+201023456789',
                'email': 'fatima.ali@email.com',
                'national_id': '28502023456789',
                'address': 'الإسكندرية، سموحة، شارع فوزي معاذ',
                'city': 'الإسكندرية',
                'notes': 'تمتلك عدة عقارات تجارية'
            },
            {
                'name': 'خالد عبدالرحمن سليم',
                'phone': '+201034567890',
                'email': 'khaled.abdulrahman@email.com',
                'national_id': '28503034567890',
                'address': 'الجيزة، المهندسين، شارع جامعة الدول العربية',
                'city': 'الجيزة',
                'notes': 'يفضل العقود طويلة الأمد'
            },
            {
                'name': 'نورا محمد إبراهيم',
                'phone': '+201045678901',
                'email': 'noura.mohamed@email.com',
                'national_id': '28504045678901',
                'address': 'الشرقية، الزقازيق، شارع فاروق',
                'city': 'الزقازيق',
                'notes': 'متعاونة جداً في الصيانة'
            },
            {
                'name': 'عبدالله سعد عثمان',
                'phone': '+201056789012',
                'email': 'abdullah.saad@email.com',
                'national_id': '28505056789012',
                'address': 'المنصورة، شارع الجيش، برج النيل',
                'city': 'المنصورة',
                'notes': 'مستثمر عقاري نشط'
            }
        ]
        
        owners = []
        for data in owners_data:
            owner, created = Owner.objects.get_or_create(
                national_id=data['national_id'],
                defaults=data
            )
            owners.append(owner)
            if created:
                self.stdout.write(f'  ✓ Created owner: {owner.name}')
        
        return owners

    def create_clients(self):
        """Create sample clients"""
        self.stdout.write('Creating clients...')
        
        clients_data = [
            {
                'name': 'أحمد عبدالله حسين',
                'phone': '+201067890123',
                'email': 'ahmed.hussein@email.com',
                'national_id': '29001067890123',
                'address': 'القاهرة، التجمع الخامس، الحي الأول',
                'city': 'القاهرة',
                'notes': 'عميل ممتاز، ملتزم بالدفع'
            },
            {
                'name': 'سارة حسن علي',
                'phone': '+201078901234',
                'email': 'sarah.hassan@email.com',
                'national_id': '29002078901234',
                'address': 'الإسكندرية، ميامي، شارع الهدى',
                'city': 'الإسكندرية',
                'notes': 'تبحث عن عقار سكني'
            },
            {
                'name': 'يوسف محمد رشاد',
                'phone': '+201089012345',
                'email': 'yousef.rashad@email.com',
                'national_id': '29003089012345',
                'address': 'المنيا، شارع الجلاء',
                'city': 'المنيا',
                'notes': 'مهتم بالعقارات التجارية'
            },
            {
                'name': 'ريم عبدالعزيز فاروق',
                'phone': '+201090123456',
                'email': 'reem.farouk@email.com',
                'national_id': '29004090123456',
                'address': 'طنطا، شارع الجلاء، برج النصر',
                'city': 'طنطا',
                'notes': 'عقد جديد، بداية ممتازة'
            },
            {
                'name': 'ماجد سالم مصطفى',
                'phone': '+201101234567',
                'email': 'majed.salem@email.com',
                'national_id': '29005101234567',
                'address': 'أسيوط، شارع النيل',
                'city': 'أسيوط',
                'notes': 'صاحب شركة، يحتاج مكتب'
            },
            {
                'name': 'ليلى أحمد صلاح',
                'phone': '+201112345678',
                'email': 'layla.salah@email.com',
                'national_id': '29006112345678',
                'address': 'القاهرة، مصر الجديدة، شارع الحجاز',
                'city': 'القاهرة',
                'notes': 'مستأجرة موثوقة منذ سنوات'
            },
            {
                'name': 'فهد عبدالرحمن زكي',
                'phone': '+201123456789',
                'email': 'fahad.zaki@email.com',
                'national_id': '29007123456789',
                'address': 'الجيزة، الدقي، شارع التحرير',
                'city': 'الجيزة',
                'notes': 'يبحث عن شقة عائلية'
            },
            {
                'name': 'منى خالد يوسف',
                'phone': '+201134567890',
                'email': 'mona.yousef@email.com',
                'national_id': '29008134567890',
                'address': 'الأقصر، شارع الكرنك',
                'city': 'الأقصر',
                'notes': 'تفضل الشقق المفروشة'
            }
        ]
        
        clients = []
        for data in clients_data:
            client, created = Client.objects.get_or_create(
                national_id=data['national_id'],
                defaults=data
            )
            clients.append(client)
            if created:
                self.stdout.write(f'  ✓ Created client: {client.name}')
        
        return clients

    def create_property_types(self):
        """Create property types"""
        self.stdout.write('Creating property types...')
        
        types_data = [
            {'name': 'شقة سكنية', 'description': 'شقق سكنية للإيجار أو البيع'},
            {'name': 'فيلا', 'description': 'فلل سكنية فاخرة'},
            {'name': 'مكتب تجاري', 'description': 'مكاتب للشركات والأعمال'},
            {'name': 'محل تجاري', 'description': 'محلات تجارية في مواقع حيوية'},
            {'name': 'مستودع', 'description': 'مستودعات للتخزين'},
            {'name': 'أرض', 'description': 'أراضي للبناء أو الاستثمار'},
            {'name': 'عمارة سكنية', 'description': 'عمائر سكنية متعددة الطوابق'},
        ]
        
        types = []
        for data in types_data:
            prop_type, created = PropertyType.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            types.append(prop_type)
            if created:
                self.stdout.write(f'  ✓ Created type: {prop_type.name}')
        
        return types

    def create_properties(self, owners, property_types):
        """Create sample properties"""
        self.stdout.write('Creating properties...')
        
        properties_data = [
            {
                'title': 'شقة فاخرة 3 غرف - حي الملك فهد',
                'code': 'RYD-APT-001',
                'address': 'الرياض، حي الملك فهد، شارع التخصصي',
                'city': 'الرياض',
                'area_sqm': Decimal('180.00'),
                'bedrooms': 3,
                'bathrooms': 2,
                'description': 'شقة فاخرة مع إطلالة رائعة، قريبة من المدارس والخدمات',
                'purchase_price': Decimal('450000.00'),
                'rental_price_monthly': Decimal('3500.00'),
                'type_index': 0,  # شقة سكنية
                'owner_index': 0,
                'is_active': True
            },
            {
                'title': 'فيلا دوبلكس فخمة - حي الياسمين',
                'code': 'RYD-VIL-002',
                'address': 'الرياض، حي الياسمين، شارع الورود',
                'city': 'الرياض',
                'area_sqm': Decimal('400.00'),
                'bedrooms': 5,
                'bathrooms': 4,
                'description': 'فيلا دوبلكس راقية مع حديقة واسعة وموقف سيارات',
                'purchase_price': Decimal('1200000.00'),
                'rental_price_monthly': Decimal('6000.00'),
                'type_index': 1,  # فيلا
                'owner_index': 0,
                'is_active': True
            },
            {
                'title': 'مكتب تجاري - برج الفيصلية',
                'code': 'RYD-OFF-003',
                'address': 'الرياض، برج الفيصلية، الدور 15',
                'city': 'الرياض',
                'area_sqm': Decimal('120.00'),
                'bedrooms': 0,
                'bathrooms': 1,
                'description': 'مكتب تجاري في موقع مرموق مع إطلالة بانورامية',
                'purchase_price': Decimal('300000.00'),
                'rental_price_monthly': Decimal('5000.00'),
                'type_index': 2,  # مكتب
                'owner_index': 1,
                'is_active': True
            },
            {
                'title': 'محل تجاري - شارع التحلية',
                'code': 'JED-SHP-004',
                'address': 'جدة، شارع التحلية، بجوار مول العرب',
                'city': 'جدة',
                'area_sqm': Decimal('80.00'),
                'bedrooms': 0,
                'bathrooms': 1,
                'description': 'محل في موقع حيوي جداً، مناسب لجميع الأنشطة التجارية',
                'purchase_price': Decimal('250000.00'),
                'rental_price_monthly': Decimal('8000.00'),
                'type_index': 3,  # محل
                'owner_index': 1,
                'is_active': True
            },
            {
                'title': 'شقة عصرية غرفتين - حي النزهة',
                'code': 'JED-APT-005',
                'address': 'جدة، حي النزهة، شارع فلسطين',
                'city': 'جدة',
                'area_sqm': Decimal('140.00'),
                'bedrooms': 2,
                'bathrooms': 2,
                'description': 'شقة حديثة ومجهزة بالكامل، قريبة من الكورنيش',
                'purchase_price': Decimal('350000.00'),
                'rental_price_monthly': Decimal('3000.00'),
                'type_index': 0,  # شقة
                'owner_index': 2,
                'is_active': True
            },
            {
                'title': 'مستودع كبير - المنطقة الصناعية',
                'code': 'DMM-WRH-006',
                'address': 'الدمام، المنطقة الصناعية الثانية',
                'city': 'الدمام',
                'area_sqm': Decimal('500.00'),
                'bedrooms': 0,
                'bathrooms': 1,
                'description': 'مستودع واسع مع رافعة شوكية، مناسب للتخزين',
                'purchase_price': Decimal('180000.00'),
                'rental_price_monthly': Decimal('4000.00'),
                'type_index': 4,  # مستودع
                'owner_index': 2,
                'is_active': True
            },
            {
                'title': 'أرض استثمارية - طريق الملك فهد',
                'code': 'RYD-LND-007',
                'address': 'الرياض، طريق الملك فهد، بجوار مركز غرناطة',
                'city': 'الرياض',
                'area_sqm': Decimal('1000.00'),
                'bedrooms': 0,
                'bathrooms': 0,
                'description': 'أرض تجارية في موقع استراتيجي',
                'purchase_price': Decimal('2000000.00'),
                'type_index': 5,  # أرض
                'owner_index': 3,
                'is_active': True
            },
            {
                'title': 'شقة 4 غرف - حي الربوة',
                'code': 'JED-APT-008',
                'address': 'جدة، حي الربوة، شارع الأمير سلطان',
                'city': 'جدة',
                'area_sqm': Decimal('200.00'),
                'bedrooms': 4,
                'bathrooms': 3,
                'description': 'شقة واسعة مع صالة كبيرة ومطبخ مجهز',
                'purchase_price': Decimal('500000.00'),
                'rental_price_monthly': Decimal('4500.00'),
                'type_index': 0,
                'owner_index': 3,
                'is_active': True
            },
            {
                'title': 'فيلا صغيرة - حي الشفا',
                'code': 'TAF-VIL-009',
                'address': 'الطائف، حي الشفا، طريق الهدا',
                'city': 'الطائف',
                'area_sqm': Decimal('250.00'),
                'bedrooms': 3,
                'bathrooms': 2,
                'description': 'فيلا هادئة في منطقة جبلية جميلة',
                'purchase_price': Decimal('600000.00'),
                'rental_price_monthly': Decimal('4000.00'),
                'type_index': 1,
                'owner_index': 4,
                'is_active': True
            },
            {
                'title': 'عمارة سكنية 6 شقق',
                'code': 'MKK-BLD-010',
                'address': 'مكة المكرمة، حي العزيزية، شارع إبراهيم الخليل',
                'city': 'مكة',
                'area_sqm': Decimal('800.00'),
                'bedrooms': 12,
                'bathrooms': 12,
                'description': 'عمارة سكنية 3 طوابق، كل طابق شقتين',
                'purchase_price': Decimal('1500000.00'),
                'rental_price_monthly': Decimal('12000.00'),
                'type_index': 6,  # عمارة
                'owner_index': 4,
                'is_active': True
            },
            {
                'title': 'شقة استديو - حي السلامة',
                'code': 'JED-STD-011',
                'address': 'جدة، حي السلامة، شارع حراء',
                'city': 'جدة',
                'area_sqm': Decimal('60.00'),
                'bedrooms': 1,
                'bathrooms': 1,
                'description': 'استديو مناسب للعزاب، مفروش بالكامل',
                'purchase_price': Decimal('120000.00'),
                'rental_price_monthly': Decimal('1500.00'),
                'type_index': 0,
                'owner_index': 1,
                'is_active': True
            },
            {
                'title': 'مكتب صغير - مركز الأعمال',
                'code': 'RYD-OFF-012',
                'address': 'الرياض، مركز الأعمال، طريق الملك عبدالله',
                'city': 'الرياض',
                'area_sqm': Decimal('50.00'),
                'bedrooms': 0,
                'bathrooms': 1,
                'description': 'مكتب صغير مناسب للشركات الناشئة',
                'purchase_price': Decimal('80000.00'),
                'rental_price_monthly': Decimal('2000.00'),
                'type_index': 2,
                'owner_index': 2,
                'is_active': True
            }
        ]
        
        properties = []
        for data in properties_data:
            prop_data = data.copy()
            type_index = prop_data.pop('type_index')
            owner_index = prop_data.pop('owner_index')
            
            prop, created = Property.objects.get_or_create(
                code=prop_data['code'],
                defaults={
                    **prop_data,
                    'property_type': property_types[type_index],
                    'owner': owners[owner_index]
                }
            )
            properties.append(prop)
            if created:
                self.stdout.write(f'  ✓ Created property: {prop.title}')
        
        return properties

    def create_maintenance_categories(self):
        """Create maintenance categories"""
        self.stdout.write('Creating maintenance categories...')
        
        categories_data = [
            {'name': 'سباكة', 'description': 'أعمال السباكة والصرف الصحي'},
            {'name': 'كهرباء', 'description': 'الأعطال والصيانة الكهربائية'},
            {'name': 'تكييف', 'description': 'صيانة المكيفات والتبريد'},
            {'name': 'نجارة', 'description': 'أعمال النجارة والأبواب'},
            {'name': 'دهان', 'description': 'أعمال الدهانات والديكور'},
            {'name': 'نظافة', 'description': 'التنظيف العام والصيانة'},
            {'name': 'حدادة', 'description': 'أعمال الحديد والأبواب الحديدية'},
            {'name': 'عامة', 'description': 'صيانة عامة متنوعة'},
        ]
        
        categories = []
        for data in categories_data:
            cat, created = MaintenanceCategory.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            categories.append(cat)
            if created:
                self.stdout.write(f'  ✓ Created category: {cat.name}')
        
        return categories

    def create_contracts(self, properties, clients):
        """Create sample contracts"""
        self.stdout.write('Creating contracts...')
        
        today = timezone.now().date()
        
        contracts_data = [
            {
                'property_index': 0,
                'client_index': 0,
                'start_date': today - timedelta(days=180),
                'end_date': today + timedelta(days=185),
                'rent_amount': Decimal('3500.00'),
                'security_deposit': Decimal('3500.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'residential_rent',
                'status': 'active',
                'notes': 'عقد إيجار سكني قياسي'
            },
            {
                'property_index': 2,
                'client_index': 2,
                'start_date': today - timedelta(days=90),
                'end_date': today + timedelta(days=275),
                'rent_amount': Decimal('5000.00'),
                'security_deposit': Decimal('10000.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'commercial_rent',
                'status': 'active',
                'notes': 'عقد إيجار تجاري - مكتب'
            },
            {
                'property_index': 3,
                'client_index': 4,
                'start_date': today - timedelta(days=60),
                'end_date': today + timedelta(days=305),
                'rent_amount': Decimal('8000.00'),
                'security_deposit': Decimal('16000.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'commercial_rent',
                'status': 'active',
                'notes': 'عقد محل تجاري في موقع ممتاز'
            },
            {
                'property_index': 4,
                'client_index': 1,
                'start_date': today - timedelta(days=200),
                'end_date': today + timedelta(days=165),
                'rent_amount': Decimal('3000.00'),
                'security_deposit': Decimal('3000.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'residential_rent',
                'status': 'active',
                'notes': 'مستأجرة ممتازة، دفع منتظم'
            },
            {
                'property_index': 8,
                'client_index': 5,
                'start_date': today - timedelta(days=400),
                'end_date': today - timedelta(days=35),
                'rent_amount': Decimal('4000.00'),
                'security_deposit': Decimal('4000.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'residential_rent',
                'status': 'expired',
                'notes': 'عقد منتهي، في انتظار التجديد'
            },
            {
                'property_index': 10,
                'client_index': 3,
                'start_date': today - timedelta(days=30),
                'end_date': today + timedelta(days=335),
                'rent_amount': Decimal('1500.00'),
                'security_deposit': Decimal('1500.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'residential_rent',
                'status': 'active',
                'notes': 'استديو مفروش، عقد جديد'
            },
            {
                'property_index': 11,
                'client_index': 6,
                'start_date': today + timedelta(days=15),
                'end_date': today + timedelta(days=380),
                'rent_amount': Decimal('2000.00'),
                'security_deposit': Decimal('2000.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'commercial_rent',
                'status': 'draft',
                'notes': 'عقد قيد التحضير'
            },
            {
                'property_index': 7,
                'client_index': 7,
                'start_date': today - timedelta(days=150),
                'end_date': today + timedelta(days=215),
                'rent_amount': Decimal('4500.00'),
                'security_deposit': Decimal('9000.00'),
                'payment_frequency': 'monthly',
                'contract_type': 'residential_rent',
                'status': 'active',
                'notes': 'عائلة كبيرة، 4 غرف'
            }
        ]
        
        contracts = []
        for data in contracts_data:
            contract_data = data.copy()
            property_index = contract_data.pop('property_index')
            client_index = contract_data.pop('client_index')
            
            # Generate unique contract number
            contract_number = f"CNT-{timezone.now().year}-{len(contracts)+1:04d}"
            
            contract, created = Contract.objects.get_or_create(
                contract_number=contract_number,
                defaults={
                    **contract_data,
                    'property': properties[property_index],
                    'client': clients[client_index]
                }
            )
            contracts.append(contract)
            if created:
                self.stdout.write(f'  ✓ Created contract: {contract.contract_number} - {contract.property.title}')
        
        return contracts

    def create_maintenance_requests(self, properties, categories):
        """Create sample maintenance requests"""
        self.stdout.write('Creating maintenance requests...')
        
        today = timezone.now().date()
        
        maintenance_data = [
            {
                'property_index': 0,
                'category_index': 0,  # سباكة
                'title': 'تسريب مياه في الحمام الرئيسي',
                'description': 'يوجد تسريب مياه من خلاط المغسلة، يحتاج لإصلاح عاجل',
                'priority': 'high',
                'status': 'pending',
                'request_date': today - timedelta(days=2),
                'estimated_cost': Decimal('500.00')
            },
            {
                'property_index': 2,
                'category_index': 1,  # كهرباء
                'title': 'عطل في الإنارة الخارجية',
                'description': 'الإنارة الخارجية للمكتب لا تعمل، تحتاج لفحص',
                'priority': 'medium',
                'status': 'in_progress',
                'request_date': today - timedelta(days=5),
                'estimated_cost': Decimal('800.00')
            },
            {
                'property_index': 4,
                'category_index': 2,  # تكييف
                'title': 'المكيف المركزي لا يبرد',
                'description': 'المكيف المركزي يعمل لكن لا يبرد بشكل كافٍ',
                'priority': 'urgent',
                'status': 'in_progress',
                'request_date': today - timedelta(days=1),
                'estimated_cost': Decimal('1200.00')
            },
            {
                'property_index': 3,
                'category_index': 4,  # دهان
                'title': 'تجديد دهان الواجهة',
                'description': 'الواجهة الأمامية تحتاج لإعادة دهان',
                'priority': 'low',
                'status': 'pending',
                'request_date': today - timedelta(days=10),
                'estimated_cost': Decimal('3000.00')
            },
            {
                'property_index': 1,
                'category_index': 3,  # نجارة
                'title': 'إصلاح باب غرفة النوم',
                'description': 'باب غرفة النوم الرئيسية لا يغلق بشكل صحيح',
                'priority': 'medium',
                'status': 'completed',
                'request_date': today - timedelta(days=20),
                'estimated_cost': Decimal('600.00')
            },
            {
                'property_index': 8,
                'category_index': 5,  # نظافة
                'title': 'تنظيف عميق بعد انتهاء العقد',
                'description': 'تنظيف شامل للفيلا قبل استقبال المستأجر الجديد',
                'priority': 'high',
                'status': 'completed',
                'request_date': today - timedelta(days=40),
                'estimated_cost': Decimal('800.00')
            },
            {
                'property_index': 7,
                'category_index': 0,  # سباكة
                'title': 'فحص دوري للسباكة',
                'description': 'فحص دوري شامل لجميع مواسير المياه والصرف',
                'priority': 'low',
                'status': 'pending',
                'request_date': today - timedelta(days=3),
                'estimated_cost': Decimal('400.00')
            },
            {
                'property_index': 5,
                'category_index': 7,  # عامة
                'title': 'صيانة بوابة المستودع',
                'description': 'البوابة الأوتوماتيكية للمستودع تحتاج لصيانة',
                'priority': 'high',
                'status': 'in_progress',
                'request_date': today - timedelta(days=7),
                'estimated_cost': Decimal('1500.00')
            },
            {
                'property_index': 10,
                'category_index': 2,  # تكييف
                'title': 'تنظيف فلاتر المكيف',
                'description': 'تنظيف فلاتر مكيف الاستديو',
                'priority': 'low',
                'status': 'completed',
                'request_date': today - timedelta(days=15),
                'estimated_cost': Decimal('200.00')
            },
            {
                'property_index': 11,
                'category_index': 1,  # كهرباء
                'title': 'إضافة نقاط كهرباء جديدة',
                'description': 'إضافة مخارج كهربائية إضافية في المكتب',
                'priority': 'medium',
                'status': 'pending',
                'request_date': today - timedelta(days=4),
                'estimated_cost': Decimal('700.00')
            },
            {
                'property_index': 0,
                'category_index': 6,  # حدادة
                'title': 'إصلاح نافذة غرفة المعيشة',
                'description': 'نافذة غرفة المعيشة لا تفتح بسهولة',
                'priority': 'medium',
                'status': 'cancelled',
                'request_date': today - timedelta(days=30),
                'estimated_cost': Decimal('350.00')
            },
            {
                'property_index': 9,
                'category_index': 7,  # عامة
                'title': 'صيانة شاملة للعمارة',
                'description': 'صيانة دورية شاملة لجميع شقق العمارة',
                'priority': 'medium',
                'status': 'in_progress',
                'request_date': today - timedelta(days=12),
                'estimated_cost': Decimal('5000.00')
            }
        ]
        
        requests = []
        for idx, data in enumerate(maintenance_data, 1):
            req_data = data.copy()
            property_index = req_data.pop('property_index')
            category_index = req_data.pop('category_index')
            
            # Generate unique request number
            request_number = f"MNT-{timezone.now().year}-{idx:04d}"
            
            request, created = MaintenanceRequest.objects.get_or_create(
                request_number=request_number,
                defaults={
                    **req_data,
                    'property': properties[property_index],
                    'category': categories[category_index]
                }
            )
            requests.append(request)
            if created:
                self.stdout.write(f'  ✓ Created maintenance: {request.title}')
        
        return requests
