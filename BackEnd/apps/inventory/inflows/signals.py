import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import Inflow, InflowItems
from apps.inventory.movements.models import Movement, MovementType, MovementStatus
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



@receiver(post_save, sender=InflowItems)
def update_movement_on_items_change(sender, instance, created, **kwargs):
    """Update movement record when inflow items change"""
    # Avoid duplicate signal calls and check for valid inflow
    if not instance.inflow_id or not instance.inflow.id:
        return
        
    # Use transaction.on_commit to ensure data consistency and avoid duplicate calls
    def _update_movement():
        # Create new transaction for the update
        with transaction.atomic():
            try:
                # Get inflow and lock it for update to prevent race conditions
                inflow = instance.inflow.__class__.objects.select_for_update().get(id=instance.inflow.id)
                
                # Calculate totals using fresh data with select_related to minimize queries
                items = inflow.items.all().select_related('product')
                total_items = sum(item.quantity for item in items)
                
                # Calculate total value safely handling products without prices
                total_value = 0
                items_data = []
                
                for item in items:
                    logger.info(
                        f"[SIGNALS - INFLOWS]Calculating price for product {item.product.id} "
                        f"(quantity: {item.quantity}) from supplier {inflow.origin.id if inflow.origin else 'None'}"
                    )
                    
                    # Get current price for better performance
                    current_price = item.product.supplier_prices.filter(
                        is_current=True,
                        supplier=inflow.origin
                    ).first()
                    
                    if current_price:
                        item_total = item.quantity * current_price.unit_price
                        total_value += item_total
                        logger.info(
                            f"[SIGNALS - INFLOWS]Found price {current_price.unit_price} for product {item.product.id}. "
                            f"Item total: {item_total}"
                        )
                    else:
                        logger.warning(
                            f"[SIGNALS - INFLOWS]No current price found for product {item.product.id} "
                            f"from supplier {inflow.origin.id if inflow.origin else 'None'}. "
                            f"Supplier prices count: {item.product.supplier_prices.count()}"
                        )
                    
                    items_data.append({
                        'product': item.product.name,
                        'quantity': item.quantity,
                        'unit_price': str(current_price.unit_price if current_price else 0)
                    })
                
                logger.info(f"[SIGNALS - INFLOWS]Final total_value calculated: {total_value}")
                
                # Get or create movement with lock
                movement, m_created = Movement.objects.select_for_update().get_or_create(
                    type=MovementType.INFLOW.value,
                    origin=inflow.origin.name if inflow.origin else None,
                    destination=inflow.destiny.name if inflow.destiny else None,
                    defaults={
                        'companie': inflow.companie,
                        'status': MovementStatus.PENDING.value,
                        'total_items': total_items,
                        'total_value': total_value,
                        'created_by': inflow.created_by,
                        'updated_by': inflow.updated_by,
                        'data': {
                            'inflow_id': str(inflow.id),
                            'items': items_data
                        }
                    }
                )
                
                # Update movement if not created
                if not m_created:
                    movement.status = MovementStatus.PENDING.value
                    movement.total_items = total_items
                    movement.total_value = total_value
                    movement.updated_by = inflow.updated_by
                    movement.data = {
                        'inflow_id': str(inflow.id),
                        'items': items_data
                    }
                    movement.save()
                
                logger.info(f"[SIGNALS - INFLOWS]{'Created' if m_created else 'Updated'} movement record for inflow {inflow.id}")
                
            except Exception as e:
                logger.error(f"[SIGNALS - INFLOWS]Error updating movement record for inflow item {instance.id}: {str(e)}")
                raise
    
    # Execute update after transaction commit
    transaction.on_commit(_update_movement)

@receiver(post_delete, sender=InflowItems)
def update_movement_on_items_delete(sender, instance, **kwargs):
    """Update movement record when inflow items are deleted"""
    try:
        # Try to update movement if inflow still exists
        if instance.inflow_id:
            update_movement_on_items_change(sender, instance, False)
    except Exception as e:
        logger.error(f"[SIGNALS - INFLOWS]Error updating movement after item deletion: {str(e)}")