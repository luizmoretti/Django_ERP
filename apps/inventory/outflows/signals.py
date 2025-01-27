import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import OutflowItems
from ..product.models import Product
from ..warehouse.models import WarehouseProduct

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=OutflowItems)
def store_previous_quantity(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = OutflowItems.objects.get(pk=instance.pk)
            instance._previous_quantity = previous.quantity
            logger.debug(f"OutflowItems ID {instance.pk}: Previous quantity stored: {previous.quantity}")
        except OutflowItems.DoesNotExist:
            instance._previous_quantity = 0
            logger.debug(f"OutflowItems ID {instance.pk}: New record, previous quantity set to 0")
    else:
        instance._previous_quantity = 0
        logger.debug("New OutflowItems: previous quantity set to 0")

@receiver(post_save, sender=OutflowItems)
def update_quantities_on_outflow(sender, instance, created, **kwargs):
    with transaction.atomic():
        product = instance.product
        warehouse = instance.outflow.origin
        
        if not product or not warehouse:
            logger.warning(f"OutflowItems ID {instance.id} has no associated product or warehouse.")
            return
        
        try:
            # Update product quantity
            if created:
                product.quantity -= instance.quantity
            else:
                difference = instance.quantity - getattr(instance, '_previous_quantity', 0)
                product.quantity -= difference
            
            if product.quantity < 0:
                logger.error(f"Attempt to set negative quantity for product {str(product)}")
                raise ValueError("Product quantity cannot be negative")
            
            # Update WarehouseProduct
            try:
                warehouse_product = WarehouseProduct.objects.get(
                    warehouse=warehouse,
                    product=product
                )
                
                if created:
                    warehouse_product.current_quantity -= instance.quantity
                else:
                    difference = instance.quantity - getattr(instance, '_previous_quantity', 0)
                    warehouse_product.current_quantity -= difference
                
                if warehouse_product.current_quantity < 0:
                    logger.error(f"Attempt to set negative quantity for warehouse product {str(warehouse_product)}")
                    raise ValueError("Warehouse product quantity cannot be negative")
                
                # Save changes
                warehouse_product.save()
                product.save()
                
                # Update total warehouse quantity
                warehouse.update_total_quantity()
                
                logger.info(
                    f"Updated quantities for outflow item {instance.id}. "
                    f"Product: {product.name}, New quantity: {product.quantity}, "
                    f"Warehouse product quantity: {warehouse_product.current_quantity}"
                )
                
            except WarehouseProduct.DoesNotExist:
                logger.error(f"WarehouseProduct not found for product {str(product)} in warehouse {str(warehouse)}")
                raise
                
        except Exception as e:
            logger.error(f"Error updating quantities for outflow item {instance.id}: {str(e)}")
            raise

@receiver(post_delete, sender=OutflowItems)
def restore_quantities_on_outflow_delete(sender, instance, **kwargs):
    with transaction.atomic():
        try:
            product = instance.product
            warehouse = instance.outflow.origin
            
            if not product or not warehouse:
                logger.warning(f"OutflowItems ID {instance.id} has no associated product or warehouse.")
                return

            # Restore product quantity
            product.quantity += instance.quantity
            
            # Restore warehouse quantity
            try:
                warehouse_product = WarehouseProduct.objects.get(
                    warehouse=warehouse,
                    product=product
                )
                warehouse_product.current_quantity += instance.quantity
                
                # Update total warehouse quantity
                warehouse.quantity += instance.quantity
                
                warehouse_product.save(update_fields=['current_quantity'])
                warehouse.save(update_fields=['quantity'])
                
            except WarehouseProduct.DoesNotExist:
                logger.error(f"WarehouseProduct not found for product {product} in warehouse {warehouse}")
                raise
            
            product.save(update_fields=['quantity'])
            
            logger.info(
                f"OutflowItems deleted: Product {product} updated. "
                f"Total quantity: {product.quantity}, "
                f"Quantity in warehouse {warehouse}: {warehouse_product.current_quantity}"
            )
                
        except Exception as e:
            logger.error(f"Error restoring quantities on OutflowItems {instance.id} deletion: {str(e)}")
            raise ValueError(f"Error restoring quantities: {str(e)}")