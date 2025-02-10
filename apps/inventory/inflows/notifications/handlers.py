# inventory/inflows/notifications/handlers.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Inflow
from apps.notifications.base import BaseNotificationHandler
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES
)

logger = logging.getLogger(__name__)

class InflowNotificationHandler(BaseNotificationHandler):
    """Handler for inflow-related notifications."""
    
    @classmethod
    @receiver(post_save, sender=Inflow)
    def notify_inflow_received(cls, sender, instance, created, **kwargs):
        """
        Notifica sobre recebimento de entrada.
        Automaticamente chamado quando um novo Inflow é criado.
        """
        if not created:
            return
            
        try:
            recipients = cls.get_recipients_by_type('Stock_Controller', 'Manager')
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'inflow_id': str(instance.id),
                'supplier_name': instance.supplier.name,
                'product_name': instance.product.name,
                'quantity': instance.quantity,
                'total_value': float(instance.total_value)
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['INFLOW_RECEIVED']] % {
                'quantity': instance.quantity,
                'product': instance.product.name,
                'supplier': instance.supplier.name,
                'value': float(instance.total_value)
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['INFLOW_RECEIVED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending inflow notification: {str(e)}")
            raise
    
    @classmethod
    def notify_inflow_approved(cls, inflow, approver, recipient_ids=None):
        """Notifica sobre aprovação de entrada."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type('Stock_Controller', 'Manager')
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'inflow_id': str(inflow.id),
                'supplier_name': inflow.supplier.name,
                'product_name': inflow.product.name,
                'quantity': inflow.quantity,
                'total_value': float(inflow.total_value),
                'approver_name': approver.get_full_name() or approver.email
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['INFLOW_APPROVED']] % {
                'quantity': inflow.quantity,
                'product': inflow.product.name,
                'supplier': inflow.supplier.name,
                'value': float(inflow.total_value)
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['INFLOW_APPROVED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending inflow approval notification: {str(e)}")
            raise
    
    @classmethod
    def notify_inflow_rejected(cls, inflow, rejector, reason, recipient_ids=None):
        """Notifica sobre rejeição de entrada."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type('Stock_Controller', 'Manager')
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['WARNING'],
                'inflow_id': str(inflow.id),
                'supplier_name': inflow.supplier.name,
                'product_name': inflow.product.name,
                'quantity': inflow.quantity,
                'rejector_name': rejector.get_full_name() or rejector.email,
                'reason': reason
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['INFLOW_REJECTED']] % {
                'quantity': inflow.quantity,
                'product': inflow.product.name,
                'supplier': inflow.supplier.name,
                'reason': reason
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['INFLOW_REJECTED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['WARNING'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending inflow rejection notification: {str(e)}")
            raise