from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_authenticated:
            user_id = str(self.scope["user"].id)
            async_to_sync(self.channel_layer.group_add)(
                f"user_{user_id}",
                self.channel_name
            )
            self.accept()

    def notification_message(self, event):
        self.send_json(event)