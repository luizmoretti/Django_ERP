import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    """
    SEVERITY_CLASSES = {
        'info': 'notification-info',
        'warning': 'notification-warning',
        'critical': 'notification-critical'
    }
    
    async def connect(self):
        """
        Handle WebSocket connection.
        """
        try:
            # Get authorization header
            headers = dict(self.scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode('utf-8')
            
            logger.debug(f"Authorization header: {auth_header}")
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("No Bearer token found in authorization header")
                await self.close(code=4001)
                return

            # Extract token
            token = auth_header.split(' ')[1]
            
            try:
                # Validate token
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Get user from database
                User = get_user_model()
                self.user = await database_sync_to_async(User.objects.get)(id=user_id)
                
                if not self.user.is_authenticated:
                    logger.warning(f"User {user_id} is not authenticated")
                    await self.close(code=4002)
                    return
                
                logger.info(f"User {self.user.email} authenticated successfully")
                
                # Add user to their personal notification group
                self.group_name = f"user_{self.user.id}"
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                
                logger.info(f"Added {self.user.email} to group {self.group_name}")
                await self.accept()
                
            except (InvalidToken, TokenError, InvalidTokenError) as e:
                logger.error(f"Token validation error: {str(e)}")
                await self.close(code=4003)
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                await self.close(code=4004)
                
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        try:
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
                logger.info(f"Removed user from group {self.group_name}")
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")

    async def notification_message(self, event):
        """
        Handle incoming notification messages.
        """
        try:
            notification_type = event.get("data", {}).get("type", "info")
            css_class = self.SEVERITY_CLASSES.get(notification_type, "notification-info")
            
            message_data = {
                "type": "notification",
                "title": event.get("title", ""),
                "message": event["message"],
                "data": event.get("data", {}),
                "css_class": css_class
            }
            
            await self.send(text_data=json.dumps(message_data))
            logger.debug(f"Sent notification to {self.user.email}: {message_data}")
            
        except Exception as e:
            logger.error(f"Message sending error: {str(e)}")
            await self.close(code=4005)