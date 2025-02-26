from django.apps import AppConfig


class TrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.deliveries.tracking'
    verbose_name = 'Delivery Tracking'

    def ready(self):
        import apps.deliveries.tracking.signals  # noqa
