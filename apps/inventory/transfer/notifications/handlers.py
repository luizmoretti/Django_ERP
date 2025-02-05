import logging
from apps.notifications.base import BaseNotificationHandler
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Transfer
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)

logger = logging.getLogger(__name__)

class TransferNotificationHandler(BaseNotificationHandler):
    """Handler for transfer-related notifications."""
    
    @classmethod
    @receiver(post_save, sender=Transfer)
    def notify_transfer_created(cls, sender, instance, created, **kwargs):
        """
        Notifica sobre criação de transferência.
        Automaticamente chamado quando uma nova Transfer é criada.
        """
        if not created:
            return
            
        try:
            recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
            recipient_ids = [str(user.id) for user in recipients]
            
            # Get total quantity from transfer items
            total_quantity = sum(item.quantity for item in instance.items.all())
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'transfer_id': str(instance.id),
                'origin_warehouse': instance.origin.name,
                'destiny_warehouse': instance.destiny.name,
                'total_quantity': total_quantity,
                'items_count': instance.items.count()
            }
            
            # Get first item for message (if multiple items, indicate this)
            first_item = instance.items.first()
            product_info = f"{first_item.product.name}"
            if instance.items.count() > 1:
                product_info += f" and {instance.items.count() - 1} other products"
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['TRANSFER_CREATED']] % {
                'quantity': total_quantity,
                'product': product_info,
                'origin': instance.origin.name,
                'destiny': instance.destiny.name
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['TRANSFER_CREATED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending transfer creation notification: {str(e)}")
            raise
    
    @classmethod
    def notify_transfer_approved(cls, transfer, approver, recipient_ids=None):
        """Notifica sobre aprovação de transferência."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['WAREHOUSE'])
                recipient_ids = [str(user.id) for user in recipients]
            
            total_quantity = sum(item.quantity for item in transfer.items.all())
            first_item = transfer.items.first()
            product_info = f"{first_item.product.name}"
            if transfer.items.count() > 1:
                product_info += f" and {transfer.items.count() - 1} other products"
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'transfer_id': str(transfer.id),
                'origin_warehouse': transfer.origin.name,
                'destiny_warehouse': transfer.destiny.name,
                'total_quantity': total_quantity,
                'items_count': transfer.items.count(),
                'approver_name': approver.get_full_name() or approver.email
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['TRANSFER_APPROVED']] % {
                'quantity': total_quantity,
                'product': product_info,
                'origin': transfer.origin.name,
                'destiny': transfer.destiny.name
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['TRANSFER_APPROVED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending transfer approval notification: {str(e)}")
            raise
    
    @classmethod
    def notify_transfer_rejected(cls, transfer, rejector, reason, recipient_ids=None):
        """Notifica sobre rejeição de transferência."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
                recipient_ids = [str(user.id) for user in recipients]
            
            total_quantity = sum(item.quantity for item in transfer.items.all())
            first_item = transfer.items.first()
            product_info = f"{first_item.product.name}"
            if transfer.items.count() > 1:
                product_info += f" and {transfer.items.count() - 1} other products"
            
            data = {
                'type': SEVERITY_TYPES['WARNING'],
                'transfer_id': str(transfer.id),
                'origin_warehouse': transfer.origin.name,
                'destiny_warehouse': transfer.destiny.name,
                'total_quantity': total_quantity,
                'items_count': transfer.items.count(),
                'rejector_name': rejector.get_full_name() or rejector.email,
                'reason': reason
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['TRANSFER_REJECTED']] % {
                'quantity': total_quantity,
                'product': product_info,
                'origin': transfer.origin.name,
                'destiny': transfer.destiny.name,
                'reason': reason
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['TRANSFER_REJECTED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['WARNING'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending transfer rejection notification: {str(e)}")
            raise
    
    @classmethod
    def notify_transfer_completed(cls, transfer, recipient_ids=None):
        """Notifica sobre conclusão de transferência."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['WAREHOUSE'])
                recipient_ids = [str(user.id) for user in recipients]
            
            total_quantity = sum(item.quantity for item in transfer.items.all())
            first_item = transfer.items.first()
            product_info = f"{first_item.product.name}"
            if transfer.items.count() > 1:
                product_info += f" and {transfer.items.count() - 1} other products"
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'transfer_id': str(transfer.id),
                'origin_warehouse': transfer.origin.name,
                'destiny_warehouse': transfer.destiny.name,
                'total_quantity': total_quantity,
                'items_count': transfer.items.count()
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['TRANSFER_COMPLETED']] % {
                'quantity': total_quantity,
                'product': product_info,
                'origin': transfer.origin.name,
                'destiny': transfer.destiny.name
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['TRANSFER_COMPLETED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending transfer completion notification: {str(e)}")
            raise