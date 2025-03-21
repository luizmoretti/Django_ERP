from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync

class DeliveryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.delivery_id = self.scope['url_route']['kwargs']['delivery_id']
        self.delivery_group_name = f'delivery_{self.delivery_id}'

        # Verify user permissions before connecting
        user = self.scope['user']
        if not self.can_access_delivery(user, self.delivery_id):
            await self.close()
            return
        
        async_to_sync(self.channel_layer.group_add)(
            self.delivery_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def can_access_delivery(self, user, delivery_id):
        pass
        
        