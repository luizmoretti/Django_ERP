from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.companies.customers'
    
    def ready(self):
        import apps.companies.customers.signals  # noqa
