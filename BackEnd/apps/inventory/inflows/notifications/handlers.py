# inventory/inflows/notifications/handlers.py
import logging
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import Inflow, InflowItems
from apps.notifications.base import BaseNotificationHandler
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    NOTIFICATION_PRIORITIES,
    RECIPIENT_TYPES
)

logger = logging.getLogger(__name__)

class InflowNotificationHandler(BaseNotificationHandler):
    """
    Handler for inflow-related notifications.
    Follows the notification system architecture for consistent handling.
    """
    
    @staticmethod
    def _get_inflow_context(inflow):
        """
        Get common context data for inflow notifications
        
        Args:
            inflow (Inflow): Inflow instance
            
        Returns:
            dict: Context data for notification
        """
        return {
            'inflow_id': str(inflow.id),
            'origin': str(inflow.origin),
            'destiny': str(inflow.destiny),
            'items_count': inflow.items.count(),
            'total_value': float(sum(item.quantity * item.product.price for item in inflow.items.all()))
        }
    
    @staticmethod
    @receiver(post_save, sender=Inflow)
    def notify_inflow_status(sender, instance, created, **kwargs):
        """
        Handle notifications for inflow creation and updates
        """
        if not instance:
            return
        
        def send_notification():
            try:
                # Recarrega a instância para garantir dados atualizados
                instance.refresh_from_db()
            
                # Determine notification type
                if created:
                    notification_type = NOTIFICATION_TYPE['INFLOW_CREATED']
                elif instance.status in ['approved', 'completed']:
                    notification_type = NOTIFICATION_TYPE['INFLOW_APPROVED']
                elif instance.status == 'rejected':
                    notification_type = NOTIFICATION_TYPE['INFLOW_REJECTED']
                else:
                    notification_type = NOTIFICATION_TYPE['INFLOW_UPDATED']

                # Get recipients based on notification type
                handler = InflowNotificationHandler()
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES[notification_type])
                recipient_ids = [str(user.id) for user in recipients]

                # Get common context
                context = InflowNotificationHandler._get_inflow_context(instance)

                # Add status-specific context
                if notification_type == NOTIFICATION_TYPE['INFLOW_APPROVED']:
                    context['approved_by'] = str(instance.updated_by)
                elif notification_type == NOTIFICATION_TYPE['INFLOW_REJECTED']:
                    context['rejected_by'] = str(instance.updated_by)
                    context['reason'] = instance.rejection_reason

                # Format message
                message = NOTIFICATION_MESSAGES[notification_type] % context

                # Determine severity
                severity = (SEVERITY_TYPES['ERROR'] if notification_type == NOTIFICATION_TYPE['INFLOW_REJECTED']
                          else SEVERITY_TYPES['INFO'])

                # Send notification
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[notification_type],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=notification_type,
                    data={
                        'inflow_id': str(instance.id),
                        'status': instance.status,
                        'severity': severity,
                        'priority': NOTIFICATION_PRIORITIES[notification_type],
                        **context
                    }
                )

                logger.info(
                    f"[INFLOW NOTIFICATIONS] Notification sent successfully. Type: {notification_type}",
                    extra={
                        'inflow_id': str(instance.id),
                        'notification_type': notification_type,
                        'recipients_count': len(recipient_ids)
                    }
                )
            except Exception as e:
                logger.error(
                    f"[INFLOW NOTIFICATIONS] Failed to send notification",
                    extra={
                        'inflow_id': str(instance.id),
                        'error': str(e)
                    },
                    exc_info=True
                )
            
        # Registra a função para ser executada após o commit da transação
        transaction.on_commit(lambda: send_notification())
    
    @staticmethod
    @receiver(post_delete, sender=Inflow)
    def notify_inflow_deleted(sender, instance, **kwargs):
        """
        Handle notifications for inflow deletion
        """
        try:
            # Get common context before the instance is deleted
            context = InflowNotificationHandler._get_inflow_context(instance)
            
            # Add deletion-specific context
            context['deleted_by'] = str(instance.updated_by)
            
            # Get recipients based on notification type
            handler = InflowNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES[NOTIFICATION_TYPE['INFLOW_DELETED']])
            recipient_ids = [str(user.id) for user in recipients]
            
            # Send notification immediately since the instance will be deleted
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['INFLOW_DELETED']],
                message=NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['INFLOW_DELETED']] % context,
                app_name=APP_NAME,
                notification_type=NOTIFICATION_TYPE['INFLOW_DELETED'],
                data={
                    'inflow_id': str(instance.id),
                    'status': 'deleted',
                    'severity': SEVERITY_TYPES['WARNING'],
                    'priority': NOTIFICATION_PRIORITIES[NOTIFICATION_TYPE['INFLOW_DELETED']],
                    **context
                }
            )
            
            logger.info(
                "[INFLOW NOTIFICATIONS] Deletion notification sent successfully",
                extra={
                    'inflow_id': str(instance.id),
                    'notification_type': NOTIFICATION_TYPE['INFLOW_DELETED'],
                    'recipients_count': len(recipient_ids)
                }
            )
            
        except Exception as e:
            logger.error(
                "[INFLOW NOTIFICATIONS] Failed to send deletion notification",
                extra={
                    'inflow_id': str(instance.id),
                    'error': str(e)
                },
                exc_info=True
            )
    
    @staticmethod
    def notify_stock_update(warehouse, product, previous_quantity, new_quantity):
        """
        Notify about stock updates and check for low stock
        
        Args:
            warehouse: Warehouse instance
            product: Product instance
            previous_quantity (int): Previous stock quantity
            new_quantity (int): New stock quantity
        """
        try:
            handler = InflowNotificationHandler()
            
            # Stock update notification
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES[NOTIFICATION_TYPE['STOCK_UPDATED']])
            recipient_ids = [str(user.id) for user in recipients]
            
            context = {
                'warehouse': str(warehouse),
                'product': str(product),
                'previous_quantity': previous_quantity,
                'new_quantity': new_quantity
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['STOCK_UPDATED']],
                message=NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['STOCK_UPDATED']] % context,
                app_name=APP_NAME,
                notification_type=NOTIFICATION_TYPE['STOCK_UPDATED'],
                data={
                    'severity': SEVERITY_TYPES['INFO'],
                    'priority': NOTIFICATION_PRIORITIES[NOTIFICATION_TYPE['STOCK_UPDATED']],
                    **context
                }
            )
            
            # Check for low stock
            if new_quantity <= product.min_quantity:
                low_stock_recipients = handler.get_recipients_by_type(
                    *RECIPIENT_TYPES[NOTIFICATION_TYPE['LOW_STOCK_ALERT']]
                )
                low_stock_recipient_ids = [str(user.id) for user in low_stock_recipients]
                
                low_stock_context = {
                    'warehouse': str(warehouse),
                    'product': str(product),
                    'current_quantity': new_quantity,
                    'min_quantity': product.min_quantity
                }
                
                handler.send_to_recipients(
                    recipient_ids=low_stock_recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['LOW_STOCK_ALERT']],
                    message=NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['LOW_STOCK_ALERT']] % low_stock_context,
                    app_name=APP_NAME,
                    notification_type=NOTIFICATION_TYPE['LOW_STOCK_ALERT'],
                    data={
                        'severity': SEVERITY_TYPES['WARNING'],
                        'priority': NOTIFICATION_PRIORITIES[NOTIFICATION_TYPE['LOW_STOCK_ALERT']],
                        **low_stock_context
                    }
                )
            
            logger.info(
                "[INFLOW NOTIFICATIONS] Stock update notification sent successfully",
                extra={
                    'warehouse': str(warehouse),
                    'product': str(product),
                    'new_quantity': new_quantity
                }
            )
            
        except Exception as e:
            logger.error(
                "[INFLOW NOTIFICATIONS] Failed to send stock update notification",
                extra={
                    'warehouse': str(warehouse),
                    'product': str(product),
                    'error': str(e)
                },
                exc_info=True
            )