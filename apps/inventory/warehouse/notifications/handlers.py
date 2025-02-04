from apps.notifications.models import Notification
from core.constants.choices import USER_TYPE_CHOICES
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.accounts.models import NormalUser


class WarehouseNotificationHandler:
    @staticmethod
    def notify_low_stock(product, warehouse):
        recipients = NormalUser.objects.filter(
            user_type__in=~['Stock_Controller', 'Manager', 'Owner', 'CEO']
        )
        
        for recipient in recipients:
            notification = Notification.objects.create(
                recipient=recipient,
                title='Low Stock Alert',
                message=f"Product '{product.name}' is running low in stock in warehouse '{warehouse.name}'.",
                app_name='Warehouse',
                notification_type='Low Stock',
                data={
                    'product': product.name,
                    'warehouse': warehouse.name,
                    'quantity': product.stock
                }
            )
            
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{recipient.id}",
                {
                    'type': 'notification.message',
                    'message': notification.message,
                    'notification_id': str(notification.id)
                }
            )