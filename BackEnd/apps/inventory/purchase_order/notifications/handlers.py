"""
Purchase Order notification handlers
"""
import logging
from contextlib import contextmanager
from threading import Lock
from apps.notifications.base import BaseNotificationHandler
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from ..models import PurchaseOrder, PurchaseOrderItem
from apps.inventory.purchase_order.services.handlers import PurchaseOrderItemChangeService
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)
from decimal import Decimal

logger = logging.getLogger(__name__)

# Lock for synchronization access to the set
_orders_lock = Lock()
_orders_being_deleted = set()

def _mark_order_for_deletion(order_id):
    """
    Marks an order for deletion in a thread-safe manner
    """
    with _orders_lock:
        _orders_being_deleted.add(str(order_id))

def _unmark_order_for_deletion(order_id):
    """
    Removes the deletion mark in a thread-safe manner
    """
    with _orders_lock:
        _orders_being_deleted.discard(str(order_id))

def _is_order_being_deleted(order_id):
    """
    Checks if an order is being deleted in a thread-safe manner
    """
    with _orders_lock:
        return str(order_id) in _orders_being_deleted

class PurchaseOrderNotificationHandler(BaseNotificationHandler):
    """Handler for purchase order notifications."""
    
    @staticmethod
    @receiver(post_save, sender=PurchaseOrder, dispatch_uid='notify_order_created')
    def notify_order_created(sender, instance, created, **kwargs):
        """
        Notifies about the creation of a new order.
        Automatically called when a new PurchaseOrder is created.
        """
        if not created:  # If not a new order, ignore
            return
            
        def send_notification():
            try:
                # Reload the order to make sure we have the latest data
                order = PurchaseOrder.objects.get(pk=instance.pk)
                
                handler = PurchaseOrderNotificationHandler()
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ORDER'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'supplier': order.supplier.name,
                    'total': float(order.total)
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ORDER_CREATED']] % {
                    'order_number': order.order_number,
                    'supplier': order.supplier.name,
                    'total': float(order.total)
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ORDER_CREATED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
                    
            except Exception as e:
                logger.error(f"Error sending order created notification: {str(e)}")
                raise
        
        # Schedule notification to be sent after transaction commit
        from django.db import transaction
        transaction.on_commit(send_notification)
    
    @staticmethod
    @receiver(post_save, sender=PurchaseOrder, dispatch_uid='notify_order_updated')
    def notify_order_updated(sender, instance, created, **kwargs):
        """
        Notifies about the update of a purchase order.
        Automatically called when a PurchaseOrder is updated.
        """
        if created:
            return
            
        try:
            # Check if any field changed besides total
            old_instance = sender.objects.get(pk=instance.pk)
            if (old_instance.supplier_id == instance.supplier_id and 
                old_instance.status == instance.status and
                old_instance.expected_delivery == instance.expected_delivery and
                old_instance.notes == instance.notes and
                old_instance.total == instance.total):
                return
            
            # If only total changed, don't notify (already notified on item change)
            if (old_instance.supplier_id == instance.supplier_id and 
                old_instance.status == instance.status and
                old_instance.expected_delivery == instance.expected_delivery and
                old_instance.notes == instance.notes):
                return
            
            handler = PurchaseOrderNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ORDER'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'order_id': str(instance.id),
                'order_number': instance.order_number,
                'supplier': instance.supplier.name,
                'total': float(instance.total)
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ORDER_UPDATED']] % {
                'order_number': instance.order_number,
                'total': float(instance.total)
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ORDER_UPDATED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending order update notification: {str(e)}")
            raise
    
    @staticmethod
    @receiver(pre_save, sender=PurchaseOrder, dispatch_uid='notify_order_status_changed')
    def notify_order_status_changed(sender, instance, **kwargs):
        """
        Notifies about the change of order status.
        Automatically called before saving a PurchaseOrder.
        """
        if not instance.pk:
            return
            
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status == instance.status:
                return
            
            handler = PurchaseOrderNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ORDER'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'order_id': str(instance.id),
                'order_number': instance.order_number,
                'supplier': instance.supplier.name,
                'old_status': old_instance.status,
                'new_status': instance.status
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ORDER_STATUS_CHANGED']] % {
                'order_number': instance.order_number,
                'old_status': old_instance.status,
                'new_status': instance.status
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ORDER_STATUS_CHANGED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except sender.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error sending order status change notification: {str(e)}")
            raise
    
    @staticmethod
    @receiver(post_save, sender=PurchaseOrderItem, dispatch_uid='notify_item_added')
    def notify_item_added(sender, instance, created, **kwargs):
        """
        Notifies when a new item is added to an existing order.
        Automatically called when a PurchaseOrderItem is created.
        """
        if not created:  # If not a new item, ignore
            return
            
        def send_notification():
            try:
                # Reload the item to make sure we have the latest data
                item = PurchaseOrderItem.objects.select_related(
                    'purchase_order', 
                    'purchase_order__supplier',
                    'product'
                ).get(pk=instance.pk)
                
                # Check if item is being created with the order
                # If order has only this item, it means it's being created now
                items_count = PurchaseOrderItem.objects.filter(
                    purchase_order=item.purchase_order
                ).count()
                
                if items_count <= 1:
                    return
                
                handler = PurchaseOrderNotificationHandler()
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ITEM'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(item.purchase_order.id),
                    'order_number': item.purchase_order.order_number,
                    'supplier': item.purchase_order.supplier.name,
                    'product': item.product.name,
                    'quantity': item.quantity,
                    'total': float(item.purchase_order.total)
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_ADDED']] % {
                    'product': item.product.name,
                    'order_number': item.purchase_order.order_number,
                    'quantity': item.quantity,
                    'total': float(item.purchase_order.total)
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_ADDED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
                    
            except Exception as e:
                logger.error(f"Error handling item added notification: {str(e)}")
                raise
        
        # Schedule notification to be sent after transaction commit
        from django.db import transaction
        transaction.on_commit(send_notification)
    
    @staticmethod
    @receiver(pre_save, sender=PurchaseOrderItem, dispatch_uid='notify_item_changes')
    def notify_item_changes(sender, instance, **kwargs):
        """
        Notifies about changes in item quantity and price.
        Automatically called before saving a PurchaseOrderItem.
        """
        if not instance.pk:  # If it's a new item, don't check changes
            return
            
        try:
            handler = PurchaseOrderNotificationHandler()
            old_instance = sender.objects.get(pk=instance.pk)
            changes = PurchaseOrderItemChangeService.check_changes(instance, old_instance)
            
            if not (changes['quantity_changed'] or changes['price_changed']):
                return
            
            # Calculate the new total of the order
            order = instance.purchase_order
            new_total = 0
            for item in order.items.all():
                if item.pk == instance.pk:
                    # For the item being updated, use the new values
                    new_total += Decimal(str(instance.unit_price)) * Decimal(str(instance.quantity))
                else:
                    # For the other items, use the current values
                    new_total += item.calculate_total()
            
            # Notify quantity change
            if changes['quantity_changed']:
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ITEM'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(instance.purchase_order.id),
                    'order_number': instance.purchase_order.order_number,
                    'supplier': instance.purchase_order.supplier.name,
                    'product': instance.product.name,
                    'old_quantity': changes['old_quantity'],
                    'new_quantity': changes['new_quantity'],
                    'total': float(new_total)  # Use the new calculated total
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_QUANTITY_CHANGED']] % {
                    'product': instance.product.name,
                    'order_number': instance.purchase_order.order_number,
                    'old_quantity': changes['old_quantity'],
                    'new_quantity': changes['new_quantity'],
                    'total': float(new_total)  # Use the new calculated total
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_QUANTITY_CHANGED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
            
            # Notify price change
            if changes['price_changed']:
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['PRICE'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(instance.purchase_order.id),
                    'order_number': instance.purchase_order.order_number,
                    'supplier': instance.purchase_order.supplier.name,
                    'product': instance.product.name,
                    'old_price': float(changes['old_price']),
                    'new_price': float(changes['new_price']),
                    'total': float(new_total)  # Use the new calculated total
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_PRICE_CHANGED']] % {
                    'product': instance.product.name,
                    'order_number': instance.purchase_order.order_number,
                    'old_price': float(changes['old_price']),
                    'new_price': float(changes['new_price']),
                    'total': float(new_total)  # Use the new calculated total
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_PRICE_CHANGED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
                
        except sender.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error handling item changes notification: {str(e)}")
            raise
    
    @staticmethod
    @receiver(pre_delete, sender=PurchaseOrder, dispatch_uid='mark_order_for_deletion')
    def mark_order_for_deletion(sender, instance, **kwargs):
        """
        Marks the order for deletion before the items start being deleted.
        """
        _mark_order_for_deletion(instance.id)
        logger.debug(f"Marked order {instance.id} for deletion")
    
    
    @staticmethod
    @receiver(post_delete, sender=PurchaseOrder, dispatch_uid='notify_order_deleted')
    def notify_order_deleted(sender, instance, **kwargs):
        """
        Notifies about order deletion and removes the deletion mark.
        Automatically called when a PurchaseOrder is deleted.
        """
        try:
            handler = PurchaseOrderNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ORDER'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['WARNING'],
                'order_id': str(instance.id),
                'order_number': instance.order_number,
                'supplier': instance.supplier.name
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ORDER_DELETED']] % {
                'order_number': instance.order_number,
                'supplier': instance.supplier.name
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ORDER_DELETED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['WARNING'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending order deletion notification: {str(e)}")
            raise
        finally:
            # Remove the deletion mark after the order is completely deleted
            _unmark_order_for_deletion(instance.id)
            logger.debug(f"Unmarked order {instance.id} from deletion")

    @staticmethod
    @receiver(post_delete, sender=PurchaseOrderItem, dispatch_uid='notify_item_deleted')
    def notify_item_deleted(sender, instance, **kwargs):
        """
        Notifies about the removal of an item from the order.
        Automatically called when a PurchaseOrderItem is deleted.
        IMPORTANT: Does not notify when the item is deleted due to order deletion.
        """
        try:
            # Use the thread-safe function to check
            if _is_order_being_deleted(instance.purchase_order.id):
                logger.debug(f"Skipping item deletion notification for order {instance.purchase_order.id} as it is being deleted")
                return
            
            handler = PurchaseOrderNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ITEM'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['WARNING'],
                'order_id': str(instance.purchase_order.id),
                'order_number': instance.purchase_order.order_number,
                'supplier': instance.purchase_order.supplier.name,
                'product': instance.product.name
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_DELETED']] % {
                'product': instance.product.name,
                'order_number': instance.purchase_order.order_number
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_DELETED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['WARNING'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending item deletion notification: {str(e)}")
            raise