from django.apps import AppConfig

class PurchaseOrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory.purchase_order'

    def ready(self):
        import apps.inventory.purchase_order.signals
        from .notifications import handlers