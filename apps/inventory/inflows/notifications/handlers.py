# inventory/inflows/notifications/handlers.py
import logging
from apps.notifications.utils import send_notification
from django.utils.translation import gettext
from apps.accounts.models import NormalUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Inflow
from apps.notifications.base import BaseNotificationHandler

logger = logging.getLogger(__name__)

class InflowNotificationHandler(BaseNotificationHandler):
    """Handler for inflow-related notifications."""
    
    @staticmethod
    @receiver(post_save, sender=Inflow)
    def notify_inflow_received(cls, inflow, recipient_ids=None):
        """Notifica sobre recebimento de entrada."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type('Stock_Controller', 'Manager')
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'inflow_id': str(inflow.id),
                'supplier_name': inflow.supplier.name,
                'product_name': inflow.product.name,
                'quantity': inflow.quantity,
                'total_value': float(inflow.total_value)
            }
            
            message = gettext(
                "New inflow received: %(quantity)d units of %(product)s "
                "from %(supplier)s. Total value: $%(value).2f"
            ) % {
                'quantity': inflow.quantity,
                'product': inflow.product.name,
                'supplier': inflow.supplier.name,
                'value': float(inflow.total_value)
            }
            
            for user_id in recipient_ids:
                send_notification(
                    user_id=user_id,
                    title=gettext("New Inflow Received"),
                    message=message,
                    app_name="inflows",
                    notification_type="info",
                    data=data
                )
                
        except Exception as e:
            logger.error(f"Error sending inflow notification: {str(e)}")
            raise