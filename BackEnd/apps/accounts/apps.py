from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration for the accounts app.
    
    This configuration class handles the app's setup and signal connections.
    It ensures that all custom signals are properly registered when the app
    is ready, including:
    - Employee creation signal
    - Permission group assignment
    - IP tracking signals
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    
    def ready(self):
        """
        Import and connect signal handlers when the app is ready.
        
        This method is called by Django when the app is loading. It imports
        our custom signals module to ensure all signal handlers are properly
        registered, including:
        - User post-save signals for employee creation
        - Group assignment signals
        - Login signals for IP tracking
        """
        import apps.accounts.signals  # noqa
