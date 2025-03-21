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
from apps.notifications.routing import websocket_urlpatterns as notification_websocket_urlpatterns
from apps.delivery.routing import websocket_urlpatterns as delivery_websocket_urlpatterns
from core.unified_middleware import UnifiedAuthMiddlewareStack

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Combinar rotas WebSocket de diferentes aplicações
websocket_urlpatterns = notification_websocket_urlpatterns + delivery_websocket_urlpatterns

# For development, we'll skip the AllowedHostsOriginValidator
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": UnifiedAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})


#For production use the AllowedHostsOriginValidator
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator(
#         UnifiedAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
#     ),
# })
