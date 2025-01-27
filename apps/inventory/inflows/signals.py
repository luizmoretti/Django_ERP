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
            logger.debug(f"InflowItems ID {instance.pk}: Previous quantity stored: {previous.quantity}")
        except InflowItems.DoesNotExist:
            instance._previous_quantity = 0
            logger.debug(f"InflowItems ID {instance.pk}: New record, previous quantity set to 0")
    else:
        instance._previous_quantity = 0
        logger.debug("New InflowItems: previous quantity set to 0")

@receiver(post_save, sender=InflowItems)
def update_quantities_on_inflow(sender, instance, created, **kwargs):
    with transaction.atomic():
        product = instance.product
        warehouse = instance.inflow.destiny
        
        if not product or not warehouse:
            logger.warning(f"InflowItems ID {instance.id} has no associated product or warehouse.")
            return
        
        try:
            # Update product quantity
            if created:
                product.quantity += instance.quantity
            else:
                difference = instance.quantity - getattr(instance, '_previous_quantity', 0)
                product.quantity += difference
            
            if product.quantity < 0:
                logger.error(f"Attempt to set negative quantity for product {str(product)}")
                raise ValueError("Product quantity cannot be negative")
            
            # Update or create WarehouseProduct
            warehouse_product, created = WarehouseProduct.objects.get_or_create(
                warehouse=warehouse,
                product=product,
                defaults={'current_quantity': 0}
            )
            
            if created:
                warehouse_product.current_quantity = instance.quantity
            else:
                if instance._previous_quantity:
                    difference = instance.quantity - instance._previous_quantity
                    warehouse_product.current_quantity += difference
                else:
                    warehouse_product.current_quantity += instance.quantity
            
            if warehouse_product.current_quantity < 0:
                raise ValueError("Warehouse quantity cannot be negative")
            
            # Update total warehouse quantity
            warehouse.quantity += instance.quantity if created else difference
            
            # Save all changes
            product.save(update_fields=['quantity'])
            warehouse_product.save(update_fields=['current_quantity'])
            warehouse.save(update_fields=['quantity'])
            
            logger.info(
                f"InflowItems {instance.id}: Product {product} updated. "
                f"Total quantity: {product.quantity}, "
                f"Quantity in warehouse {warehouse}: {warehouse_product.current_quantity}"
            )
            
        except Exception as e:
            logger.error(f"Error updating quantities in InflowItems {instance.id}: {str(e)}")
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

            # Update product quantity
            product.quantity -= instance.quantity
            if product.quantity < 0:
                logger.error(f"Attempt to set negative quantity for product {str(product)}")
                raise ValueError("Product quantity cannot be negative")
            
            # Update WarehouseProduct
            try:
                warehouse_product = WarehouseProduct.objects.get(
                    warehouse=warehouse,
                    product=product
                )
                warehouse_product.current_quantity -= instance.quantity
                
                if warehouse_product.current_quantity < 0:
                    raise ValueError("Warehouse quantity cannot be negative")
                
                warehouse_product.save(update_fields=['current_quantity'])
                
                # Update total warehouse quantity
                warehouse.quantity -= instance.quantity
                warehouse.save(update_fields=['quantity'])
                
            except WarehouseProduct.DoesNotExist:
                logger.error(f"WarehouseProduct not found for product {product} in warehouse {warehouse}")
                raise
            
            product.save(update_fields=['quantity'])
            
            logger.info(
                f"InflowItems deleted: Product {product} updated. "
                f"Total quantity: {product.quantity}, "
                f"Quantity in warehouse {warehouse}: {warehouse_product.current_quantity}"
            )
                
        except Exception as e:
            logger.error(f"Error updating quantities on InflowItems {instance.id} deletion: {str(e)}")
            raise ValueError(f"Error updating quantities: {str(e)}")