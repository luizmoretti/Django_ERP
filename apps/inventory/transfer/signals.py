import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import TransferItems
from ..product.models import Product
from ..warehouse.models import WarehouseProduct

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=TransferItems)
def store_previous_quantity(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = TransferItems.objects.get(pk=instance.pk)
            instance._previous_quantity = previous.quantity
            logger.debug(f"TransferItems ID {instance.pk}: Previous quantity stored: {previous.quantity}")
        except TransferItems.DoesNotExist:
            instance._previous_quantity = 0
            logger.debug(f"TransferItems ID {instance.pk}: New record, previous quantity set to 0")
    else:
        instance._previous_quantity = 0
        logger.debug("New TransferItems: previous quantity set to 0")

@receiver(post_save, sender=TransferItems)
def update_quantities_on_transfer(sender, instance, created, **kwargs):
    with transaction.atomic():
        product = instance.product
        origin_warehouse = instance.transfer.origin
        destiny_warehouse = instance.transfer.destiny
        
        if not all([product, origin_warehouse, destiny_warehouse]):
            logger.warning(f"TransferItems ID {instance.id} has missing product or warehouses.")
            return
        
        try:
            # Get or create WarehouseProduct for origin
            origin_warehouse_product, _ = WarehouseProduct.objects.get_or_create(
                warehouse=origin_warehouse,
                product=product,
                defaults={'current_quantity': 0}
            )
            
            # Get or create WarehouseProduct for destiny
            destiny_warehouse_product, _ = WarehouseProduct.objects.get_or_create(
                warehouse=destiny_warehouse,
                product=product,
                defaults={'current_quantity': 0}
            )
            
            if created:
                # Subtract from origin
                origin_warehouse_product.current_quantity -= instance.quantity
                origin_warehouse.quantity -= instance.quantity
                
                # Add to destiny
                destiny_warehouse_product.current_quantity += instance.quantity
                destiny_warehouse.quantity += instance.quantity
                
            else:
                # Calculate difference from previous quantity
                difference = instance.quantity - getattr(instance, '_previous_quantity', 0)
                
                # Update origin
                origin_warehouse_product.current_quantity -= difference
                origin_warehouse.quantity -= difference
                
                # Update destiny
                destiny_warehouse_product.current_quantity += difference
                destiny_warehouse.quantity += difference
            
            # Validate quantities
            if origin_warehouse_product.current_quantity < 0:
                raise ValueError("Origin warehouse quantity cannot be negative")
                
            if destiny_warehouse_product.current_quantity < 0:
                raise ValueError("Destiny warehouse quantity cannot be negative")
            
            # Save all changes
            origin_warehouse_product.save(update_fields=['current_quantity'])
            destiny_warehouse_product.save(update_fields=['current_quantity'])
            origin_warehouse.save(update_fields=['quantity'])
            destiny_warehouse.save(update_fields=['quantity'])
            
            logger.info(
                f"TransferItems {instance.id}: Product {product} transferred. "
                f"Origin warehouse {origin_warehouse}: {origin_warehouse_product.current_quantity}, "
                f"Destiny warehouse {destiny_warehouse}: {destiny_warehouse_product.current_quantity}"
            )
            
        except Exception as e:
            logger.error(f"Error updating quantities in TransferItems {instance.id}: {str(e)}")
            raise

@receiver(post_delete, sender=TransferItems)
def restore_quantities_on_transfer_delete(sender, instance, **kwargs):
    with transaction.atomic():
        try:
            product = instance.product
            origin_warehouse = instance.transfer.origin
            destiny_warehouse = instance.transfer.destiny
            
            if not all([product, origin_warehouse, destiny_warehouse]):
                logger.warning(f"TransferItems ID {instance.id} has missing product or warehouses.")
                return

            # Get WarehouseProducts
            try:
                origin_warehouse_product = WarehouseProduct.objects.get(
                    warehouse=origin_warehouse,
                    product=product
                )
                destiny_warehouse_product = WarehouseProduct.objects.get(
                    warehouse=destiny_warehouse,
                    product=product
                )
                
                # Restore quantities
                origin_warehouse_product.current_quantity += instance.quantity
                origin_warehouse.quantity += instance.quantity
                
                destiny_warehouse_product.current_quantity -= instance.quantity
                destiny_warehouse.quantity -= instance.quantity
                
                if origin_warehouse_product.current_quantity < 0:
                    raise ValueError("Origin warehouse quantity cannot be negative")
                    
                if destiny_warehouse_product.current_quantity < 0:
                    raise ValueError("Destiny warehouse quantity cannot be negative")
                
                # Save all changes
                origin_warehouse_product.save(update_fields=['current_quantity'])
                destiny_warehouse_product.save(update_fields=['current_quantity'])
                origin_warehouse.save(update_fields=['quantity'])
                destiny_warehouse.save(update_fields=['quantity'])
                
                logger.info(
                    f"TransferItems deleted: Product {product} transfer reversed. "
                    f"Origin warehouse {origin_warehouse}: {origin_warehouse_product.current_quantity}, "
                    f"Destiny warehouse {destiny_warehouse}: {destiny_warehouse_product.current_quantity}"
                )
                
            except WarehouseProduct.DoesNotExist:
                logger.error(f"WarehouseProduct not found for product {product} in one of the warehouses")
                raise
                
        except Exception as e:
            logger.error(f"Error restoring quantities on TransferItems {instance.id} deletion: {str(e)}")
            raise ValueError(f"Error restoring quantities: {str(e)}")