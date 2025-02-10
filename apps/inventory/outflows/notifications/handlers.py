import logging
from apps.notifications.base import BaseNotificationHandler
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Outflow
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)

logger = logging.getLogger(__name__)

class OutflowNotificationHandler(BaseNotificationHandler):
    """Handler for outflow-related notifications."""
    
    @classmethod
    @receiver(post_save, sender=Outflow)
    def notify_outflow_created(cls, sender, instance, created, **kwargs):
        """
        Notifica sobre criação de saída.
        Automaticamente chamado quando um novo Outflow é criado.
        """
        if not created:
            return
            
        try:
            recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'outflow_id': str(instance.id),
                'customer_name': instance.customer.name,
                'product_name': instance.product.name,
                'quantity': instance.quantity,
                'total_value': float(instance.total_value)
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['OUTFLOW_CREATED']] % {
                'quantity': instance.quantity,
                'product': instance.product.name,
                'customer': instance.customer.name,
                'value': float(instance.total_value)
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['OUTFLOW_CREATED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending outflow creation notification: {str(e)}")
            raise
    
    @classmethod
    def notify_outflow_approved(cls, outflow, approver, recipient_ids=None):
        """Notifica sobre aprovação de saída."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'outflow_id': str(outflow.id),
                'customer_name': outflow.customer.name,
                'product_name': outflow.product.name,
                'quantity': outflow.quantity,
                'total_value': float(outflow.total_value),
                'approver_name': approver.get_full_name() or approver.email
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['OUTFLOW_APPROVED']] % {
                'quantity': outflow.quantity,
                'product': outflow.product.name,
                'customer': outflow.customer.name,
                'value': float(outflow.total_value)
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['OUTFLOW_APPROVED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending outflow approval notification: {str(e)}")
            raise
    
    @classmethod
    def notify_outflow_rejected(cls, outflow, rejector, reason, recipient_ids=None):
        """Notifica sobre rejeição de saída."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['WARNING'],
                'outflow_id': str(outflow.id),
                'customer_name': outflow.customer.name,
                'product_name': outflow.product.name,
                'quantity': outflow.quantity,
                'rejector_name': rejector.get_full_name() or rejector.email,
                'reason': reason
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['OUTFLOW_REJECTED']] % {
                'quantity': outflow.quantity,
                'product': outflow.product.name,
                'customer': outflow.customer.name,
                'reason': reason
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['OUTFLOW_REJECTED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['WARNING'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending outflow rejection notification: {str(e)}")
            raise
    
    @classmethod
    def notify_outflow_delivered(cls, outflow, delivery_date, recipient_ids=None):
        """Notifica sobre entrega de saída."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DELIVERY'])
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'outflow_id': str(outflow.id),
                'customer_name': outflow.customer.name,
                'product_name': outflow.product.name,
                'quantity': outflow.quantity,
                'delivery_date': delivery_date.strftime('%Y-%m-%d %H:%M')
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['OUTFLOW_DELIVERED']] % {
                'quantity': outflow.quantity,
                'product': outflow.product.name,
                'customer': outflow.customer.name,
                'delivery_date': delivery_date.strftime('%Y-%m-%d %H:%M')
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['OUTFLOW_DELIVERED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending outflow delivery notification: {str(e)}")
            raise