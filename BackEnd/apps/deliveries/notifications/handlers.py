from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.notifications.base import BaseNotificationHandler
from apps.deliveries.models import Delivery
from apps.deliveries.tracking.models import DeliveryLocationUpdate, DeliveryStatusUpdate
from .constants import (
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)
import logging

logger = logging.getLogger(__name__)

class DeliveryNotificationHandler(BaseNotificationHandler):
    """
    Handles notifications for delivery events.
    """
    
    @receiver(post_save, sender=Delivery)
    def notify_delivery_created(sender, instance, created, **kwargs):
        """
        Sends notification when a new delivery is created.
        """
        try:
            if created:
                notification_type = NOTIFICATION_TYPE['DELIVERY_CREATED']
                title = NOTIFICATION_TITLES[notification_type]
                message = NOTIFICATION_MESSAGES[notification_type].format(instance.number)
                severity = SEVERITY_TYPES[notification_type]
                
                # Get recipients
                recipients = DeliveryNotificationHandler.get_recipients_by_type(
                    *RECIPIENT_TYPES['DELIVERY_ADMIN']
                )
                
                # Prepare data
                data = {
                    'delivery_id': str(instance.id),
                    'delivery_number': instance.number,
                    'origin': instance.origin,
                    'destiny': instance.destiny,
                    'created_at': instance.created_at.isoformat(),
                }
                
                # Send notification
                DeliveryNotificationHandler.send_to_recipients(
                    recipient_ids=[str(user.id) for user in recipients],
                    title=title,
                    message=message,
                    app_name='deliveries',
                    notification_type=severity,
                    data=data
                )
                
                logger.info(f"Delivery created notification sent for delivery {instance.number}")
        except Exception as e:
            logger.error(f"Error sending delivery created notification: {str(e)}")
    
    @receiver(post_save, sender=DeliveryStatusUpdate)
    def notify_status_changed(sender, instance, created, **kwargs):
        """
        Sends notification when a delivery status changes.
        """
        try:
            if created:
                notification_type = NOTIFICATION_TYPE['DELIVERY_STATUS_CHANGED']
                title = NOTIFICATION_TITLES[notification_type]
                message = NOTIFICATION_MESSAGES[notification_type].format(
                    instance.delivery.number, instance.status
                )
                severity = SEVERITY_TYPES[notification_type]
                
                # Get recipients
                recipients = DeliveryNotificationHandler.get_recipients_by_type(
                    *RECIPIENT_TYPES['DELIVERY_ADMIN']
                )
                
                # Add delivery operators
                operator_recipients = DeliveryNotificationHandler.get_recipients_by_type(
                    *RECIPIENT_TYPES['DELIVERY_OPERATOR']
                )
                recipients = list(set(list(recipients) + list(operator_recipients)))
                
                # Prepare data
                data = {
                    'delivery_id': str(instance.delivery.id),
                    'delivery_number': instance.delivery.number,
                    'status': instance.status,
                    'previous_status': instance.delivery.status,
                    'notes': instance.notes,
                    'updated_at': instance.created_at.isoformat(),
                }
                
                # Send notification
                DeliveryNotificationHandler.send_to_recipients(
                    recipient_ids=[str(user.id) for user in recipients],
                    title=title,
                    message=message,
                    app_name='deliveries',
                    notification_type=severity,
                    data=data
                )
                
                logger.info(f"Status change notification sent for delivery {instance.delivery.number}")
        except Exception as e:
            logger.error(f"Error sending status change notification: {str(e)}")
    
    @receiver(post_save, sender=DeliveryLocationUpdate)
    def notify_location_updated(sender, instance, created, **kwargs):
        """
        Sends notification when a delivery location is updated.
        Only sends notifications for significant location updates to avoid spam.
        """
        try:
            if created:
                # Check if this is a significant update (e.g., every 15 minutes or significant distance change)
                # This logic would need to be implemented based on your specific requirements
                
                # For now, we'll just check if this is the first update or if it's been a while since the last one
                previous_updates = DeliveryLocationUpdate.objects.filter(
                    delivery=instance.delivery
                ).exclude(id=instance.id).order_by('-created_at')
                
                # If this is the first update or it's been more than 15 minutes since the last one
                if not previous_updates.exists() or (
                    instance.created_at - previous_updates.first().created_at
                ).total_seconds() > 900:  # 15 minutes = 900 seconds
                    
                    notification_type = NOTIFICATION_TYPE['DELIVERY_LOCATION_UPDATED']
                    title = NOTIFICATION_TITLES[notification_type]
                    message = NOTIFICATION_MESSAGES[notification_type].format(instance.delivery.number)
                    severity = SEVERITY_TYPES[notification_type]
                    
                    # Get recipients (only admin and operators for location updates)
                    recipients = DeliveryNotificationHandler.get_recipients_by_type(
                        *RECIPIENT_TYPES['DELIVERY_ADMIN']
                    )
                    
                    # Prepare data
                    data = {
                        'delivery_id': str(instance.delivery.id),
                        'delivery_number': instance.delivery.number,
                        'latitude': instance.location.y,
                        'longitude': instance.location.x,
                        'accuracy': instance.accuracy,
                        'speed': instance.speed,
                        'heading': instance.heading,
                        'updated_at': instance.created_at.isoformat(),
                    }
                    
                    # Send notification
                    DeliveryNotificationHandler.send_to_recipients(
                        recipient_ids=[str(user.id) for user in recipients],
                        title=title,
                        message=message,
                        app_name='deliveries',
                        notification_type=severity,
                        data=data
                    )
                    
                    logger.info(f"Location update notification sent for delivery {instance.delivery.number}")
        except Exception as e:
            logger.error(f"Error sending location update notification: {str(e)}")
            
    # Additional notification methods can be added here for other delivery events