from django.apps import AppConfig


class CustomMiddlewaresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_settings.custom_middlewares'
    
    def ready(self):
        from .middleware import JSONResponse404Middleware, AnonymousUserMiddleware
