from django.apps import AppConfig


class TransferConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory.transfer'

    def ready(self):
        import apps.inventory.transfer.signals