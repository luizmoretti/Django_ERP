from django.apps import AppConfig


class OutflowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory.outflows'

    def ready(self):
        import apps.inventory.outflows.signals