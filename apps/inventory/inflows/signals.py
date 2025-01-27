import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import InflowItems
from ..product.models import Product
from ..warehouse.models import WarehouseProduct

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=InflowItems)
def store_previous_quantity(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = InflowItems.objects.get(pk=instance.pk)
            instance._previous_quantity = previous.quantity
            logger.info(f"InflowItems ID {instance.pk}: Previous quantity stored: {previous.quantity}")
        except InflowItems.DoesNotExist:
            instance._previous_quantity = 0
            logger.info(f"InflowItems ID {instance.pk}: New record, previous quantity set to 0")
    else:
        instance._previous_quantity = 0
        logger.info("New InflowItems: previous quantity set to 0")

@receiver(post_save, sender=InflowItems)
def update_quantities_on_inflow(sender, instance, created, **kwargs):
    with transaction.atomic():
        product = instance.product
        warehouse = instance.inflow.destiny
        
        if not product or not warehouse:
            logger.warning(f"InflowItems ID {instance.id} has no associated product or warehouse.")
            return
        
        try:
            # Get or create WarehouseProduct
            warehouse_product, wp_created = WarehouseProduct.objects.get_or_create(
                warehouse=warehouse,
                product=product,
                defaults={'current_quantity': 0}
            )
            
            if created:
                # New inflow
                warehouse_product.current_quantity += instance.quantity
                product.quantity += instance.quantity
            else:
                # Update - calculate difference
                difference = instance.quantity - getattr(instance, '_previous_quantity', 0)
                warehouse_product.current_quantity += difference
                product.quantity += difference
            
            # Save changes
            warehouse_product.save()
            product.save()
            
            # Update total warehouse quantity
            warehouse.update_total_quantity()
            
            logger.info(
                f"Updated quantities for inflow item {instance.id}. "
                f"Product: {product.name}, New quantity: {product.quantity}, "
                f"Warehouse product quantity: {warehouse_product.current_quantity}"
            )
            
        except Exception as e:
            logger.error(f"Error updating quantities for inflow item {instance.id}: {str(e)}")
            raise

@receiver(post_delete, sender=InflowItems)
def subtract_quantities_on_inflow_delete(sender, instance, **kwargs):
    with transaction.atomic():
        try:
            product = instance.product
            warehouse = instance.inflow.destiny
            
            if not product or not warehouse:
                logger.warning(f"InflowItems ID {instance.id} has no associated product or warehouse.")
                return

            try:
                # Get WarehouseProduct
                warehouse_product = WarehouseProduct.objects.get(
                    warehouse=warehouse,
                    product=product
                )
                
                # Update quantities
                warehouse_product.current_quantity -= instance.quantity
                product.quantity -= instance.quantity
                warehouse.quantity -= instance.quantity
                
                if warehouse_product.current_quantity < 0:
                    raise ValueError("Warehouse product quantity cannot be negative")
                
                if product.quantity < 0:
                    raise ValueError("Product quantity cannot be negative")
                
                # Save all changes
                warehouse_product.save(update_fields=['current_quantity'])
                product.save(update_fields=['quantity'])
                warehouse.save(update_fields=['quantity'])
                
                logger.info(
                    f"InflowItems deleted: Removed {instance.quantity} from product {product}. "
                    f"Current warehouse quantity: {warehouse_product.current_quantity}"
                )
                
            except WarehouseProduct.DoesNotExist:
                logger.error(f"WarehouseProduct not found for product {product} in warehouse {warehouse}")
                raise
                
        except Exception as e:
            logger.error(f"Error updating quantities on InflowItems {instance.id} deletion: {str(e)}")
            raise ValueError(f"Error updating quantities: {str(e)}")