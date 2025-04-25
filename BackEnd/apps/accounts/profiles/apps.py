from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts.profiles'
    verbose_name = 'User Profiles'

    
    def ready(self):
        # Import signals when the application is ready
        import apps.accounts.profiles.signals