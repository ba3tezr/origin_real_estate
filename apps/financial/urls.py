"""
URL patterns for Financial app
"""
from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    # Dashboard
    path('', views.financial_dashboard, name='dashboard'),
    
    # Chart of Accounts
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/create/', views.account_create, name='account_create'),
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'),
    
    # Journal Entries
    path('journal-entries/', views.journal_entry_list, name='journal_entry_list'),
    path('journal-entries/create/', views.journal_entry_create, name='journal_entry_create'),
    path('journal-entries/<int:pk>/', views.journal_entry_detail, name='journal_entry_detail'),
    path('journal-entries/<int:pk>/post/', views.journal_entry_post, name='journal_entry_post'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    
    # Payments (Receipts/Payment Vouchers)
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/print/', views.payment_print, name='payment_print'),
    
    # Reports
    path('reports/trial-balance/', views.report_trial_balance, name='report_trial_balance'),
    path('reports/profit-loss/', views.report_profit_loss, name='report_profit_loss'),
    path('reports/balance-sheet/', views.report_balance_sheet, name='report_balance_sheet'),
]
