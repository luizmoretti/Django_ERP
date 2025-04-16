import logging
from apps.notifications.models import Notification
from apps.accounts.models import User
from apps.notifications.utils import send_notification
from django.utils.translation import gettext_lazy as _
from apps.notifications.base import BaseNotificationHandler
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_THRESHOLDS,
    SEVERITY_TYPES,
    SEVERITY_LABELS
)

logger = logging.getLogger(__name__)

class WarehouseNotificationHandler(BaseNotificationHandler):
    """
    Handler for warehouse-related notifications.
    
    This class manages notifications specific to warehouse operations,
    particularly focusing on inventory-related alerts.
    """
    
    @staticmethod
    def _calculate_severity(current_quantity: int, min_quantity: int) -> tuple[str, str]:
        """
        Calculate notification severity based on stock levels.
        
        Args:
            current_quantity: Current stock quantity
            min_quantity: Minimum required stock quantity
        
        Returns:
            tuple: (severity_type, severity_label)
            - severity_type: One of SEVERITY_TYPES values
            - severity_label: Human readable label from SEVERITY_LABELS
        """
        if current_quantity <= 0:
            return SEVERITY_TYPES['CRITICAL'], SEVERITY_LABELS[SEVERITY_TYPES['CRITICAL']]
        
        percentage = (current_quantity / min_quantity) * 100
        
        if percentage <= SEVERITY_THRESHOLDS['CRITICAL']:
            return SEVERITY_TYPES['CRITICAL'], SEVERITY_LABELS[SEVERITY_TYPES['CRITICAL']]
        elif percentage <= SEVERITY_THRESHOLDS['WARNING']:
            return SEVERITY_TYPES['WARNING'], SEVERITY_LABELS[SEVERITY_TYPES['WARNING']]
        else:
            return SEVERITY_TYPES['INFO'], SEVERITY_LABELS[SEVERITY_TYPES['INFO']]
    
    @classmethod
    def notify_low_stock(cls, product, warehouse, current_quantity, recipient_ids=None):
        """
        Send notification about low stock levels.
        
        Args:
            product: Product instance
            warehouse: Warehouse instance
            current_quantity: Current stock quantity
            recipient_ids: Optional list of specific recipient IDs
        """
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(
                    'Stock_Controller', 'Manager', 'Owner', 'CEO', 'Admin'
                )
                recipient_ids = [str(user.id) for user in recipients]
            
            severity_type, severity_label = cls._calculate_severity(
                current_quantity, 
                product.min_quantity
            )
            
            percentage = (current_quantity / product.min_quantity) * 100
            
            notification_type = (
                NOTIFICATION_TYPE['OUT_OF_STOCK'] 
                if current_quantity <= 0 
                else NOTIFICATION_TYPE['LOW_STOCK']
            )
            
            message_template = (
                NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['OUT_OF_STOCK']]
                if current_quantity <= 0
                else NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['LOW_STOCK']]
            )
            
            data = {
                'type': severity_type,
                'product_id': str(product.id),
                'product_name': product.name,
                'warehouse_id': str(warehouse.id),
                'warehouse_name': warehouse.name,
                'current_quantity': current_quantity,
                'min_quantity': product.min_quantity,
                'percentage': round(percentage, 1) if current_quantity > 0 else 0
            }
            
            message = message_template % {
                'severity': severity_label,
                'product': product.name,
                'warehouse': warehouse.name,
                'current': current_quantity,
                'percentage': percentage
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[notification_type],
                message=message,
                app_name=APP_NAME,
                notification_type=severity_type,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending low stock notification: {str(e)}")
            raise
    
    @classmethod
    def notify_stock_replenished(cls, product, warehouse, current_quantity, recipient_ids=None):
        """
        Send notification when stock is replenished.
        
        Args:
            product: Product instance
            warehouse: Warehouse instance
            current_quantity: New stock quantity
            recipient_ids: Optional list of specific recipient IDs
        """
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type('Stock_Controller', 'Manager')
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'product_id': str(product.id),
                'product_name': product.name,
                'warehouse_id': str(warehouse.id),
                'warehouse_name': warehouse.name,
                'current_quantity': current_quantity
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['STOCK_REPLENISHED']] % {
                'product': product.name,
                'warehouse': warehouse.name,
                'current': current_quantity
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['STOCK_REPLENISHED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending stock replenished notification: {str(e)}")
            raise