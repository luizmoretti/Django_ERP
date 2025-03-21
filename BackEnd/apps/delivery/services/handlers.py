from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from ..models import Delivery, DeliveryCheckpoint
from apps.companies.customers.models import Customer
from apps.companies.employeers.models import Employeer
from apps.vehicle.models import Vehicle
from apps.inventory.load_order.models import LoadOrder
from .validators import DeliveryValidator
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import json

logger = logging.getLogger(__name__)

class DeliveryHandler:
    """Handler for delivery operations that manages business logic and transaction management."""
    
    @staticmethod
    @transaction.atomic
    def create_delivery(data: dict, created_by) -> Delivery:
        """
        Creates a new delivery entity with associated load orders.
        
        Args:
            data: Dictionary containing delivery data including customer, driver, vehicle and load IDs
            created_by: User creating the delivery
            
        Returns:
            Newly created Delivery instance
            
        Raises:
            ValidationError: If data validation fails or any related object doesn't exist
        """
        try:
            # Validate data
            DeliveryValidator.validate_delivery_data(data)
            
            # Get related objects
            customer = Customer.objects.get(id=data['customer'])
            driver = Employeer.objects.get(id=data['driver'])
            vehicle = Vehicle.objects.get(id=data['vehicle'])
            loads = [LoadOrder.objects.get(id=load_id) for load_id in data['load']]
            
            # Set initial status
            status = data.get('status', 'pending')
            
            # Create delivery
            delivery = Delivery(
                customer=customer,
                driver=driver,
                vehicle=vehicle,
                status=status,
                created_by=created_by,
                updated_by=created_by,
                companie=created_by.companie
            )
            
            # Set initial location if provided
            if 'current_location' in data:
                delivery.current_location = data['current_location']
                
            # Set estimated arrival time if provided
            if 'estimated_arrival' in data:
                delivery.estimated_arrival = data['estimated_arrival']
                
            delivery.save()
            
            # Add load orders
            delivery.load.set(loads)
            
            # Create initial checkpoint
            if delivery.current_location:
                DeliveryCheckpoint.objects.create(
                    delivery=delivery,
                    location=delivery.current_location,
                    status=status,
                    notes=_("Delivery created"),
                    created_by=created_by,
                    updated_by=created_by
                )
            
            logger.info(f"[DELIVERY HANDLER] Delivery {delivery.id} successfully created")
            return delivery
            
        except ValidationError as e:
            logger.error(f"[DELIVERY HANDLER] Validation error when creating delivery: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[DELIVERY HANDLER] Error creating delivery: {str(e)}")
            raise ValidationError(_("Error creating delivery"))
    
    @staticmethod
    @transaction.atomic
    def update_delivery(delivery: Delivery, data: dict, updated_by) -> Delivery:
        """
        Updates an existing delivery with new data.
        
        Args:
            delivery: Existing Delivery instance to update
            data: Dictionary containing updated delivery data
            updated_by: User performing the update
            
        Returns:
            Updated Delivery instance
            
        Raises:
            ValidationError: If data validation fails or status transition is invalid
        """
        try:
            # Validate update
            DeliveryValidator.validate_delivery_update(delivery, data)
            
            # Update related objects
            if 'customer' in data:
                delivery.customer = Customer.objects.get(id=data['customer'])
                
            if 'driver' in data:
                delivery.driver = Employeer.objects.get(id=data['driver'])
                
            if 'vehicle' in data:
                delivery.vehicle = Vehicle.objects.get(id=data['vehicle'])
                
            # Update status (if provided)
            if 'status' in data:
                old_status = delivery.status
                new_status = data['status']
                
                delivery.status = new_status
                
                # If status is 'delivered', record actual arrival time
                if new_status == 'delivered' and not delivery.actual_arrival:
                    delivery.actual_arrival = timezone.now()
                    
                # Create checkpoint for status change
                location = delivery.current_location or {'latitude': 0, 'longitude': 0}
                notes = data.get('notes', f"Status changed from {old_status} to {new_status}")
                
                checkpoint = DeliveryCheckpoint.objects.create(
                    delivery=delivery,
                    location=location,
                    status=new_status,
                    notes=notes,
                    created_by=updated_by,
                    updated_by=updated_by
                )
                
                # Notify via WebSocket
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'delivery_{delivery.id}',
                        {
                            'type': 'status_update',
                            'status': new_status,
                            'delivery_id': str(delivery.id),
                            'timestamp': checkpoint.timestamp.isoformat()
                        }
                    )
                except Exception as e:
                    logger.error(f"[DELIVERY HANDLER] Error sending status update via WebSocket: {str(e)}")
            
            # Update location (if provided)
            if 'current_location' in data:
                delivery.current_location = data['current_location']
                
            # Update ETA (if provided)
            if 'estimated_arrival' in data:
                delivery.estimated_arrival = data['estimated_arrival']
                
            # Update load orders (if provided)
            if 'load' in data:
                loads = [LoadOrder.objects.get(id=load_id) for load_id in data['load']]
                delivery.load.set(loads)
                
            delivery.updated_by = updated_by
            delivery.save()
            
            logger.info(f"[DELIVERY HANDLER] Delivery {delivery.id} successfully updated")
            return delivery
            
        except ValidationError as e:
            logger.error(f"[DELIVERY HANDLER] Validation error when updating delivery: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[DELIVERY HANDLER] Error updating delivery: {str(e)}")
            raise ValidationError(_("Error updating delivery"))
    
    @staticmethod
    @transaction.atomic
    def update_delivery_location(delivery: Delivery, data: dict, updated_by) -> Delivery:
        """
        Updates the current location of a delivery with real-time WebSocket notification.
        
        Args:
            delivery: Existing Delivery instance to update
            data: Dictionary containing location data (latitude, longitude)
            updated_by: User performing the update
            
        Returns:
            Updated Delivery instance
            
        Raises:
            ValidationError: If location data is invalid or delivery is in a terminal state
        """
        try:
            # Validate location update
            DeliveryValidator.validate_location_update(delivery, data)
            
            # Extract coordinates
            latitude = data['latitude']
            longitude = data['longitude']
            
            # Update location
            delivery.current_location = {'latitude': latitude, 'longitude': longitude}
            
            # Update ETA if provided
            if 'estimated_arrival' in data:
                delivery.estimated_arrival = data['estimated_arrival']
                
            delivery.updated_by = updated_by
            delivery.save()
            
            # Create checkpoint if requested
            create_checkpoint = data.get('create_checkpoint', False)
            notes = data.get('notes', '')
            
            if create_checkpoint:
                checkpoint = DeliveryCheckpoint.objects.create(
                    delivery=delivery,
                    location=delivery.current_location,
                    status=delivery.status,
                    notes=notes,
                    created_by=updated_by,
                    updated_by=updated_by
                )
                
            # Notify via WebSocket
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'delivery_{delivery.id}',
                    {
                        'type': 'location_update',
                        'latitude': latitude,
                        'longitude': longitude,
                        'delivery_id': str(delivery.id),
                        'status': delivery.status,
                        'estimated_arrival': delivery.estimated_arrival.isoformat() if delivery.estimated_arrival else None
                    }
                )
            except Exception as e:
                logger.error(f"[DELIVERY HANDLER] Error sending location update via WebSocket: {str(e)}")
                
            logger.info(f"[DELIVERY HANDLER] Location of delivery {delivery.id} successfully updated")
            return delivery
            
        except ValidationError as e:
            logger.error(f"[DELIVERY HANDLER] Validation error when updating location: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[DELIVERY HANDLER] Error updating location: {str(e)}")
            raise ValidationError(_("Error updating location"))
    
    @staticmethod
    @transaction.atomic
    def delete_delivery(delivery: Delivery) -> None:
        """
        Deletes a delivery and all associated data.
        
        Args:
            delivery: Delivery instance to delete
            
        Raises:
            ValidationError: If deletion fails
        """
        try:
            delivery_id = delivery.id
            delivery.delete()
            logger.info(f"[DELIVERY HANDLER] Delivery {delivery_id} successfully deleted")
            
        except Exception as e:
            logger.error(f"[DELIVERY HANDLER] Error deleting delivery: {str(e)}")
            raise ValidationError(_("Error deleting delivery"))
