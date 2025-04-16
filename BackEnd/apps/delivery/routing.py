from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    # Pattern: ws://host/ws/delivery/<uuid>/
    re_path(r'ws/delivery/(?P<delivery_id>[0-9a-f-]+)/$', consumer.DeliveryConsumer.as_asgi()),
] 