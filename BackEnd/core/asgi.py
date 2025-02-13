"""
ASGI config for core project.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from apps.notifications.routing import websocket_urlpatterns
from apps.notifications.middleware import TokenAuthMiddlewareStack

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# For development, we'll skip the AllowedHostsOriginValidator
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddlewareStack(
        URLRouter([
            *websocket_urlpatterns,
        ])
    ),
})
