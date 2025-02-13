from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory.warehouse'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.inventory.warehouse.signals  # noqa
