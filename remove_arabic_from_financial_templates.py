#!/usr/bin/env python3
"""
Remove all Arabic text from financial templates
"""
import re
import os

def remove_arabic_text(text):
    """Remove Arabic text from the given text"""
    
    # Common Arabic phrases to remove or replace
    replacements = {
        # Titles
        r' - شجرة الحسابات': '',
        r' - إنشاء حساب': '',
        r' - إنشاء فاتورة': '',
        r' - إنشاء سند': '',
        r' - القيود اليومية': '',
        r' - إنشاء قيد يومي': '',
        r' - الفواتير': '',
        r' - سندات القبض والصرف': '',
        r' - الميزانية العمومية': '',
        r' - قائمة الدخل': '',
        r' - ميزان المراجعة': '',
        
        # Descriptions
        r'شجرة الحسابات المحاسبية': 'Manage your financial accounts',
        r'إنشاء فاتورة جديدة': 'Create new invoice',
        r'إنشاء سند قبض أو صرف جديد': 'Create new payment or receipt',
        r'إنشاء قيد يومي جديد': 'Create new journal entry',
        r'القيود اليومية - Double Entry Bookkeeping': 'Double Entry Bookkeeping',
        r'إدارة الفواتير': 'Manage invoices',
        r'سندات القبض والصرف': 'Payments and Receipts',
        r'الميزانية العمومية - Statement of Financial Position': 'Statement of Financial Position',
        r'قائمة الدخل - Income Statement': 'Income Statement',
        r'ميزان المراجعة - Balance Verification': 'Balance Verification',
        
        # Account types
        r' \(الأصول\)': '',
        r' \(الخصوم\)': '',
        r' \(حقوق الملكية\)': '',
        r' \(الإيرادات\)': '',
        r' \(المصروفات\)': '',
        r'Asset \(الأصول\)': 'Asset',
        r'Liability \(الخصوم\)': 'Liability',
        r'Equity \(حقوق الملكية\)': 'Equity',
        r'Revenue \(الإيرادات\)': 'Revenue',
        r'Expense \(المصروفات\)': 'Expense',
        
        # Invoice types
        r' \(فاتورة مبيعات\)': '',
        r' \(فاتورة مشتريات\)': '',
        r' \(فاتورة إيجار\)': '',
        r' \(فاتورة خدمات\)': '',
        r' \(مسودة\)': '',
        r' \(صادرة\)': '',
        
        # Payment types and methods
        r' - سند قبض': '',
        r' - سند صرف': '',
        r'Receipt \(سند قبض\)': 'Receipt',
        r'Payment \(سند صرف\)': 'Payment',
        r'Cash \(نقد\)': 'Cash',
        r'Check \(شيك\)': 'Check',
        r'Bank Transfer \(حوالة بنكية\)': 'Bank Transfer',
        r'Credit Card \(بطاقة ائتمان\)': 'Credit Card',
        r'Online Payment \(دفع إلكتروني\)': 'Online Payment',
        
        # Entry types
        r'Manual Entry \(قيد يدوي\)': 'Manual Entry',
        r'Adjustment Entry \(قيد تسوية\)': 'Adjustment Entry',
        r'Opening Entry \(قيد افتتاحي\)': 'Opening Entry',
        r'Closing Entry \(قيد إقفال\)': 'Closing Entry',
        
        # Other terms
        r'Entry Lines \(سطور القيد\)': 'Entry Lines',
        r'RECEIPT VOUCHER \(سند قبض\)': 'RECEIPT VOUCHER',
        r'PAYMENT VOUCHER \(سند صرف\)': 'PAYMENT VOUCHER',
        r'ASSETS \(الأصول\)': 'ASSETS',
        r'LIABILITIES \(الخصوم\)': 'LIABILITIES',
        r'EQUITY \(حقوق الملكية\)': 'EQUITY',
        r'REVENUE \(الإيرادات\)': 'REVENUE',
        r'EXPENSES \(المصروفات\)': 'EXPENSES',
        r'NET INCOME \(صافي الدخل\)': 'NET INCOME',
        
        # Remove Arabic placeholders
        r'e\.g\., النقدية': 'e.g., Cash',
        r'استلمنا من': 'Received From',
        r'دفعنا إلى': 'Paid To',
        
        # Help text
        r'<li><strong>Receipt \(سند قبض\):</strong> Money received from customers/tenants</li>': '<li><strong>Receipt:</strong> Money received from customers/tenants</li>',
        r'<li><strong>Payment \(سند صرف\):</strong> Money paid to vendors/suppliers</li>': '<li><strong>Payment:</strong> Money paid to vendors/suppliers</li>',
        r"label\.textContent = 'Received From \(استلمنا من\)';": "label.textContent = 'Received From';",
        r"label\.textContent = 'Paid To \(دفعنا إلى\)';": "label.textContent = 'Paid To';",
    }
    
    # Apply all replacements
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    
    # Remove any remaining Arabic characters in specific contexts
    text = re.sub(r'\([\u0600-\u06FF\s]+\)', '', text)
    text = re.sub(r' - [\u0600-\u06FF\s]+$', '', text, flags=re.MULTILINE)
    
    return text

def clean_financial_templates():
    """Clean all financial templates"""
    templates_dir = "templates/financial"
    
    if not os.path.exists(templates_dir):
        print(f"Error: {templates_dir} not found!")
        return
    
    files_cleaned = 0
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                # Read file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file has Arabic text
                if re.search(r'[\u0600-\u06FF]', content):
                    # Clean Arabic text
                    cleaned_content = remove_arabic_text(content)
                    
                    # Write back
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    print(f"✓ Cleaned: {filepath}")
                    files_cleaned += 1
    
    print(f"\n✅ Cleaned {files_cleaned} files")

if __name__ == '__main__':
    clean_financial_templates()
