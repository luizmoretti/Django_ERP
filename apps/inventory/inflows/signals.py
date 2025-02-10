import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import InflowItems
from ..product.models import Product
from ..warehouse.models import WarehouseProduct

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=InflowItems)
def store_previous_quantity(sender, instance, **kwargs):
    """Store previous quantity before changes"""
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

@receiver(pre_save, sender=InflowItems)
def validate_inflow_capacity(sender, instance, **kwargs):
    """Validate warehouse capacity before saving"""
    warehouse = instance.inflow.destiny
    
    if not warehouse.limit:  # No limit set
        return
        
    # Calculate quantity change
    if instance.pk:
        try:
            previous = InflowItems.objects.get(pk=instance.pk)
            quantity_change = instance.quantity - previous.quantity
        except InflowItems.DoesNotExist:
            quantity_change = instance.quantity
    else:
        quantity_change = instance.quantity
    
    # Calculate projected total
    projected_total = warehouse.quantity + quantity_change
    
    # Check if total would exceed limit
    if projected_total > warehouse.limit:
        logger.error(f"Inflow would exceed warehouse capacity. Current: {warehouse.quantity}, Change: {quantity_change}, Limit: {warehouse.limit}")
        raise ValidationError(
            f"Operation would exceed warehouse capacity. "
            f"Current: {warehouse.quantity}, "
            f"Change: {quantity_change}, "
            f"Limit: {warehouse.limit}"
        )

@receiver(post_save, sender=InflowItems)
def update_quantities_on_inflow(sender, instance, created, **kwargs):
    """Update quantities after successful validation"""
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
                quantity_change = instance.quantity
            else:
                # Update - calculate difference
                quantity_change = instance.quantity - getattr(instance, '_previous_quantity', 0)
            
            # Update WarehouseProduct quantity
            warehouse_product.current_quantity += quantity_change
            warehouse_product.save()
            
            # Update Product quantity
            product.quantity += quantity_change
            product.save()
            
            # Update Warehouse total quantity
            warehouse.quantity = warehouse.get_total_quantity()
            warehouse.save()
            
            logger.info(
                f"Updated quantities for inflow item {instance.id}. "
                f"Product: {product.name}, New quantity: {product.quantity}, "
                f"Warehouse product quantity: {warehouse_product.current_quantity}, "
                f"Total warehouse quantity: {warehouse.quantity}"
            )
            
        except Exception as e:
            logger.error(f"Error updating quantities for inflow item {instance.id}: {str(e)}")
            transaction.set_rollback(True)
            raise

@receiver(post_delete, sender=InflowItems)
def subtract_quantities_on_inflow_delete(sender, instance, **kwargs):
    """Subtract quantities when inflow is deleted"""
    with transaction.atomic():
        try:
            product = instance.product
            warehouse = instance.inflow.destiny
            
            if not product or not warehouse:
                logger.warning(f"InflowItems ID {instance.id} has no associated product or warehouse.")
                return
            
            # Get warehouse product
            try:
                warehouse_product = WarehouseProduct.objects.get(
                    warehouse=warehouse,
                    product=product
                )
                
                # Update quantities
                warehouse_product.current_quantity -= instance.quantity
                product.quantity -= instance.quantity
                
                # Save changes
                warehouse_product.save()
                product.save()
                
                # Update total warehouse quantity
                warehouse.update_total_quantity()
                
                logger.info(
                    f"InflowItems deleted: Removed {instance.quantity} from product {product.name}. "
                    f"Current warehouse quantity: {warehouse_product.current_quantity}"
                )
                
            except WarehouseProduct.DoesNotExist:
                logger.warning(
                    f"WarehouseProduct not found for inflow item {instance.id}. "
                    f"Product: {product.name}, Warehouse: {warehouse.name}"
                )
                
        except Exception as e:
            logger.error(f"Error subtracting quantities for inflow item {instance.id}: {str(e)}")
            transaction.set_rollback(True)
            raise
