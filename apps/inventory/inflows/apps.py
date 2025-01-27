from django.apps import AppConfig


class InflowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory.inflows'

    def ready(self):
        import apps.inventory.inflows.signals