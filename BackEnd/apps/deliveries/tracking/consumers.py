import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.gis.geos import Point
import logging

logger = logging.getLogger(__name__)

class DeliveryTrackingConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for delivery tracking.
    Allows clients to receive real-time updates about delivery locations.
    """
    
    async def connect(self):
        """
        Called when the WebSocket is established.
        Extracts the delivery ID from the URL and adds the client to the tracking group.
        """
        self.delivery_id = self.scope['url_route']['kwargs']['delivery_id']
        self.tracking_group_name = f'delivery_tracking_{self.delivery_id}'
        
        # Log connection attempt with user information
        user = self.scope.get('user')
        if user and user.is_authenticated:
            logger.info(f"[TRACKING - CONSUMER] WebSocket connection attempt for delivery {self.delivery_id} by user {user.email}")
        else:
            logger.info(f"[TRACKING - CONSUMER] WebSocket connection attempt for delivery {self.delivery_id} by anonymous user")
        
        # Check if the delivery exists and if the user has permission to access it
        delivery_exists = await self.delivery_exists_and_authorized()
        
        if not delivery_exists:
            # Reject the connection if the delivery doesn't exist or the user doesn't have permission
            logger.warning(f"[TRACKING - CONSUMER] Connection rejected: Delivery {self.delivery_id} does not exist or user has no permission")
            await self.close(code=4003)
            return
        
        # Add to tracking group
        await self.channel_layer.group_add(
            self.tracking_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        logger.info(f"[TRACKING - CONSUMER] WebSocket connection accepted for delivery {self.delivery_id}")
        
        # Send the most recent location immediately after connection
        latest_location = await self.get_latest_location()
        if latest_location:
            await self.send_json(latest_location)
            logger.debug(f"[TRACKING - CONSUMER] Sent initial location for delivery {self.delivery_id}")
        else:
            logger.debug(f"[TRACKING - CONSUMER] No location data available for delivery {self.delivery_id}")
    
    async def disconnect(self, close_code):
        """
        Called when the WebSocket is closed.
        Removes the client from the tracking group.
        """
        # Remove from group when disconnecting
        await self.channel_layer.group_discard(
            self.tracking_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """
        Called when we receive a JSON message from the WebSocket.
        Processes location and status updates.
        """
        try:
            # Check message type
            message_type = content.get('type')
            
            if message_type == 'location_update':
                # Process location update
                await self.handle_location_update(content)
            elif message_type == 'status_update':
                # Process status update
                await self.handle_status_update(content)
            else:
                logger.warning(f"[TRACKING - CONSUMER] Unknown message type: {message_type}")
        except Exception as e:
            logger.error(f"[TRACKING - CONSUMER] Error processing WebSocket message: {str(e)}")
            # Send error message to client
            await self.send_json({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            })
    
    async def location_update(self, event):
        """
        Called when a message is sent to the group.
        Sends the location update to the WebSocket.
        """
        # Send to WebSocket
        await self.send_json(event)
    
    async def status_update(self, event):
        """
        Called when a status update is sent to the group.
        Sends the status update to the WebSocket.
        """
        # Send to WebSocket
        await self.send_json(event)
    
    async def handle_location_update(self, content):
        """
        Handles location update by saving to database and sending to group.
        """
        try:
            # First, save to database (sync operation)
            location_update = await self._save_location_update(content)
            
            # Then, send to group (async operation)
            latitude = content.get('latitude')
            longitude = content.get('longitude')
            accuracy = content.get('accuracy')
            speed = content.get('speed')
            heading = content.get('heading')
            
            await self.channel_layer.group_send(
                self.tracking_group_name,
                {
                    'type': 'location_update',
                    'delivery_id': str(self.delivery_id),
                    'latitude': latitude,
                    'longitude': longitude,
                    'accuracy': accuracy,
                    'speed': speed,
                    'heading': heading,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return location_update
        except Exception as e:
            logger.error(f"[TRACKING - CONSUMER] Error handling location update: {str(e)}")
            raise
    
    @database_sync_to_async
    def _save_location_update(self, content):
        """
        Saves a location update to the database.
        This is a synchronous function wrapped with database_sync_to_async.
        """
        try:
            from apps.deliveries.models import Delivery
            from apps.deliveries.tracking.models import DeliveryLocationUpdate
            
            # Extract data from message
            latitude = content.get('latitude')
            longitude = content.get('longitude')
            accuracy = content.get('accuracy')
            speed = content.get('speed')
            heading = content.get('heading')
            
            # Check if required data is present
            if latitude is None or longitude is None:
                raise ValueError("Latitude and longitude are required")
            
            # Create geographic point
            location = Point(float(longitude), float(latitude))
            
            # Get delivery and vehicle
            delivery = Delivery.objects.get(id=self.delivery_id)
            vehicle = delivery.driver
            
            # Save location update
            location_update = DeliveryLocationUpdate.objects.create(
                delivery=delivery,
                vehicle=vehicle,
                location=location,
                accuracy=accuracy,
                speed=speed,
                heading=heading
            )
            
            return location_update
        except Exception as e:
            logger.error(f"[TRACKING - CONSUMER] Error processing location update: {str(e)}")
            raise
    
    async def handle_status_update(self, content):
        """
        Handles status update by saving to database and sending to group.
        """
        try:
            # First, save to database (sync operation)
            status_update = await self._save_status_update(content)
            
            # Then, send to group (async operation)
            status = content.get('status')
            notes = content.get('notes')
            
            await self.channel_layer.group_send(
                self.tracking_group_name,
                {
                    'type': 'status_update',
                    'delivery_id': str(self.delivery_id),
                    'status': status,
                    'notes': notes,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return status_update
        except Exception as e:
            logger.error(f"[TRACKING - CONSUMER] Error handling status update: {str(e)}")
            raise
    
    @database_sync_to_async
    def _save_status_update(self, content):
        """
        Saves a status update to the database.
        This is a synchronous function wrapped with database_sync_to_async.
        """
        try:
            from apps.deliveries.models import Delivery
            from apps.deliveries.tracking.models import DeliveryLocationUpdate, DeliveryStatusUpdate
            
            # Extract data from message
            status = content.get('status')
            notes = content.get('notes')
            
            # Check if required data is present
            if not status:
                raise ValueError("Status is required")
            
            # Get delivery
            delivery = Delivery.objects.get(id=self.delivery_id)
            
            # Get current location, if available
            location_update = DeliveryLocationUpdate.objects.filter(
                delivery=delivery
            ).order_by('-created_at').first()
            
            # Update delivery status
            delivery.status = status
            delivery.save(update_fields=['status', 'updated_at'])
            
            # Save status update
            status_update = DeliveryStatusUpdate.objects.create(
                delivery=delivery,
                status=status,
                location_update=location_update,
                notes=notes
            )
            
            return status_update
        except Exception as e:
            logger.error(f"[TRACKING - CONSUMER] Error processing status update: {str(e)}")
            raise
    
    @database_sync_to_async
    def delivery_exists_and_authorized(self):
        """
        Checks if the delivery exists and if the user has permission to access it.
        """
        try:
            from apps.deliveries.models import Delivery
            
            user = self.scope['user']
            
            # If the user is not authenticated, only check if the delivery exists
            if user.is_anonymous:
                # For public deliveries, just check if it exists
                return Delivery.objects.filter(id=self.delivery_id).exists()
            
            # For authenticated users, check permissions
            employeer = user.employeer
            return Delivery.objects.filter(
                id=self.delivery_id,
                companie=employeer.companie
            ).exists()
        except Exception as e:
            logger.error(f"[TRACKING - CONSUMER] Error checking delivery: {str(e)}")
            return False
    
    @database_sync_to_async
    def get_latest_location(self):
        """
        Gets the most recent location of the delivery.
        """
        try:
            from apps.deliveries.tracking.models import DeliveryLocationUpdate
            
            latest = DeliveryLocationUpdate.objects.filter(
                delivery_id=self.delivery_id
            ).order_by('-created_at').first()
            
            if latest:
                return {
                    'type': 'location_update',
                    'delivery_id': str(self.delivery_id),
                    'latitude': latest.location.y,
                    'longitude': latest.location.x,
                    'accuracy': latest.accuracy,
                    'speed': latest.speed,
                    'heading': latest.heading,
                    'timestamp': latest.created_at.isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"[TRACKING - CONSUMER] Error getting most recent location: {str(e)}")
            return None