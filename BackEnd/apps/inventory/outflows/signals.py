import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
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

@receiver(pre_save, sender=OutflowItems)
def validate_quantities(sender, instance, **kwargs):
    """
    Signal to validate quantities before saving an outflow item.
    Raises ValidationError if any quantity would become negative.
    """
    try:
        product = instance.product
        warehouse = instance.outflow.origin
        warehouse_product = WarehouseProduct.objects.get(
            warehouse=warehouse,
            product=product
        )

        # Calculate quantity change
        if not instance.pk:
            quantity_change = instance.quantity
        else:
            previous_quantity = getattr(instance, '_previous_quantity', 0)
            quantity_change = instance.quantity - previous_quantity

        # First validate the quantity itself is not negative
        if instance.quantity < 0:
            logger.error(f"Invalid negative quantity specified: {instance.quantity}")
            raise ValidationError("Quantity cannot be negative")

        # Then validate projected quantities
        projected_warehouse_product_quantity = warehouse_product.current_quantity - quantity_change
        projected_warehouse_quantity = warehouse.quantity - quantity_change
        projected_product_quantity = product.quantity - quantity_change

        if projected_warehouse_product_quantity < 0:
            logger.error(f"Outflow would result in negative warehouse product quantity. Current: {warehouse_product.current_quantity}, Change: -{quantity_change}")
            raise ValidationError(f"Outflow would result in negative warehouse product quantity. Current: {warehouse_product.current_quantity}, Change: -{quantity_change}")

        if projected_warehouse_quantity < 0:
            logger.error(f"Outflow would result in negative warehouse quantity. Current: {warehouse.quantity}, Change: -{quantity_change}")
            raise ValidationError(f"Outflow would result in negative warehouse quantity. Current total: {warehouse.quantity}, Attempted change: -{quantity_change}")

        if projected_product_quantity < 0:
            logger.error(f"Outflow would result in negative product quantity. Current: {product.quantity}, Change: -{quantity_change}")
            raise ValidationError(f"Product quantity cannot be negative. Current: {product.quantity}, Change: -{quantity_change}")

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error validating quantities for outflow item: {str(e)}")
        raise ValidationError(f"Error validating quantities: {str(e)}")

@receiver(post_save, sender=OutflowItems)
def update_quantities_on_outflow(sender, instance, created, **kwargs):
    """
    Signal to update quantities when an outflow item is created or updated.
    """
    try:
        with transaction.atomic():
            product = instance.product
            warehouse = instance.outflow.origin
            warehouse_product = WarehouseProduct.objects.get(
                warehouse=warehouse,
                product=product
            )

            # Calculate quantity change
            if created:
                quantity_change = instance.quantity
            else:
                previous_quantity = getattr(instance, '_previous_quantity', 0)
                quantity_change = instance.quantity - previous_quantity

            # Update Product quantity
            product.quantity -= quantity_change
            product.save()
            
            # Update WarehouseProduct quantity
            # This will trigger update_total_quantity() in WarehouseProduct.save()
            warehouse_product.current_quantity -= quantity_change
            warehouse_product.save()

            logger.info(
                f"Updated quantities for outflow item {instance.id}. "
                f"Product: {product.name}, New quantity: {product.quantity}, "
                f"Warehouse product quantity: {warehouse_product.current_quantity}, "
                f"Total warehouse quantity: {warehouse.quantity}"
            )

    except Exception as e:
        logger.error(f"Error updating quantities for outflow item {str(instance.id)}: {str(e)}")
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
            product.save()
            
            # Restore warehouse quantity
            try:
                warehouse_product = WarehouseProduct.objects.get(
                    warehouse=warehouse,
                    product=product
                )
                warehouse_product.current_quantity += instance.quantity
                warehouse_product.save()
                
                logger.info(
                    f"OutflowItems deleted: Product {product.name} outflow reversed. "
                    f"Origin warehouse {warehouse.name}: {warehouse.quantity}, "
                    f"Product quantity: {product.quantity}, "
                    f"Warehouse product quantity: {warehouse_product.current_quantity}"
                )
            except WarehouseProduct.DoesNotExist:
                logger.warning(f"No warehouse product found for {product.name} in {warehouse.name}")
                
        except Exception as e:
            logger.error(f"Error restoring quantities on outflow delete: {str(e)}")
            raise
