"""
Management command to clear all data from the database
Usage: python manage.py clear_all_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.properties.models import (
    Property, PropertyType, PropertyImage, PropertyDocument,
    PropertyValuation, PropertyExpense, PropertyRevenue
)
from apps.owners.models import Owner
from apps.clients.models import Client
from apps.contracts.models import Contract, ContractPayment, ContractRenewal
from apps.maintenance.models import (
    MaintenanceRequest, MaintenanceCategory, MaintenanceAttachment,
    MaintenanceSchedule
)
from apps.financial.models import (
    Account, FinancialPeriod, JournalEntry, JournalEntryLine,
    Invoice, InvoiceItem, Payment, Budget
)


class Command(BaseCommand):
    help = 'Clear all data from the database (except superuser)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            confirm = input('This will delete ALL data (except superuser). Are you sure? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        self.stdout.write(self.style.WARNING('Starting data cleanup...'))

        # Financial Module
        self.stdout.write('Clearing Financial data...')
        Budget.objects.all().delete()
        Payment.objects.all().delete()
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        JournalEntryLine.objects.all().delete()
        JournalEntry.objects.all().delete()
        FinancialPeriod.objects.all().delete()
        Account.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Financial data cleared'))

        # Maintenance Module
        self.stdout.write('Clearing Maintenance data...')
        MaintenanceSchedule.objects.all().delete()
        MaintenanceAttachment.objects.all().delete()
        MaintenanceRequest.objects.all().delete()
        MaintenanceCategory.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Maintenance data cleared'))

        # Contracts Module
        self.stdout.write('Clearing Contracts data...')
        ContractRenewal.objects.all().delete()
        ContractPayment.objects.all().delete()
        Contract.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Contracts data cleared'))

        # Properties Module
        self.stdout.write('Clearing Properties data...')
        PropertyRevenue.objects.all().delete()
        PropertyExpense.objects.all().delete()
        PropertyValuation.objects.all().delete()
        PropertyDocument.objects.all().delete()
        PropertyImage.objects.all().delete()
        Property.objects.all().delete()
        PropertyType.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Properties data cleared'))

        # Clients and Owners
        self.stdout.write('Clearing Clients and Owners...')
        Client.objects.all().delete()
        Owner.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Clients and Owners cleared'))

        # Users (except superuser)
        self.stdout.write('Clearing regular users...')
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('✓ Regular users cleared'))

        self.stdout.write(self.style.SUCCESS('\n✅ All data cleared successfully!'))
        self.stdout.write(self.style.SUCCESS('Superuser account preserved.'))
