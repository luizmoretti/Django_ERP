from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync, sync_to_async
from .models import Delivery
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class DeliveryConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time delivery tracking.
    
    Handles:
    - Real-time location updates
    - Status changes notifications
    - User authentication and permission checks
    - Group subscription management
    """
    
    async def connect(self):
        """
        Handles WebSocket connection initialization.
        
        - Extracts delivery ID from URL route
        - Verifies user permissions to access delivery data
        - Adds user to the delivery's channel group if authorized
        """
        self.delivery_id = self.scope['url_route']['kwargs']['delivery_id']
        self.delivery_group_name = f'delivery_{self.delivery_id}'

        # Verify user permissions before connecting
        user = self.scope['user']
        can_access = await self.can_access_delivery(user, self.delivery_id)
        
        if not can_access:
            logger.warning(f"[DELIVERY CONSUMER] - Access denied for user {user.username} to delivery {self.delivery_id}")
            await self.close()
            return
        
        # Add to delivery group
        await self.channel_layer.group_add(
            self.delivery_group_name,
            self.channel_name
        )
        
        logger.info(f"[DELIVERY CONSUMER] - WebSocket connected for delivery {self.delivery_id}")
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        
        - Removes user from the delivery's channel group
        - Logs the disconnection event
        """
        # Leave delivery group
        await self.channel_layer.group_discard(
            self.delivery_group_name,
            self.channel_name
        )
        logger.info(f"[DELIVERY CONSUMER] - WebSocket disconnected for delivery {self.delivery_id}")
    
    async def receive(self, text_data):
        """
        Processes incoming WebSocket messages.
        
        Currently handles:
        - Client connection notifications
        - Ping messages (responding with pong)
        
        Args:
            text_data: JSON string containing the message data
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'client_connected':
                # Handle client connection notification
                logger.info(f"[DELIVERY CONSUMER] - Client {data.get('client_id')} connected to delivery {self.delivery_id}")
                
            elif message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        
        except Exception as e:
            logger.error(f"[DELIVERY CONSUMER] - Error processing message: {str(e)}")
    
    # Message handler methods
    
    async def location_update(self, event):
        """
        Handles location update events from the channel layer.
        
        Forwards the location update to connected WebSocket clients.
        
        Args:
            event: Dictionary containing location data
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'delivery_id': event['delivery_id'],
            'status': event['status'],
            'estimated_arrival': event['estimated_arrival']
        }))
    
    async def status_update(self, event):
        """
        Handles status update events from the channel layer.
        
        Forwards the status update to connected WebSocket clients.
        
        Args:
            event: Dictionary containing status data
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status'],
            'delivery_id': event['delivery_id'],
            'timestamp': event['timestamp']
        }))
    
    @sync_to_async
    def can_access_delivery(self, user, delivery_id):
        """
        Checks if a user has permission to access delivery data via WebSocket.
        
        Permissions are based on user role:
        - Driver assigned to this delivery
        - Customer associated with this delivery
        - Manager at the company handling the delivery
        
        Args:
            user: User attempting to access the WebSocket
            delivery_id: ID of the delivery being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        if not user.is_authenticated:
            return False
            
        try:
            # Try to get delivery object
            delivery = Delivery.objects.get(id=delivery_id)
            
            # Check if user is delivery driver
            if hasattr(user, 'employeer') and user.user_type == 'Driver' and delivery.driver_id == user.employeer.id:
                return True
                
            # Check if user is the customer
            if hasattr(user, 'customer') and delivery.customer_id == user.customer.id:
                return True
                
            # Check if user is manager at the company
            if user.user_type == 'Manager' and hasattr(user, 'employeer'):
                if user.employeer.companie == delivery.companie:
                    return True
            
            return False
            
        except Delivery.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"[DELIVERY CONSUMER] - Error checking permissions: {str(e)}")
            return False
        
        