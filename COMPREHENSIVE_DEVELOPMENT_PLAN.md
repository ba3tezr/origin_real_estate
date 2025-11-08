# 📋 خطة التطوير الشاملة - Origin App Real Estate
## نظام متكامل للمقاولات والتطوير العقاري

---

## 📚 جدول المحتويات

1. [فهم شامل للنظام الحالي](#section-1)
2. [تحليل الفجوات (Gap Analysis)](#section-2)
3. [خطة تطوير Properties للبيع](#section-3)
4. [نظام المقاولات والتطوير العقاري](#section-4)
5. [النماذج الجديدة المطلوبة](#section-5)
6. [الجدول الزمني للتنفيذ](#section-6)
7. [ERD للنظام المحدث](#section-7)
8. [المتطلبات التقنية](#section-8)
9. [خطة الاختبار](#section-9)
10. [التكامل مع النظام الحالي](#section-10)

---

<a name="section-1"></a>
## 1️⃣ فهم شامل للنظام الحالي

### 🏗️ البنية الحالية

#### النماذج الموجودة (Current Models):

```
📦 PROPERTIES MODULE
├── Property (العقارات)
│   ├── Basic Info: title, code, type, owner
│   ├── Location: address, city, GPS
│   ├── Details: area, bedrooms, bathrooms, floors
│   ├── Pricing: purchase_price, market_value, rental_price_monthly
│   ├── Features: elevator, garden, pool, security, furnished
│   ├── Status: available, rented, maintenance, sold ⚠️
│   └── Relations: owner, property_type
├── PropertyType (أنواع العقارات)
├── PropertyDocument (المستندات)
├── PropertyImage (الصور)
├── PropertyValuation (التقييمات)
├── PropertyAmenity (المرافق)
├── PropertyInspection (الفحوصات)
├── PropertyExpense (المصروفات)
└── PropertyRevenue (الإيرادات)

📦 CONTRACTS MODULE (عقود الإيجار فقط ⚠️)
├── Contract (العقود)
│   ├── Type: residential, commercial, industrial
│   ├── Parties: property, client (tenant)
│   ├── Dates: start_date, end_date, signed_date
│   ├── Financial: rent_amount, security_deposit
│   ├── Payment: frequency, payment_day
│   └── Status: draft, active, expired, terminated, renewed
├── ContractPayment (مدفوعات الإيجار)
└── ContractRenewal (تجديد العقود)

📦 CLIENTS MODULE (المستأجرين فقط ⚠️)
└── Client (العملاء/المستأجرين)
    ├── Personal: name, phone, email, national_id
    ├── Address: address, city, country
    ├── Employment: employer, occupation, monthly_income
    ├── Emergency: contact_name, contact_phone
    └── Status: is_active, credit_score

📦 OWNERS MODULE
└── Owner (الملاك)
    ├── Personal: name, phone, email, national_id
    ├── Address: address, city, country
    └── Tax: tax_id

📦 MAINTENANCE MODULE
├── MaintenanceRequest (طلبات الصيانة)
├── MaintenanceCategory (تصنيفات الصيانة)
├── MaintenanceAttachment (مرفقات)
└── MaintenanceSchedule (جدول الصيانة الوقائية)

📦 FINANCIAL MODULE
├── Account (شجرة الحسابات)
├── Invoice (الفواتير)
├── Payment (المدفوعات)
├── JournalEntry (القيود اليومية)
└── JournalEntryLine (تفاصيل القيود)

📦 CORE MODULE
├── User & UserProfile
├── Role & Permission
├── AuditLog
├── SystemSetting
└── Notification
```

### ✅ نقاط القوة في النظام الحالي:

1. **Property Model قوي ومرن:**
   - يحتوي على حقل `status='sold'` (جاهز للتوسع)
   - يحتوي على `purchase_price` و `market_value`
   - نظام شامل للمستندات والصور
   - تتبع المصروفات والإيرادات

2. **Financial Module متقدم:**
   - شجرة حسابات كاملة (Chart of Accounts)
   - نظام قيود محاسبية مزدوجة
   - فواتير ومدفوعات

3. **بنية معيارية قابلة للتوسع:**
   - تطبيقات Django منفصلة
   - APIs جاهزة
   - نظام صلاحيات قوي

4. **واجهة مستخدم عصرية:**
   - Bootstrap 5
   - HTMX
   - تصميم موحد

---

<a name="section-2"></a>
## 2️⃣ تحليل الفجوات (Gap Analysis)

### ❌ ما ينقص النظام الحالي:

#### أ) بيع العقارات:
```
❌ لا يوجد نموذج SalesContract (عقود البيع)
❌ لا يوجد نموذج Buyer (المشتري)
❌ لا يوجد نظام Payment Plans (خطط الدفع/التقسيط)
❌ لا يوجد Sales Process Workflow (مسار عملية البيع)
❌ لا يوجد Reservation System (نظام الحجز)
❌ لا يوجد تكامل مع Mortgage/Financing (التمويل العقاري)
```

#### ب) شركات المقاولات والتطوير:
```
❌ لا يوجد Projects Module (مشاريع التطوير)
❌ لا يوجد Units Inventory (مخزون الوحدات)
❌ لا يوجد Construction Schedule (جدول الإنشاءات)
❌ لا يوجد Developers/Contractors Management (إدارة المقاولين)
❌ لا يوجد Construction Milestones (مراحل البناء)
❌ لا يوجد Land Acquisition (شراء الأراضي)
❌ لا يوجد Permits & Approvals (التصاريح والموافقات)
❌ لا يوجد Project Budget & Cost Control (الموازنة ومراقبة التكاليف)
❌ لا يوجد Pre-sales Management (إدارة ما قبل البيع)
❌ لا يوجد Construction Materials Tracking (تتبع مواد البناء)
```

#### ج) التقارير المتقدمة:
```
❌ لا توجد تقارير المبيعات
❌ لا توجد تقارير المشاريع
❌ لا توجد تقارير الربحية لكل مشروع
❌ لا توجد تقارير التدفق النقدي المتوقع
```

---

<a name="section-3"></a>
## 3️⃣ خطة تطوير Properties للبيع

### 🎯 المرحلة الأولى: نظام بيع العقارات

#### أ) النماذج المطلوبة:

#### 1. Buyer Model (المشترين)

```python
class Buyer(models.Model):
    """
    نموذج المشترين - يختلف عن المستأجرين
    """
    # Personal Information
    buyer_type = [
        ('individual', 'Individual'),      # فرد
        ('company', 'Company'),            # شركة
        ('investor', 'Investor'),          # مستثمر
    ]
    buyer_type = models.CharField(max_length=20, choices=buyer_type)
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=17)
    email = models.EmailField()
    national_id = models.CharField(max_length=50, unique=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    # Company Info (إذا كان شركة)
    company_name = models.CharField(max_length=200, blank=True)
    company_registration = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Financial Information
    annual_income = models.DecimalField(max_digits=15, decimal_places=2)
    credit_score = models.IntegerField()
    financing_approved = models.BooleanField(default=False)
    financing_institution = models.CharField(max_length=200, blank=True)
    approved_loan_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Identification Documents
    id_document = models.FileField(upload_to='buyers/documents/')
    income_proof = models.FileField(upload_to='buyers/documents/', blank=True)
    
    # Agent/Representative
    has_agent = models.BooleanField(default=False)
    agent_name = models.CharField(max_length=200, blank=True)
    agent_phone = models.CharField(max_length=17, blank=True)
    agent_license = models.CharField(max_length=100, blank=True)
    
    # Status
    is_qualified = models.BooleanField(default=False)  # مؤهل للشراء
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Buyer'
        verbose_name_plural = 'Buyers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_buyer_type_display()}"
    
    def get_purchasing_power(self):
        """حساب القدرة الشرائية"""
        return self.annual_income * Decimal('3.5') + self.approved_loan_amount
```

#### 2. PropertyReservation Model (حجز العقار)

```python
class PropertyReservation(models.Model):
    """
    حجز العقار قبل إتمام عملية البيع
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),           # قيد الانتظار
        ('approved', 'Approved'),         # موافق عليه
        ('cancelled', 'Cancelled'),       # ملغى
        ('converted', 'Converted to Sale'), # تحول لعقد بيع
    ]
    
    reservation_number = models.CharField(max_length=50, unique=True)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    buyer = models.ForeignKey(Buyer, on_delete=models.PROTECT)
    
    # Dates
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()  # تاريخ انتهاء الحجز
    
    # Financial
    reservation_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_reference = models.CharField(max_length=100)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Notes
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Staff
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Property Reservation'
        verbose_name_plural = 'Property Reservations'
        ordering = ['-reservation_date']
    
    def __str__(self):
        return f"{self.reservation_number} - {self.property.code}"
    
    def is_expired(self):
        """تحقق من انتهاء صلاحية الحجز"""
        from django.utils import timezone
        return timezone.now().date() > self.expiry_date and self.status == 'pending'
    
    def convert_to_sale(self):
        """تحويل الحجز إلى عقد بيع"""
        self.status = 'converted'
        self.save()
```

#### 3. SalesContract Model (عقود البيع)

```python
class SalesContract(models.Model):
    """
    عقود بيع العقارات - منفصل عن عقود الإيجار
    """
    CONTRACT_STATUS = [
        ('draft', 'Draft'),                    # مسودة
        ('under_review', 'Under Review'),      # قيد المراجعة
        ('approved', 'Approved'),              # موافق عليه
        ('signed', 'Signed'),                  # موقع
        ('in_progress', 'In Progress'),        # قيد التنفيذ
        ('completed', 'Completed'),            # مكتمل
        ('cancelled', 'Cancelled'),            # ملغى
    ]
    
    # Basic Information
    contract_number = models.CharField(max_length=50, unique=True)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    buyer = models.ForeignKey(Buyer, on_delete=models.PROTECT)
    seller = models.ForeignKey(Owner, on_delete=models.PROTECT)  # البائع (المالك)
    
    # Price & Payment
    sale_price = models.DecimalField(max_digits=15, decimal_places=2)
    down_payment = models.DecimalField(max_digits=15, decimal_places=2)
    financed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Financing Details
    has_financing = models.BooleanField(default=False)
    financing_institution = models.CharField(max_length=200, blank=True)
    financing_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    financing_years = models.IntegerField(default=0)
    
    # Dates
    contract_date = models.DateField()
    signing_date = models.DateField(null=True, blank=True)
    expected_handover_date = models.DateField()  # تاريخ التسليم المتوقع
    actual_handover_date = models.DateField(null=True, blank=True)
    
    # Payment Plan
    has_installments = models.BooleanField(default=False)
    number_of_installments = models.IntegerField(default=0)
    installment_frequency = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi_annual', 'Semi-Annual'),
            ('annual', 'Annual'),
        ],
        default='monthly'
    )
    
    # Property Condition
    sold_as_is = models.BooleanField(default=False)  # يباع كما هو
    includes_furniture = models.BooleanField(default=False)
    furniture_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Legal & Documents
    title_deed_number = models.CharField(max_length=100, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    notary_name = models.CharField(max_length=200, blank=True)
    lawyer_name = models.CharField(max_length=200, blank=True)
    
    # Terms & Conditions
    terms_and_conditions = models.TextField()
    special_conditions = models.TextField(blank=True)
    warranty_terms = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='draft')
    is_registered = models.BooleanField(default=False)  # مسجل رسمياً
    registration_date = models.DateField(null=True, blank=True)
    
    # Files
    contract_file = models.FileField(upload_to='sales_contracts/', blank=True)
    signed_contract_file = models.FileField(upload_to='sales_contracts/signed/', blank=True)
    
    # Agent Commission
    has_agent = models.BooleanField(default=False)
    agent_name = models.CharField(max_length=200, blank=True)
    agent_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    agent_commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Staff
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_contracts_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_contracts_approved')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Contract'
        verbose_name_plural = 'Sales Contracts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract_number} - {self.property.code}"
    
    def get_total_paid(self):
        """إجمالي المبلغ المدفوع"""
        return self.payments.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def get_remaining_amount(self):
        """المبلغ المتبقي"""
        return self.sale_price - self.get_total_paid()
    
    def get_payment_progress_percentage(self):
        """نسبة إتمام الدفع"""
        if self.sale_price > 0:
            return (self.get_total_paid() / self.sale_price) * 100
        return 0
```

#### 4. SalesPaymentPlan Model (خطة الدفع/التقسيط)

```python
class SalesPaymentPlan(models.Model):
    """
    خطة الدفع بالتقسيط لعقود البيع
    """
    sales_contract = models.ForeignKey(SalesContract, on_delete=models.CASCADE, related_name='payment_plans')
    
    installment_number = models.IntegerField()  # رقم القسط
    due_date = models.DateField()              # تاريخ الاستحقاق
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Late Payment
    is_overdue = models.BooleanField(default=False)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Payment Plan'
        verbose_name_plural = 'Sales Payment Plans'
        ordering = ['due_date', 'installment_number']
        unique_together = ['sales_contract', 'installment_number']
    
    def __str__(self):
        return f"{self.sales_contract.contract_number} - Installment #{self.installment_number}"
    
    def check_overdue(self):
        """تحقق من تأخر الدفع"""
        from django.utils import timezone
        if not self.is_paid and timezone.now().date() > self.due_date:
            self.is_overdue = True
            self.save()
```

#### 5. SalesPayment Model (مدفوعات البيع)

```python
class SalesPayment(models.Model):
    """
    مدفوعات عقود البيع
    """
    PAYMENT_TYPES = [
        ('down_payment', 'Down Payment'),          # دفعة مقدمة
        ('installment', 'Installment'),           # قسط
        ('final_payment', 'Final Payment'),       # دفعة نهائية
        ('late_fee', 'Late Fee'),                 # غرامة تأخير
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    sales_contract = models.ForeignKey(SalesContract, on_delete=models.PROTECT, related_name='payments')
    payment_plan = models.ForeignKey(SalesPaymentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    
    # Payment Method
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('check', 'Check'),
            ('credit_card', 'Credit Card'),
            ('mortgage', 'Mortgage Payment'),
            ('online', 'Online Payment'),
        ]
    )
    
    # References
    reference_number = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=200, blank=True)
    check_number = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Receipt
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_file = models.FileField(upload_to='sales_payments/receipts/', blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Staff
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Payment'
        verbose_name_plural = 'Sales Payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"
```

#### 6. تحديث Property Model

```python
# إضافة الحقول التالية إلى Property Model الحالي:

class Property(models.Model):
    # ... الحقول الموجودة ...
    
    # Sales-specific fields
    is_for_sale = models.BooleanField('For Sale', default=False)
    is_for_rent = models.BooleanField('For Rent', default=True)
    
    sale_price = models.DecimalField(
        'Sale Price',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Marketing
    marketing_status = models.CharField(
        max_length=20,
        choices=[
            ('not_listed', 'Not Listed'),
            ('coming_soon', 'Coming Soon'),
            ('active', 'Active'),
            ('under_contract', 'Under Contract'),
            ('sold', 'Sold'),
            ('off_market', 'Off Market'),
        ],
        default='not_listed'
    )
    
    listed_date = models.DateField(null=True, blank=True)
    sold_date = models.DateField(null=True, blank=True)
    
    # Agent Information
    listing_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listed_properties'
    )
    
    # Virtual Tour & Marketing
    virtual_tour_url = models.URLField(blank=True)
    video_tour_url = models.URLField(blank=True)
    property_brochure = models.FileField(upload_to='properties/brochures/', blank=True)
    
    # ... باقي الحقول الموجودة ...
```

---

#### ب) مسار العمل (Sales Workflow):

```
1. Property Listing (إدراج العقار)
   ├── تحديد السعر
   ├── التصوير والتسويق
   ├── إنشاء البروشور
   └── نشر في الموقع/التطبيق

2. Lead Management (إدارة العملاء المحتملين)
   ├── استقبال الاستفسارات
   ├── جدولة المعاينات
   ├── متابعة العملاء
   └── تقييم القدرة الشرائية

3. Reservation (الحجز)
   ├── دفع مبلغ الحجز
   ├── تحديد مدة الحجز
   ├── إيقاف تسويق العقار
   └── إصدار إيصال الحجز

4. Due Diligence (العناية الواجبة)
   ├── فحص المستندات
   ├── التقييم العقاري
   ├── الفحص الهندسي
   └── موافقة التمويل (إن وجد)

5. Contract Preparation (إعداد العقد)
   ├── صياغة العقد
   ├── مراجعة قانونية
   ├── تحديد خطة الدفع
   └── شروط خاصة

6. Contract Signing (توقيع العقد)
   ├── توقيع الأطراف
   ├── توثيق العقد
   ├── دفع الدفعة المقدمة
   └── تسجيل العقد

7. Payment Processing (معالجة المدفوعات)
   ├── متابعة الأقساط
   ├── إصدار الإيصالات
   ├── تتبع المتأخرات
   └── غرامات التأخير

8. Property Handover (تسليم العقار)
   ├── التفتيش النهائي
   ├── تسليم المفاتيح
   ├── نقل الملكية
   └── إغلاق الملف

9. Post-Sale (ما بعد البيع)
   ├── خدمة ما بعد البيع
   ├── ضمانات
   ├── صيانة (فترة الضمان)
   └── رضا العملاء
```

---

#### ج) الواجهات المطلوبة:

```
📱 Sales Management Dashboard
├── Sales Pipeline (مسار المبيعات)
├── Properties for Sale (العقارات المعروضة)
├── Reservations (الحجوزات)
├── Active Sales Contracts (عقود البيع النشطة)
├── Payment Collections (التحصيلات)
└── Sales Performance (أداء المبيعات)

📋 Buyers Management
├── Buyers List (قائمة المشترين)
├── Buyer Profile (ملف المشتري)
├── Credit Assessment (تقييم الائتمان)
├── Purchase History (سجل المشتريات)
└── Communication Log (سجل التواصل)

🏠 Property Sales Listing
├── Properties for Sale (العقارات للبيع)
├── Property Details & Gallery (التفاصيل والمعرض)
├── Price History (تاريخ السعر)
├── Viewing Requests (طلبات المعاينة)
└── Marketing Materials (المواد التسويقية)

📄 Sales Contracts
├── Contracts List (قائمة العقود)
├── Contract Details (تفاصيل العقد)
├── Payment Schedule (جدول الدفعات)
├── Contract Documents (مستندات العقد)
└── Contract History (سجل العقد)

💰 Sales Payments
├── Payments Calendar (تقويم الدفعات)
├── Due Installments (الأقساط المستحقة)
├── Payment Collection (تحصيل الدفعات)
├── Overdue Tracking (متابعة المتأخرات)
└── Payment Reports (تقارير الدفعات)

📊 Sales Reports
├── Sales Summary (ملخص المبيعات)
├── Revenue Analysis (تحليل الإيرادات)
├── Properties Sold (العقارات المباعة)
├── Payment Collections (التحصيلات)
├── Commission Reports (تقارير العمولات)
└── Sales Forecast (التوقعات)
```

---

<a name="section-4"></a>
## 4️⃣ نظام المقاولات والتطوير العقاري

### 🏗️ المرحلة الثانية: Construction & Development

#### أ) النماذج المطلوبة:

#### 1. DevelopmentProject Model (مشاريع التطوير)

```python
class DevelopmentProject(models.Model):
    """
    مشاريع التطوير العقاري
    """
    PROJECT_TYPES = [
        ('residential', 'Residential Complex'),      # مجمع سكني
        ('commercial', 'Commercial Building'),       # مبنى تجاري
        ('mixed_use', 'Mixed Use'),                 # استخدام مختلط
        ('villa_compound', 'Villa Compound'),       # مجمع فلل
        ('tower', 'Tower'),                         # برج
        ('mall', 'Shopping Mall'),                  # مول تجاري
        ('industrial', 'Industrial'),               # صناعي
    ]
    
    PROJECT_STATUS = [
        ('planning', 'Planning'),                   # التخطيط
        ('design', 'Design'),                       # التصميم
        ('approval', 'Seeking Approval'),           # طلب الموافقات
        ('pre_construction', 'Pre-Construction'),   # ما قبل البناء
        ('under_construction', 'Under Construction'),# تحت الإنشاء
        ('finishing', 'Finishing'),                 # التشطيبات
        ('completed', 'Completed'),                 # مكتمل
        ('delivered', 'Delivered'),                 # مُسلّم
        ('on_hold', 'On Hold'),                     # متوقف
        ('cancelled', 'Cancelled'),                 # ملغى
    ]
    
    # Basic Information
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=200)
    project_name_ar = models.CharField(max_length=200, blank=True)
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPES)
    
    # Location
    land_area_sqm = models.DecimalField(max_digits=12, decimal_places=2)
    total_built_area_sqm = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Project Details
    number_of_floors = models.IntegerField()
    number_of_units = models.IntegerField()
    number_of_buildings = models.IntegerField(default=1)
    
    # Timeline
    planning_start_date = models.DateField()
    construction_start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    project_duration_months = models.IntegerField()  # المدة المتوقعة
    
    # Financial
    total_budget = models.DecimalField(max_digits=18, decimal_places=2)
    land_cost = models.DecimalField(max_digits=18, decimal_places=2)
    construction_cost = models.DecimalField(max_digits=18, decimal_places=2)
    infrastructure_cost = models.DecimalField(max_digits=18, decimal_places=2)
    marketing_budget = models.DecimalField(max_digits=15, decimal_places=2)
    contingency_budget = models.DecimalField(max_digits=15, decimal_places=2)  # احتياطي
    
    expected_total_revenue = models.DecimalField(max_digits=18, decimal_places=2)
    expected_profit_margin = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Actual Costs
    actual_spent = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Developer Information
    developer = models.ForeignKey(Owner, on_delete=models.PROTECT, related_name='developed_projects')
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    
    # Status
    status = models.CharField(max_length=30, choices=PROJECT_STATUS, default='planning')
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Permits & Approvals
    has_land_permit = models.BooleanField(default=False)
    has_building_permit = models.BooleanField(default=False)
    has_environmental_approval = models.BooleanField(default=False)
    has_civil_defense_approval = models.BooleanField(default=False)
    
    # Marketing
    is_marketed = models.BooleanField(default=False)
    marketing_start_date = models.DateField(null=True, blank=True)
    pre_sale_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Description
    description = models.TextField()
    description_ar = models.TextField(blank=True)
    features = models.TextField(blank=True)
    amenities = models.TextField(blank=True)
    
    # Media
    master_plan_image = models.ImageField(upload_to='projects/master_plans/', blank=True)
    logo = models.ImageField(upload_to='projects/logos/', blank=True)
    brochure = models.FileField(upload_to='projects/brochures/', blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Development Project'
        verbose_name_plural = 'Development Projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
    
    def get_roi(self):
        """Return on Investment"""
        if self.total_budget > 0:
            profit = self.expected_total_revenue - self.total_budget
            return (profit / self.total_budget) * 100
        return 0
    
    def get_actual_profit(self):
        """الربح الفعلي حتى الآن"""
        total_sales = self.units.filter(
            status='sold'
        ).aggregate(total=models.Sum('sale_price'))['total'] or 0
        return Decimal(total_sales) - self.actual_spent
```

#### 2. ProjectUnit Model (وحدات المشروع)

```python
class ProjectUnit(models.Model):
    """
    الوحدات ضمن مشروع التطوير
    """
    UNIT_TYPES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('townhouse', 'Townhouse'),
        ('duplex', 'Duplex'),
        ('penthouse', 'Penthouse'),
        ('shop', 'Shop'),
        ('office', 'Office'),
        ('warehouse', 'Warehouse'),
        ('showroom', 'Showroom'),
    ]
    
    UNIT_STATUS = [
        ('planned', 'Planned'),                 # مخطط
        ('under_construction', 'Under Construction'), # تحت الإنشاء
        ('completed', 'Completed'),             # مكتمل
        ('available', 'Available'),             # متاح
        ('reserved', 'Reserved'),               # محجوز
        ('sold', 'Sold'),                       # مباع
        ('delivered', 'Delivered'),             # مُسلّم
    ]
    
    FINISHING_TYPES = [
        ('shell', 'Shell & Core'),              # هيكل فقط
        ('semi_finished', 'Semi-Finished'),     # نصف تشطيب
        ('fully_finished', 'Fully Finished'),   # كامل التشطيب
        ('luxury', 'Luxury Finishing'),         # تشطيب فاخر
    ]
    
    # Identification
    project = models.ForeignKey(DevelopmentProject, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=50)
    unit_code = models.CharField(max_length=50, unique=True)  # كود فريد
    
    # Unit Details
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    building_number = models.CharField(max_length=20, blank=True)
    floor_number = models.IntegerField()
    
    # Specifications
    area_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    living_rooms = models.IntegerField(default=0)
    has_balcony = models.BooleanField(default=False)
    balcony_area = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    has_garden = models.BooleanField(default=False)
    garden_area = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    parking_spaces = models.IntegerField(default=0)
    storage_room = models.BooleanField(default=False)
    
    # Finishing
    finishing_type = models.CharField(max_length=20, choices=FINISHING_TYPES)
    
    # Orientation
    facing_direction = models.CharField(
        max_length=20,
        choices=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
            ('north_east', 'North East'),
            ('north_west', 'North West'),
            ('south_east', 'South East'),
            ('south_west', 'South West'),
        ],
        blank=True
    )
    
    # Pricing
    base_price = models.DecimalField(max_digits=15, decimal_places=2)
    current_price = models.DecimalField(max_digits=15, decimal_places=2)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Discounts
    has_discount = models.BooleanField(default=False)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=30, choices=UNIT_STATUS, default='planned')
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Construction Dates
    construction_start_date = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Sales Information
    is_for_sale = models.BooleanField(default=True)
    listed_date = models.DateField(null=True, blank=True)
    reserved_date = models.DateField(null=True, blank=True)
    sold_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    
    # Buyer Information (إذا تم البيع)
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    sales_contract = models.OneToOneField(SalesContract, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Property Link (بعد التسليم يتحول لـ Property)
    property = models.OneToOneField(Property, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Features
    features_list = models.JSONField(default=list, blank=True)  # قائمة المميزات
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project Unit'
        verbose_name_plural = 'Project Units'
        ordering = ['project', 'building_number', 'floor_number', 'unit_number']
        unique_together = ['project', 'unit_number']
    
    def __str__(self):
        return f"{self.project.project_code} - Unit {self.unit_number}"
    
    def calculate_final_price(self):
        """حساب السعر النهائي بعد الخصم"""
        if self.has_discount:
            self.final_price = self.current_price - self.discount_amount
        else:
            self.final_price = self.current_price
        self.save()
```

#### 3. Contractor Model (المقاولين)

```python
class Contractor(models.Model):
    """
    المقاولين والمقاولات
    """
    CONTRACTOR_TYPES = [
        ('general', 'General Contractor'),        # مقاول عام
        ('electrical', 'Electrical'),             # كهرباء
        ('plumbing', 'Plumbing'),                # سباكة
        ('hvac', 'HVAC'),                        # تكييف وتهوية
        ('finishing', 'Finishing'),              # تشطيبات
        ('landscaping', 'Landscaping'),          # تنسيق حدائق
        ('concrete', 'Concrete'),                # خرسانة
        ('steel', 'Steel Work'),                 # حديد
        ('carpentry', 'Carpentry'),              # نجارة
        ('painting', 'Painting'),                # دهان
        ('tiles', 'Tiles & Flooring'),           # بلاط وأرضيات
        ('other', 'Other'),
    ]
    
    # Company Information
    company_name = models.CharField(max_length=200)
    company_name_ar = models.CharField(max_length=200, blank=True)
    contractor_type = models.CharField(max_length=30, choices=CONTRACTOR_TYPES)
    license_number = models.CharField(max_length=100, unique=True)
    tax_id = models.CharField(max_length=50)
    
    # Contact Information
    contact_person = models.CharField(max_length=200)
    phone = models.CharField(max_length=17)
    mobile = models.CharField(max_length=17, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    # Bank Information
    bank_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    iban = models.CharField(max_length=50, blank=True)
    
    # Rating & Performance
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # من 5
    completed_projects = models.IntegerField(default=0)
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Insurance & Certificates
    has_insurance = models.BooleanField(default=False)
    insurance_expiry_date = models.DateField(null=True, blank=True)
    certifications = models.TextField(blank=True)
    
    # Documents
    license_document = models.FileField(upload_to='contractors/licenses/', blank=True)
    insurance_document = models.FileField(upload_to='contractors/insurance/', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contractor'
        verbose_name_plural = 'Contractors'
        ordering = ['company_name']
    
    def __str__(self):
        return f"{self.company_name} - {self.get_contractor_type_display()}"
```

#### 4. ProjectContract Model (عقود المقاولات)

```python
class ProjectContract(models.Model):
    """
    عقود المقاولات للمشاريع
    """
    CONTRACT_TYPES = [
        ('lump_sum', 'Lump Sum'),                # مبلغ مقطوع
        ('unit_price', 'Unit Price'),            # سعر الوحدة
        ('cost_plus', 'Cost Plus'),              # التكلفة زائد
        ('design_build', 'Design-Build'),        # تصميم وتنفيذ
    ]
    
    CONTRACT_STATUS = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('signed', 'Signed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]
    
    # Basic Information
    contract_number = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(DevelopmentProject, on_delete=models.PROTECT, related_name='contracts')
    contractor = models.ForeignKey(Contractor, on_delete=models.PROTECT, related_name='contracts')
    
    # Contract Details
    contract_type = models.CharField(max_length=30, choices=CONTRACT_TYPES)
    scope_of_work = models.TextField()
    
    # Financial
    contract_value = models.DecimalField(max_digits=18, decimal_places=2)
    advance_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    advance_payment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    retention_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    retention_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Timeline
    start_date = models.DateField()
    expected_completion_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    contract_duration_days = models.IntegerField()
    
    # Penalties & Bonuses
    has_penalties = models.BooleanField(default=True)
    daily_penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_penalties = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    has_bonuses = models.BooleanField(default=False)
    early_completion_bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Performance
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Insurance & Guarantees
    has_performance_bond = models.BooleanField(default=False)
    performance_bond_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    warranty_period_months = models.IntegerField(default=12)
    
    # Status
    status = models.CharField(max_length=30, choices=CONTRACT_STATUS, default='draft')
    
    # Documents
    contract_file = models.FileField(upload_to='project_contracts/', blank=True)
    signed_contract_file = models.FileField(upload_to='project_contracts/signed/', blank=True)
    
    # Terms
    payment_terms = models.TextField()
    special_conditions = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project Contract'
        verbose_name_plural = 'Project Contracts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract_number} - {self.contractor.company_name}"
    
    def get_remaining_amount(self):
        """المبلغ المتبقي"""
        return self.contract_value - self.total_paid - self.retention_amount
```

#### 5. ConstructionMilestone Model (مراحل الإنشاء)

```python
class ConstructionMilestone(models.Model):
    """
    مراحل الإنشاء والإنجاز
    """
    MILESTONE_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
        ('on_hold', 'On Hold'),
    ]
    
    project = models.ForeignKey(DevelopmentProject, on_delete=models.CASCADE, related_name='milestones')
    project_contract = models.ForeignKey(ProjectContract, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Milestone Details
    milestone_name = models.CharField(max_length=200)
    milestone_order = models.IntegerField()  # الترتيب
    description = models.TextField()
    
    # Timeline
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Progress
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # وزن المرحلة من المشروع
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Financial
    milestone_value = models.DecimalField(max_digits=15, decimal_places=2)
    payment_due_on_completion = models.DecimalField(max_digits=15, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    
    # Quality Control
    requires_inspection = models.BooleanField(default=True)
    is_inspected = models.BooleanField(default=False)
    inspection_date = models.DateField(null=True, blank=True)
    inspection_passed = models.BooleanField(default=False)
    inspector_name = models.CharField(max_length=200, blank=True)
    inspection_notes = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=MILESTONE_STATUS, default='pending')
    
    # Dependencies
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='prerequisite_for')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Construction Milestone'
        verbose_name_plural = 'Construction Milestones'
        ordering = ['project', 'milestone_order']
    
    def __str__(self):
        return f"{self.project.project_code} - {self.milestone_name}"
    
    def is_delayed(self):
        """تحقق من التأخير"""
        from django.utils import timezone
        if self.status not in ['completed'] and timezone.now().date() > self.planned_end_date:
            return True
        return False
```

#### 6. ConstructionMaterial Model (مواد البناء)

```python
class ConstructionMaterial(models.Model):
    """
    مواد البناء والتتبع
    """
    MATERIAL_CATEGORIES = [
        ('cement', 'Cement'),
        ('steel', 'Steel & Rebar'),
        ('blocks', 'Blocks & Bricks'),
        ('sand', 'Sand & Aggregates'),
        ('plumbing', 'Plumbing Materials'),
        ('electrical', 'Electrical Materials'),
        ('finishing', 'Finishing Materials'),
        ('paint', 'Paint'),
        ('tiles', 'Tiles & Flooring'),
        ('doors', 'Doors & Windows'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(DevelopmentProject, on_delete=models.CASCADE, related_name='materials')
    
    # Material Details
    material_name = models.CharField(max_length=200)
    material_category = models.CharField(max_length=30, choices=MATERIAL_CATEGORIES)
    specification = models.TextField()
    unit_of_measurement = models.CharField(max_length=50)  # ton, m3, m2, piece, etc.
    
    # Supplier
    supplier_name = models.CharField(max_length=200)
    supplier_phone = models.CharField(max_length=17, blank=True)
    
    # Quantity & Cost
    required_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Delivery
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Status
    is_delivered = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    # Quality
    quality_certificate = models.FileField(upload_to='materials/certificates/', blank=True)
    test_report = models.FileField(upload_to='materials/reports/', blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Construction Material'
        verbose_name_plural = 'Construction Materials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.material_name} - {self.project.project_code}"
```

#### 7. LandAcquisition Model (شراء الأراضي)

```python
class LandAcquisition(models.Model):
    """
    سجل شراء الأراضي للمشاريع
    """
    LAND_STATUS = [
        ('prospecting', 'Prospecting'),          # بحث
        ('under_negotiation', 'Negotiation'),    # تفاوض
        ('due_diligence', 'Due Diligence'),      # العناية الواجبة
        ('contract_signed', 'Contract Signed'),   # عقد موقع
        ('payment_pending', 'Payment Pending'),   # بانتظار الدفع
        ('completed', 'Completed'),               # مكتمل
        ('cancelled', 'Cancelled'),               # ملغى
    ]
    
    # Land Information
    land_code = models.CharField(max_length=50, unique=True)
    land_title_deed = models.CharField(max_length=100)
    land_area_sqm = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Seller Information
    seller_name = models.CharField(max_length=200)
    seller_id = models.CharField(max_length=50)
    seller_phone = models.CharField(max_length=17)
    
    # Financial
    asking_price = models.DecimalField(max_digits=18, decimal_places=2)
    negotiated_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(max_digits=18, decimal_places=2)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    down_payment = models.DecimalField(max_digits=15, decimal_places=2)
    total_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Dates
    identification_date = models.DateField()
    offer_date = models.DateField(null=True, blank=True)
    contract_date = models.DateField(null=True, blank=True)
    transfer_date = models.DateField(null=True, blank=True)
    
    # Legal
    land_use_type = models.CharField(max_length=100)  # residential, commercial, etc.
    zoning_classification = models.CharField(max_length=100)
    building_regulations = models.TextField()
    has_legal_issues = models.BooleanField(default=False)
    legal_notes = models.TextField(blank=True)
    
    # Due Diligence
    survey_report = models.FileField(upload_to='land/surveys/', blank=True)
    soil_test_report = models.FileField(upload_to='land/soil_tests/', blank=True)
    title_search_report = models.FileField(upload_to='land/title_searches/', blank=True)
    
    # Project Link
    development_project = models.OneToOneField(
        DevelopmentProject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='land'
    )
    
    # Status
    status = models.CharField(max_length=30, choices=LAND_STATUS)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Land Acquisition'
        verbose_name_plural = 'Land Acquisitions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.land_code} - {self.city}"
```

#### 8. ProjectPermit Model (التصاريح والموافقات)

```python
class ProjectPermit(models.Model):
    """
    التصاريح والموافقات المطلوبة للمشاريع
    """
    PERMIT_TYPES = [
        ('land_use', 'Land Use Permit'),
        ('building', 'Building Permit'),
        ('demolition', 'Demolition Permit'),
        ('environmental', 'Environmental Approval'),
        ('civil_defense', 'Civil Defense Approval'),
        ('municipality', 'Municipality Approval'),
        ('utility', 'Utility Connection'),
        ('occupancy', 'Occupancy Certificate'),
        ('other', 'Other'),
    ]
    
    PERMIT_STATUS = [
        ('pending', 'Pending Application'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('renewed', 'Renewed'),
    ]
    
    project = models.ForeignKey(DevelopmentProject, on_delete=models.CASCADE, related_name='permits')
    
    # Permit Details
    permit_type = models.CharField(max_length=30, choices=PERMIT_TYPES)
    permit_number = models.CharField(max_length=100, blank=True)
    issuing_authority = models.CharField(max_length=200)
    
    # Dates
    application_date = models.DateField()
    approval_date = models.DateField(null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Financial
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    permit_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=PERMIT_STATUS, default='pending')
    
    # Documents
    application_document = models.FileField(upload_to='permits/applications/', blank=True)
    permit_document = models.FileField(upload_to='permits/documents/', blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project Permit'
        verbose_name_plural = 'Project Permits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.project_code} - {self.get_permit_type_display()}"
    
    def is_expired(self):
        """تحقق من انتهاء الصلاحية"""
        if self.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiry_date
        return False
```

---

<a name="section-5"></a>
## 5️⃣ النماذج الإضافية المساعدة

### أ) نماذج إدارة العملاء المحتملين (Leads):

```python
class PropertyLead(models.Model):
    """
    العملاء المحتملين المهتمين بالعقارات
    """
    LEAD_SOURCE = [
        ('website', 'Website'),
        ('phone', 'Phone Call'),
        ('email', 'Email'),
        ('walk_in', 'Walk-in'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('advertising', 'Advertising'),
        ('other', 'Other'),
    ]
    
    LEAD_STATUS = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('viewing_scheduled', 'Viewing Scheduled'),
        ('negotiating', 'Negotiating'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]
    
    INTEREST_TYPE = [
        ('buy', 'Interested to Buy'),
        ('rent', 'Interested to Rent'),
        ('invest', 'Investment'),
    ]
    
    # Lead Information
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=17)
    email = models.EmailField(blank=True)
    
    # Interest
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPE)
    interested_property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    interested_project = models.ForeignKey(DevelopmentProject, on_delete=models.SET_NULL, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Preferences
    preferred_location = models.CharField(max_length=200, blank=True)
    preferred_property_type = models.CharField(max_length=100, blank=True)
    number_of_bedrooms = models.IntegerField(null=True, blank=True)
    
    # Lead Management
    lead_source = models.CharField(max_length=30, choices=LEAD_SOURCE)
    status = models.CharField(max_length=30, choices=LEAD_STATUS, default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Follow-up
    last_contact_date = models.DateField(null=True, blank=True)
    next_follow_up_date = models.DateField(null=True, blank=True)
    
    # Conversion
    converted_to_buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    converted_to_client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    conversion_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    lost_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Property Lead'
        verbose_name_plural = 'Property Leads'
        ordering = ['-created_at']
```

### ب) نماذج جدولة المعاينات:

```python
class PropertyViewing(models.Model):
    """
    جدولة معاينات العقارات
    """
    VIEWING_STATUS = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='viewings')
    lead = models.ForeignKey(PropertyLead, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Viewer Information
    viewer_name = models.CharField(max_length=200)
    viewer_phone = models.CharField(max_length=17)
    viewer_email = models.EmailField(blank=True)
    
    # Viewing Details
    viewing_date = models.DateField()
    viewing_time = models.TimeField()
    duration_minutes = models.IntegerField(default=30)
    
    # Agent
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=VIEWING_STATUS, default='scheduled')
    
    # Feedback
    viewer_feedback = models.TextField(blank=True)
    agent_notes = models.TextField(blank=True)
    interest_level = models.IntegerField(null=True, blank=True)  # 1-5
    
    # Notes
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Property Viewing'
        verbose_name_plural = 'Property Viewings'
        ordering = ['-viewing_date', '-viewing_time']
```

---

<a name="section-6"></a>
## 6️⃣ الجدول الزمني للتنفيذ

### 📅 خطة التنفيذ على 6 مراحل:

#### **المرحلة 1: Property Sales Module (4-6 أسابيع)**

**الأسبوع 1-2: النماذج الأساسية**
```
✅ إنشاء Buyer Model
✅ إنشاء PropertyReservation Model
✅ إنشاء SalesContract Model
✅ إنشاء SalesPaymentPlan Model
✅ إنشاء SalesPayment Model
✅ تحديث Property Model (إضافة حقول البيع)
✅ Migrations وأنشاء قاعدة البيانات
```

**الأسبوع 3-4: الواجهات والـ Views**
```
✅ Sales Dashboard
✅ Buyers Management (List, Create, Edit, Delete)
✅ Property Sales Listing
✅ Reservation System
✅ Sales Contracts Management
✅ Payment Plans Interface
✅ Payment Collection Interface
```

**الأسبوع 5-6: التكامل والاختبار**
```
✅ تكامل مع Financial Module
✅ APIs للبيع
✅ التقارير الأساسية
✅ الإشعارات
✅ الاختبار الشامل
✅ إصلاح الأخطاء
```

---

#### **المرحلة 2: Development Projects Module (6-8 أسابيع)**

**الأسبوع 1-2: مشاريع التطوير**
```
✅ إنشاء DevelopmentProject Model
✅ إنشاء ProjectUnit Model
✅ إنشاء LandAcquisition Model
✅ Migrations
✅ Dashboard للمشاريع
✅ إنشاء/تعديل المشاريع
✅ إدارة الوحدات
```

**الأسبوع 3-4: المقاولات**
```
✅ إنشاء Contractor Model
✅ إنشاء ProjectContract Model
✅ إدارة المقاولين
✅ إدارة عقود المقاولات
✅ متابعة الدفعات للمقاولين
```

**الأسبوع 5-6: مراحل الإنشاء**
```
✅ إنشاء ConstructionMilestone Model
✅ إنشاء ConstructionMaterial Model
✅ إنشاء ProjectPermit Model
✅ جدول زمني للمشروع (Gantt Chart)
✅ متابعة التقدم
✅ إدارة المواد
✅ التصاريح والموافقات
```

**الأسبوع 7-8: التكامل والاختبار**
```
✅ تكامل مع Sales Module
✅ تكامل مع Financial Module
✅ APIs للمشاريع
✅ تقارير المشاريع
✅ الاختبار الشامل
```

---

#### **المرحلة 3: Leads & Marketing Module (3-4 أسابيع)**

**الأسبوع 1-2:**
```
✅ إنشاء PropertyLead Model
✅ إنشاء PropertyViewing Model
✅ Lead Management Interface
✅ Viewing Scheduler
✅ Lead Tracking Dashboard
```

**الأسبوع 3-4:**
```
✅ Email Marketing Integration
✅ WhatsApp Integration
✅ SMS Notifications
✅ Lead Scoring System
✅ Conversion Tracking
```

---

#### **المرحلة 4: Advanced Financial Integration (4-5 أسابيع)**

**الأسبوع 1-2:**
```
✅ تكامل Sales مع Chart of Accounts
✅ قيود محاسبية تلقائية للمبيعات
✅ تتبع الإيرادات المستقبلية
✅ تقارير التدفق النقدي
```

**الأسبوع 3-4:**
```
✅ Project Budget Management
✅ Cost Control System
✅ Construction Cost Tracking
✅ Profitability Analysis per Project
```

**الأسبوع 5:**
```
✅ Financial Dashboards
✅ ROI Calculations
✅ Cash Flow Forecasting
✅ Investment Analysis
```

---

#### **المرحلة 5: Reporting & Analytics (3-4 أسابيع)**

```
✅ Sales Reports
   ├── Sales Summary
   ├── Properties Sold
   ├── Revenue by Project
   ├── Sales Pipeline
   └── Agent Performance

✅ Project Reports
   ├── Project Progress
   ├── Budget vs Actual
   ├── Timeline Analysis
   ├── Contractor Performance
   └── Material Tracking

✅ Financial Reports
   ├── Profit & Loss by Project
   ├── Cash Flow
   ├── Budget Reports
   ├── Revenue Recognition
   └── Cost Analysis

✅ Executive Dashboard
   ├── KPIs Overview
   ├── Sales Performance
   ├── Project Status
   ├── Financial Health
   └── Alerts & Notifications
```

---

#### **المرحلة 6: Mobile App & Advanced Features (6-8 أسابيع)**

```
✅ Mobile App Development
   ├── Buyer App
   ├── Agent App
   ├── Project Manager App
   └── Owner Portal

✅ Advanced Features
   ├── Virtual Tours Integration
   ├── 3D Visualization
   ├── Document Management System
   ├── Mortgage Calculator
   └── Property Comparison

✅ Integration
   ├── Payment Gateway
   ├── Bank Integration
   ├── Government Systems
   └── Third-party Services
```

---

### 📊 إجمالي الوقت المتوقع:

```
المرحلة 1: Property Sales         = 6 أسابيع
المرحلة 2: Development Projects   = 8 أسابيع
المرحلة 3: Leads & Marketing     = 4 أسابيع
المرحلة 4: Financial Integration = 5 أسابيع
المرحلة 5: Reporting             = 4 أسابيع
المرحلة 6: Mobile & Advanced     = 8 أسابيع
─────────────────────────────────────────────
الإجمالي                          = 35 أسبوع (~8-9 أشهر)
```

---

<a name="section-7"></a>
## 7️⃣ ERD للنظام المحدث

```
┌─────────────────────────────────────────────────────────────────┐
│                     CORE SYSTEM (موجود)                         │
├─────────────────────────────────────────────────────────────────┤
│ User, UserProfile, Role, Permission, AuditLog, Notification     │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                              │
┌───────▼──────────┐                         ┌────────▼─────────┐
│  PROPERTY SYSTEM │                         │  FINANCIAL SYSTEM│
│   (محدّث)        │                         │    (موجود)      │
├──────────────────┤                         ├──────────────────┤
│ Property         │◄────────────────────────┤ Account          │
│ PropertyType     │                         │ Invoice          │
│ PropertyDocument │                         │ Payment          │
│ PropertyImage    │                         │ JournalEntry     │
│ PropertyValuation│                         └──────────────────┘
└──────┬───────────┘
       │
       │ ┌────────────────────────────────────────────────┐
       │ │            SALES SYSTEM (جديد)                 │
       │ ├────────────────────────────────────────────────┤
       ├─┤ Buyer                                          │
       │ │ PropertyReservation                            │
       │ │ SalesContract ────► SalesPaymentPlan          │
       │ │       └────────────► SalesPayment             │
       │ │ PropertyLead                                   │
       │ │ PropertyViewing                                │
       │ └────────────────────────────────────────────────┘
       │
       │ ┌────────────────────────────────────────────────┐
       │ │     DEVELOPMENT PROJECTS SYSTEM (جديد)         │
       │ ├────────────────────────────────────────────────┤
       └─┤ DevelopmentProject                             │
         │   ├─► ProjectUnit ────► Buyer/SalesContract   │
         │   ├─► ConstructionMilestone                    │
         │   ├─► ConstructionMaterial                     │
         │   ├─► ProjectPermit                            │
         │   └─► LandAcquisition                          │
         │                                                 │
         │ Contractor ───► ProjectContract                │
         └────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              EXISTING MODULES (موجودة)                          │
├─────────────────────────────────────────────────────────────────┤
│ Owner, Client, Contract (Rental), Maintenance                   │
└─────────────────────────────────────────────────────────────────┘
```

---

<a name="section-8"></a>
## 8️⃣ المتطلبات التقنية

### أ) التقنيات والمكتبات:

```python
# requirements.txt الإضافية

# للمشاريع والجداول الزمنية
django-gantt==1.5.0
python-dateutil==2.8.2

# للتقارير المتقدمة
reportlab==4.0.5
openpyxl==3.1.2
pandas==2.1.1

# للرسوم البيانية
plotly==5.17.0
django-chartjs==2.3.0

# للـ Notifications
django-notifications-hq==1.8.3
celery==5.3.4
redis==5.0.0

# للـ WhatsApp Integration
twilio==8.9.1

# للـ Email Marketing
sendgrid==6.10.0

# للـ Document Management
django-storages==1.14
boto3==1.28.57  # للـ AWS S3

# للـ PDF Generation
weasyprint==60.0

# للـ Data Export
django-import-export==3.3.1

# للـ API Documentation
drf-yasg==1.21.7

# للـ Background Tasks
django-celery-beat==2.5.0

# للـ Caching
django-redis==5.4.0
```

### ب) قاعدة البيانات:

```python
# للإنتاج - PostgreSQL موصى به
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'origin_app_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### ج) المساحة التخزينية المتوقعة:

```
Database:
├── Development: ~500 MB - 1 GB
├── Production (1 year): ~5-10 GB
└── Production (5 years): ~25-50 GB

Media Files:
├── Property Images: ~10-20 GB/year
├── Documents: ~5-10 GB/year
├── Project Plans: ~5-10 GB/year
└── Reports: ~2-5 GB/year
```

---

<a name="section-9"></a>
## 9️⃣ خطة الاختبار

### أ) اختبارات الوحدة (Unit Tests):

```python
# tests/test_sales.py
def test_buyer_creation()
def test_property_reservation()
def test_sales_contract_creation()
def test_payment_plan_generation()
def test_installment_calculation()

# tests/test_projects.py
def test_project_creation()
def test_unit_creation()
def test_contractor_assignment()
def test_milestone_tracking()
def test_material_tracking()
```

### ب) اختبارات التكامل (Integration Tests):

```python
def test_reservation_to_contract_flow()
def test_payment_to_financial_integration()
def test_project_unit_to_property_conversion()
def test_contractor_payment_flow()
def test_milestone_completion_notification()
```

### ج) اختبارات الأداء (Performance Tests):

```python
def test_large_project_loading()
def test_bulk_unit_creation()
def test_report_generation_speed()
def test_concurrent_user_access()
```

---

<a name="section-10"></a>
## 🔟 التكامل مع النظام الحالي

### أ) نقاط التكامل الرئيسية:

#### 1. Property Model:
```python
# قبل:
Property → Owner
         → PropertyType
         → Contracts (Rental only)

# بعد:
Property → Owner
         → PropertyType
         → Contracts (Rental)
         → SalesContract (New)
         → PropertyReservation (New)
         → PropertyLead (New)
         → ProjectUnit (Link - New)
```

#### 2. Financial Module:
```python
# تكامل المبيعات:
SalesPayment → Create JournalEntry automatically
├── Debit: Bank/Cash Account
└── Credit: Sales Revenue Account

# تكامل المشاريع:
ProjectContract Payment → Create JournalEntry
├── Debit: Construction Cost Account
└── Credit: Bank/Payables Account
```

#### 3. Maintenance Module:
```python
# ربط مع المشاريع:
DevelopmentProject → MaintenanceRequest (warranty period)
ProjectUnit → MaintenanceRequest (defects)
```

---

## 📋 الخلاصة والتوصيات

### ✅ النقاط الرئيسية:

1. **النظام الحالي قوي وجاهز للتوسع**
   - البنية المعيارية ممتازة
   - Financial Module متقدم
   - الواجهات موحدة

2. **المرحلة الأولى (Sales) أولوية قصوى**
   - 6 أسابيع للتنفيذ
   - تأثير كبير على العمل
   - سهلة التكامل

3. **المرحلة الثانية (Projects) الأكثر تعقيداً**
   - 8 أسابيع للتنفيذ
   - تتطلب تخطيط دقيق
   - تحول النظام لمنصة متكاملة

4. **التوثيق والتدريب مهم جداً**
   - دليل المستخدم
   - فيديوهات تدريبية
   - دعم فني

### 🎯 التوصيات:

1. **البدء بالمرحلة الأولى فوراً**
2. **تعيين فريق متخصص**
3. **اختبارات مستمرة**
4. **تدريب المستخدمين**
5. **جمع Feedback باستمرار**

---

## 📞 الدعم والمتابعة

هذه الوثيقة حية ويجب تحديثها بانتظام مع تقدم التطوير.

**آخر تحديث:** 2025-11-08
**الإصدار:** 1.0
**الحالة:** جاهز للتنفيذ

---

**🚀 جاهزون للبدء في بناء أقوى نظام إدارة عقارات ومقاولات في المنطقة!**
