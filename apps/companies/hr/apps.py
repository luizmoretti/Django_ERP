from django.apps import AppConfig


class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.companies.hr'

    def ready(self):
        """Import signals when app is ready."""
        import apps.companies.hr.signals  # noqa
