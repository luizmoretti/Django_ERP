# apps/inventory/purchase_order/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from core.email_handlers import PurchaseOrderEmailHandler
from apps.inventory.supplier.models import SupplierProductPrice
from .models import PurchaseOrderItem, PurchaseOrder
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=PurchaseOrderItem)
def update_supplier_product_price(sender, instance, created, **kwargs):
    """
    When a purchase order item is created/updated, update the supplier's product price if needed.
    Maintains price history by marking old prices as not current.
    """
    try:
        with transaction.atomic():
            # Get current price if exists
            current_price = SupplierProductPrice.objects.filter(
                supplier=instance.purchase_order.supplier,
                product=instance.product,
                is_current=True
            ).first()

            # If no current price or price has changed, create new price record
            if not current_price or current_price.unit_price != instance.unit_price:
                # Mark all existing prices as not current
                SupplierProductPrice.objects.filter(
                    supplier=instance.purchase_order.supplier,
                    product=instance.product,
                    is_current=True
                ).update(is_current=False)

                # Create new current price
                SupplierProductPrice.objects.create(
                    supplier=instance.purchase_order.supplier,
                    product=instance.product,
                    unit_price=instance.unit_price,
                    is_current=True,
                    created_by=instance.created_by,
                    updated_by=instance.updated_by,
                    companie=instance.companie
                )

                logger.info(
                    f"[SIGNALS - PURCHASE ORDER]Updated price for product {instance.product.name} "
                    f"from supplier {instance.purchase_order.supplier.name} to {instance.unit_price}"
                )
    except Exception as e:
        logger.error(
            f"[SIGNALS - PURCHASE ORDER]Error updating supplier product price: {str(e)}"
        )

@receiver(post_save, sender=PurchaseOrder)
def send_purchase_order_email(sender, instance, created, **kwargs):
    """
    When a purchase order status changes to 'pending', send an email notification to the supplier
    """
    def send_email():
        try:
            # Reloads the instance to ensure that all items are available
            purchase_order = PurchaseOrder.objects.prefetch_related('items__product').get(pk=instance.pk)
            
            if purchase_order.status == 'pending' and purchase_order.items.exists():
                handler = PurchaseOrderEmailHandler()
                success = handler.send_purchase_order_email(purchase_order)
                
                if success:
                    logger.info(
                        f"[SIGNALS - PURCHASE ORDER] Email sent successfully for PO #{purchase_order.order_number} "
                        f"to supplier {purchase_order.supplier.name}"
                    )
                else:
                    logger.error(
                        f"[SIGNALS - PURCHASE ORDER] Failed to send email for PO #{purchase_order.order_number} "
                        f"to supplier {purchase_order.supplier.name}"
                    )
        except Exception as e:
            logger.error(
                f"[SIGNALS - PURCHASE ORDER] Error sending email: {str(e)}",
                exc_info=True
            )
    
    # Sends email only when status changes to 'pending'
    if not created and instance.status == 'pending':
        transaction.on_commit(send_email)
    elif created or instance.status != 'pending':
        print("Email not sent")


@receiver(post_save, sender=PurchaseOrderItem)
def send_purchase_order_email_on_first_item(sender, instance, created, **kwargs):
    """
    When the first item is added to a purchase order with status 'pending', 
    send an email notification to the supplier
    """
    def send_email():
        try:
            # Reloads the instance to ensure that all items are available
            purchase_order = PurchaseOrder.objects.prefetch_related('items__product').get(pk=instance.purchase_order.pk)
            
            # Check that this is the first item and that the status is 'pending'
            items_count = purchase_order.items.count()
            if items_count == 1 and purchase_order.status == 'pending':
                handler = PurchaseOrderEmailHandler()
                success = handler.send_purchase_order_email(purchase_order)
                
                if success:
                    logger.info(
                        f"[SIGNALS - PURCHASE ORDER] Email sent successfully for PO #{purchase_order.order_number} "
                        f"after first item was added"
                    )
                else:
                    logger.error(
                        f"[SIGNALS - PURCHASE ORDER] Failed to send email for PO #{purchase_order.order_number} "
                        f"after first item was added"
                    )
        except Exception as e:
            logger.error(
                f"[SIGNALS - PURCHASE ORDER] Error sending email after first item: {str(e)}",
                exc_info=True
            )
    
    if created:
        transaction.on_commit(send_email)