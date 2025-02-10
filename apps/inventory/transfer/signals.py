import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import TransferItems
from ..product.models import Product
from ..warehouse.models import WarehouseProduct

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=TransferItems)
def validate_transfer_quantities(sender, instance, **kwargs):
    """Validate transfer quantities before saving"""
    with transaction.atomic():
        try:
            product = instance.product
            origin_warehouse = instance.transfer.origin
            destiny_warehouse = instance.transfer.destiny

            if not all([product, origin_warehouse, destiny_warehouse]):
                raise ValidationError("Missing product or warehouse information")

            # Get or create WarehouseProduct for origin
            origin_warehouse_product, _ = WarehouseProduct.objects.get_or_create(
                warehouse=origin_warehouse,
                product=product,
                defaults={'current_quantity': 0}
            )

            # Calculate quantity change
            if not instance.pk:  # New instance
                quantity_change = instance.quantity
            else:
                try:
                    previous = TransferItems.objects.get(pk=instance.pk)
                    quantity_change = instance.quantity - previous.quantity
                except TransferItems.DoesNotExist:
                    quantity_change = instance.quantity

            # Validate origin warehouse has enough quantity
            if not instance.pk:  # For new transfers, check total quantity
                if origin_warehouse_product.current_quantity < quantity_change:
                    logger.error(f"Insufficient quantity in origin warehouse. Available: {origin_warehouse_product.current_quantity}, Requested: {quantity_change}")
                    raise ValidationError(f"Insufficient quantity in origin warehouse. Available: {origin_warehouse_product.current_quantity}, Requested: {quantity_change}")
            else:  # For updates, check if the change would make quantity negative
                projected_origin_quantity = origin_warehouse_product.current_quantity - quantity_change
                if projected_origin_quantity < 0:
                    logger.error(f"Insufficient quantity in origin warehouse. Available: {origin_warehouse_product.current_quantity}, Requested change: {quantity_change}")
                    raise ValidationError(f"Insufficient quantity in origin warehouse. Available: {origin_warehouse_product.current_quantity}, Requested change: {quantity_change}")

            # Validate destiny warehouse capacity
            if destiny_warehouse.limit > 0:  # Only check if limit is set
                projected_total = destiny_warehouse.quantity + quantity_change
                if projected_total > destiny_warehouse.limit:
                    logger.error(
                        f"Transfer would exceed destiny warehouse capacity. "
                        f"Current: {destiny_warehouse.quantity}, "
                        f"Change: {quantity_change}, "
                        f"Limit: {destiny_warehouse.limit}"
                    )
                    raise ValidationError(
                        f"Transfer would exceed warehouse capacity limit of {destiny_warehouse.limit}. "
                        f"Current total: {destiny_warehouse.quantity}, Attempted change: {quantity_change}"
                    )

                # Warn if approaching capacity
                if projected_total >= (destiny_warehouse.limit * 0.9):
                    logger.warning(
                        f"Destiny warehouse {destiny_warehouse.name} will be at "
                        f"{(projected_total/destiny_warehouse.limit)*100:.1f}% capacity after this transfer"
                    )

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating transfer quantities: {str(e)}")
            raise ValidationError(f"Error validating transfer quantities: {str(e)}")

@receiver(post_save, sender=TransferItems)
def update_quantities_on_transfer(sender, instance, created, **kwargs):
    with transaction.atomic():
        try:
            product = instance.product
            origin_warehouse = instance.transfer.origin
            destiny_warehouse = instance.transfer.destiny
            
            if not all([product, origin_warehouse, destiny_warehouse]):
                logger.warning(f"TransferItems ID {instance.id} has missing product or warehouses.")
                return
            
            # Get or create WarehouseProduct for origin and destiny
            origin_warehouse_product, _ = WarehouseProduct.objects.get_or_create(
                warehouse=origin_warehouse,
                product=product,
                defaults={'current_quantity': 0}
            )
            
            destiny_warehouse_product, _ = WarehouseProduct.objects.get_or_create(
                warehouse=destiny_warehouse,
                product=product,
                defaults={'current_quantity': 0}
            )
            
            # Calculate quantity change
            if created:
                quantity_change = instance.quantity
            else:
                quantity_change = instance.quantity - getattr(instance, '_previous_quantity', 0)
            
            # Update quantities
            origin_warehouse_product.current_quantity -= quantity_change
            destiny_warehouse_product.current_quantity += quantity_change
            
            # Final validation check
            if origin_warehouse_product.current_quantity < 0:
                raise ValidationError("Origin warehouse product quantity cannot be negative")
                
            if destiny_warehouse_product.current_quantity < 0:
                raise ValidationError("Destiny warehouse product quantity cannot be negative")
            
            # Save changes
            origin_warehouse_product.save()
            destiny_warehouse_product.save()
            
            # Update total quantities
            origin_warehouse.update_total_quantity()
            destiny_warehouse.update_total_quantity()
            
            logger.info(
                f"Updated quantities for transfer item {instance.id}. "
                f"Origin warehouse ({origin_warehouse.name}) quantity: {origin_warehouse_product.current_quantity}, "
                f"Destiny warehouse ({destiny_warehouse.name}) quantity: {destiny_warehouse_product.current_quantity}"
            )
            
        except Exception as e:
            logger.error(f"Error updating quantities for transfer item {instance.id}: {str(e)}")
            raise ValidationError(f"Error updating quantities: {str(e)}")

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
                destiny_warehouse_product.current_quantity -= instance.quantity
                
                if origin_warehouse_product.current_quantity < 0:
                    raise ValidationError("Origin warehouse quantity cannot be negative")
                    
                if destiny_warehouse_product.current_quantity < 0:
                    raise ValidationError("Destiny warehouse quantity cannot be negative")
                
                # Save changes
                origin_warehouse_product.save()
                destiny_warehouse_product.save()
                
                # Update total quantities
                origin_warehouse.update_total_quantity()
                destiny_warehouse.update_total_quantity()
                
                logger.info(
                    f"TransferItems deleted: Product {product} transfer reversed. "
                    f"Origin warehouse {origin_warehouse}: {origin_warehouse_product.current_quantity}, "
                    f"Destiny warehouse {destiny_warehouse}: {destiny_warehouse_product.current_quantity}"
                )
                
            except WarehouseProduct.DoesNotExist:
                logger.error(f"WarehouseProduct not found for product {product} in one of the warehouses")
                raise ValidationError("WarehouseProduct not found in one of the warehouses")
                
        except Exception as e:
            logger.error(f"Error restoring quantities on TransferItems {instance.id} deletion: {str(e)}")
            raise ValidationError(f"Error restoring quantities: {str(e)}")
