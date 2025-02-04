import logging
from apps.notifications.models import Notification
from apps.accounts.models import NormalUser
from apps.notifications.utils import send_notification
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext

logger = logging.getLogger(__name__)

class WarehouseNotificationHandler:
    """
    Handler for warehouse-related notifications.
    
    This class manages notifications specific to warehouse operations,
    particularly focusing on inventory-related alerts.
    """
    
    @staticmethod
    def _calculate_severity(current_quantity, min_quantity):
        """
        Calculate notification severity based on stock levels.
        
        Returns:
            tuple: (severity, severity_label)
            - severity: One of "info", "warning", "critical"
            - severity_label: Human readable label
        """
        if current_quantity <= 0:
            return "critical", gettext("Out of Stock")
        
        percentage = (current_quantity / min_quantity) * 100
        
        if percentage <= 50:
            return "critical", gettext("Critical Low Stock")
        elif percentage <= 90:
            return "warning", gettext("Low Stock")
        else:
            return "info", gettext("Stock Alert")
    
    @staticmethod
    def notify_low_stock(product, warehouse, current_quantity):
        """
        Send notifications for low stock situations.
        
        Args:
            product: Product instance that is low in stock
            warehouse: Warehouse instance where the product is stored
            current_quantity: Current quantity of the product
        """
        try:
            # Get relevant staff (Stock Controllers and Managers)
            recipients = NormalUser.objects.filter(
                user_type__in=['Stock_Controller', 'Manager', 'Admin', 'Owner', 'CEO'],
                is_active=True
            )
            
            if not recipients.exists():
                logger.warning("No active recipients found for low stock notification")
                return
            
            # Calculate severity
            severity, severity_label = WarehouseNotificationHandler._calculate_severity(
                current_quantity, 
                product.min_quantity
            )
            
            notification_data = {
                'severity': severity,
                'percentage': round((current_quantity / product.min_quantity) * 100, 1),
                
                'product_id': str(product.id),
                'product_name': product.name,
                
                'warehouse_id': str(warehouse.id),
                'warehouse_name': warehouse.name,
                
                'current_quantity': current_quantity,
                'min_quantity': product.min_quantity
            }
            
            # Force evaluation of translated strings
            message_template = gettext(
                "%(severity)s: Product %(product)s is low in %(warehouse)s. "
                "Current quantity: %(current)d (%(percentage).1f%% of minimum %(min)d)"
            )
            
            message = message_template % {
                'severity': severity_label,
                'percentage': notification_data['percentage'],
                'product': product.name,
                'warehouse': warehouse.name,
                'current': current_quantity,
                'min': product.min_quantity,
            }
            
            title = severity_label
            
            # Send notification to each recipient
            for recipient in recipients:
                success = send_notification(
                    user_id=recipient.id,
                    title=title,
                    message=message,
                    app_name="warehouse",
                    notification_type=severity,
                    data=notification_data
                )
                
                if success:
                    logger.info(f"[{severity.upper()}] Stock notification sent to {recipient.email}")
                else:
                    logger.error(f"Failed to send stock notification to {recipient.email}")
                    
        except Exception as e:
            logger.error(f"Error sending stock notification: {str(e)}")
            raise