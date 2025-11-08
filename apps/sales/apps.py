from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sales'
    verbose_name = 'Property Sales'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.sales.signals
