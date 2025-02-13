# apps/inventory/purchase_order/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from apps.inventory.supplier.models import SupplierProductPrice
from .models import PurchaseOrderItem
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