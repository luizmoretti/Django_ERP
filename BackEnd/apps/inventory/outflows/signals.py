import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Outflow, OutflowItems
from ..warehouse.models import WarehouseProduct

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Outflow)
def store_previous_outflow_status(sender, instance, **kwargs):
    """Store previous outflow status before changes"""
    if instance.pk:
        try:
            previous = Outflow.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
            logger.info(f"Outflow ID {instance.pk}: Previous status stored: {previous.status}")
        except Outflow.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None

@receiver(pre_save, sender=OutflowItems)
def store_previous_quantity(sender, instance, **kwargs):
    """Store previous quantity before changes"""
    if instance.pk:
        try:
            previous = OutflowItems.objects.get(pk=instance.pk)
            instance._previous_quantity = previous.quantity
        except OutflowItems.DoesNotExist:
            instance._previous_quantity = 0
    else:
        instance._previous_quantity = 0

@receiver(pre_save, sender=OutflowItems)
def validate_quantities(sender, instance, **kwargs):
    """Validate if warehouse has enough quantity"""
    # Skip validation for non-approved outflows (will be checked at approval time)
    if hasattr(instance, 'outflow') and instance.outflow and instance.outflow.status != 'approved':
        return
        
    # Also skip if we're in the middle of an approval
    if hasattr(instance.outflow, '_previous_status') and instance.outflow._previous_status != 'approved':
        return
    
    warehouse = instance.outflow.origin
    product = instance.product
    
    try:
        # Get current warehouse product quantity
        warehouse_product = WarehouseProduct.objects.get(
            warehouse=warehouse,
            product=product
        )
        
        # Calculate change in quantity
        if instance.pk:
            try:
                previous = OutflowItems.objects.get(pk=instance.pk)
                quantity_change = instance.quantity - previous.quantity
            except OutflowItems.DoesNotExist:
                quantity_change = instance.quantity
        else:
            quantity_change = instance.quantity
        
        # Check if we have enough quantity
        if warehouse_product.current_quantity < quantity_change:
            raise ValidationError(
                f"Not enough stock for product {product.name}. "
                f"Available: {warehouse_product.current_quantity}, "
                f"Requested: {quantity_change}"
            )
            
    except WarehouseProduct.DoesNotExist:
        # If product doesn't exist in warehouse, we can't fulfill
        raise ValidationError(f"Product {product.name} not available in warehouse {warehouse.name}")

@receiver(post_save, sender=Outflow)
def update_quantities_on_status_change(sender, instance, created, **kwargs):
    """Update quantities when outflow status changes to approved"""
    # Skip on creation
    if created:
        return
        
    # Only process when status changes to approved
    if instance.status == 'approved' and hasattr(instance, '_previous_status') and instance._previous_status != 'approved':
        logger.info(f"Outflow {instance.id} status changed to 'approved'. Updating quantities...")
        
        with transaction.atomic():
            # Process all outflow items
            for item in instance.items.all():
                try:
                    product = item.product
                    warehouse = instance.origin
                    
                    # Get warehouse product
                    warehouse_product = WarehouseProduct.objects.get(
                        warehouse=warehouse,
                        product=product
                    )
                    
                    # Update quantities
                    warehouse_product.current_quantity -= item.quantity
                    product.quantity -= item.quantity
                    
                    # Save changes
                    warehouse_product.save()
                    product.save()
                    
                    #Update instance status to completed
                    instance.status = 'completed'
                    instance.save()
                    
                    logger.info(
                        f"Updated quantities for outflow item {item.id} after approval. "
                        f"Product: {product.name}, "
                        f"New warehouse quantity: {warehouse_product.current_quantity}, "
                        f"New total quantity: {product.quantity}"
                    )
                    
                except Exception as e:
                    logger.error(f"Error updating quantities for outflow item {item.id}: {str(e)}")
                    transaction.set_rollback(True)
                    raise
                    
            # Update warehouse total quantity
            instance.origin.update_total_quantity()

@receiver(post_save, sender=OutflowItems)
def update_quantities_on_outflow_item_change(sender, instance, created, **kwargs):
    """Update quantities when items in completed outflows change"""
    # Only process if outflow is completed
    if instance.outflow.status != 'completed':
        return
    
    # Skip if we're in the middle of an outflow approval
    if hasattr(instance.outflow, '_previous_status') and instance.outflow._previous_status != 'completed':
        return
    
    with transaction.atomic():
        try:
            warehouse = instance.outflow.origin
            product = instance.product
            
            # Get warehouse product
            warehouse_product = WarehouseProduct.objects.get(
                warehouse=warehouse,
                product=product
            )
            
            # Calculate quantity change
            if created:
                quantity_change = instance.quantity
            else:
                quantity_change = instance.quantity - getattr(instance, '_previous_quantity', 0)
            
            # Update quantities
            warehouse_product.current_quantity -= quantity_change
            product.quantity -= quantity_change
            
            # Save changes
            warehouse_product.save()
            product.save()
            
            # Update warehouse total
            warehouse.update_total_quantity()
            
            logger.info(
                f"Updated quantities for outflow item change. "
                f"Product: {product.name}, "
                f"Change: {quantity_change}, "
                f"New warehouse quantity: {warehouse_product.current_quantity}"
            )
            
        except Exception as e:
            logger.error(f"Error updating quantities for outflow item {instance.id}: {str(e)}")
            transaction.set_rollback(True)
            raise

@receiver(post_delete, sender=OutflowItems)
def restore_quantities_on_outflow_delete(sender, instance, **kwargs):
    """Restore quantities when outflow items are deleted"""
    # Only restore quantities if outflow was approved
    if not hasattr(instance, 'outflow') or instance.outflow.status != 'approved':
        return
    
    with transaction.atomic():
        try:
            warehouse = instance.outflow.origin
            product = instance.product
            
            # Get warehouse product
            warehouse_product = WarehouseProduct.objects.get(
                warehouse=warehouse,
                product=product
            )
            
            # Restore quantities
            warehouse_product.current_quantity += instance.quantity
            product.quantity += instance.quantity
            
            # Save changes
            warehouse_product.save()
            product.save()
            
            # Update warehouse total
            warehouse.update_total_quantity()
            
            logger.info(
                f"Restored quantities after outflow item deletion. "
                f"Product: {product.name}, "
                f"Quantity: {instance.quantity}, "
                f"New warehouse quantity: {warehouse_product.current_quantity}"
            )
            
        except Exception as e:
            logger.error(f"Error restoring quantities for deleted outflow item: {str(e)}")
            transaction.set_rollback(True)
            raise
