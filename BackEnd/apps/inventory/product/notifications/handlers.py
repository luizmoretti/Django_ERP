# inventory/product/notifications/handlers.py
import logging
from apps.notifications.base import BaseNotificationHandler
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from ..models import Product
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)

logger = logging.getLogger(__name__)

class ProductNotificationHandler(BaseNotificationHandler):
    """Handler for product-related notifications."""
    
    @classmethod
    @receiver(post_save, sender=Product)
    def notify_product_created(cls, sender, instance, created, **kwargs):
        """
        Notifica sobre criação de produto.
        Automaticamente chamado quando um novo Product é criado.
        """
        if not created:
            return
            
        try:
            recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'product_id': str(instance.id),
                'product_name': instance.name,
                'product_sku': instance.productsku_set.first().sku if instance.productsku_set.exists() else 'N/A',
                'category_name': instance.category.name if instance.category else 'N/A',
                'brand_name': instance.brand.name if instance.brand else 'N/A'
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['PRODUCT_CREATED']] % {
                'name': instance.name,
                'sku': data['product_sku'],
                'category': data['category_name'],
                'brand': data['brand_name']
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['PRODUCT_CREATED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending product creation notification: {str(e)}")
            raise
    
    @classmethod
    def notify_product_updated(cls, product, changes, recipient_ids=None):
        """Notifica sobre atualização de produto."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'product_id': str(product.id),
                'product_name': product.name,
                'product_sku': product.productsku_set.first().sku if product.productsku_set.exists() else 'N/A',
                'changes': changes
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['PRODUCT_UPDATED']] % {
                'name': product.name,
                'sku': data['product_sku'],
                'changes': changes
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['PRODUCT_UPDATED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending product update notification: {str(e)}")
            raise
    
    @classmethod
    def notify_category_changed(cls, product, old_category, new_category, recipient_ids=None):
        """Notifica sobre mudança de categoria do produto."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['CATALOG'])
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'product_id': str(product.id),
                'product_name': product.name,
                'old_category': old_category.name if old_category else 'N/A',
                'new_category': new_category.name if new_category else 'N/A'
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['CATEGORY_CHANGED']] % {
                'name': product.name,
                'old_category': data['old_category'],
                'new_category': data['new_category']
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['CATEGORY_CHANGED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending category change notification: {str(e)}")
            raise
    
    @classmethod
    def notify_brand_changed(cls, product, old_brand, new_brand, recipient_ids=None):
        """Notifica sobre mudança de marca do produto."""
        try:
            if recipient_ids is None:
                recipients = cls.get_recipients_by_type(*RECIPIENT_TYPES['CATALOG'])
                recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'product_id': str(product.id),
                'product_name': product.name,
                'old_brand': old_brand.name if old_brand else 'N/A',
                'new_brand': new_brand.name if new_brand else 'N/A'
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['BRAND_CHANGED']] % {
                'name': product.name,
                'old_brand': data['old_brand'],
                'new_brand': data['new_brand']
            }
            
            cls.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['BRAND_CHANGED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending brand change notification: {str(e)}")
            raise