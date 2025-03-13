import logging
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import Inflow, InflowItems
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

@receiver(pre_save, sender=Inflow)
def store_previous_inflow_status(sender, instance, **kwargs):
    """Store previous inflow status before changes"""
    if instance.pk:
        try:
            previous = Inflow.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
            logger.info(f"Inflow ID {instance.pk}: Previous status stored: {previous.status}")
        except Inflow.DoesNotExist:
            instance._previous_status = None
            logger.info(f"Inflow ID {instance.pk}: New record, no previous status")
    else:
        instance._previous_status = None
        logger.info("New Inflow: no previous status")

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

# @receiver(post_save, sender=InflowItems)
# def update_quantities_on_inflow(sender, instance, created, **kwargs):
#     """Update quantities after successful validation, but only if inflow is approved"""
#     # Verificar se o inflow está aprovado
#     if instance.inflow.status != 'approved':
#         logger.info(
#             f"Skipping quantity update for inflow item {instance.id} because inflow status is '{instance.inflow.status}'"
#         )
#         return
    
#     with transaction.atomic():
#         product = instance.product
#         warehouse = instance.inflow.destiny
        
#         if not product or not warehouse:
#             logger.warning(f"InflowItems ID {instance.id} has no associated product or warehouse.")
#             return
        
#         try:
#             # Get or create WarehouseProduct
#             warehouse_product, wp_created = WarehouseProduct.objects.get_or_create(
#                 warehouse=warehouse,
#                 product=product,
#                 defaults={'current_quantity': 0}
#             )
            
#             if created:
#                 # New inflow
#                 quantity_change = instance.quantity
#             else:
#                 # Update - calculate difference
#                 quantity_change = instance.quantity - getattr(instance, '_previous_quantity', 0)
            
#             # Update WarehouseProduct quantity
#             warehouse_product.current_quantity += quantity_change
#             warehouse_product.save()
            
#             # Update Product quantity
#             product.quantity += quantity_change
#             product.save()
            
#             # Update Warehouse total quantity
#             warehouse.quantity = warehouse.get_total_quantity()
#             warehouse.save()
            
            
#             #Change inflow status to completed
#             instance.inflow.status = 'completed'
#             instance.inflow.save()
            
#             logger.info(
#                 f"Updated quantities for inflow item {instance.id}. "
#                 f"Product: {product.name}, New quantity: {product.quantity}, "
#                 f"Warehouse product quantity: {warehouse_product.current_quantity}, "
#                 f"Total warehouse quantity: {warehouse.quantity}"
#             )
            
#         except Exception as e:
#             logger.error(f"Error updating quantities for inflow item {instance.id}: {str(e)}")
#             transaction.set_rollback(True)
#             raise



@receiver(post_save, sender=Inflow)
def update_quantities_on_inflow_status_change(sender, instance, created, **kwargs):
    """
    Update quantities when inflow status changes to approved
    This signal handles the case when an existing inflow is approved
    """
    # Ignorar se é uma criação (será tratado pelos signals de InflowItems)
    if created:
        return
        
    # Verificar se o status é 'approved' e se houve mudança de status
    if instance.status == 'approved' and hasattr(instance, '_previous_status') and instance._previous_status != 'approved':
        logger.info(f"Inflow {instance.id} status changed to 'approved'. Updating quantities...")
        
        with transaction.atomic():
            # Processar todos os itens do inflow
            for item in instance.items.all():
                try:
                    product = item.product
                    warehouse = instance.destiny
                    
                    if not product or not warehouse:
                        logger.warning(f"InflowItems ID {item.id} has no associated product or warehouse.")
                        continue
                    
                    # Get or create WarehouseProduct
                    warehouse_product, wp_created = WarehouseProduct.objects.get_or_create(
                        warehouse=warehouse,
                        product=product,
                        defaults={'current_quantity': 0}
                    )
                    
                    # Update WarehouseProduct quantity
                    previous_quantity = warehouse_product.current_quantity
                    warehouse_product.current_quantity += item.quantity
                    warehouse_product.save()
                    
                    # Update Product quantity
                    product_previous_quantity = product.quantity
                    product.quantity += item.quantity
                    product.save()
                    
                    #Change inflow status to completed
                    instance.status = 'completed'
                    instance.save()
                    logger.info(f"Inflow {instance.id} status changed to {instance.status} successfully")
                    
                    logger.info(
                        f"Updated quantities for inflow item {item.id} after approval. "
                        f"Product: {product.name}, "
                        f"Previous quantity: {product_previous_quantity}, "
                        f"New quantity: {product.quantity}, "
                        f"Warehouse product previous quantity: {previous_quantity}, "
                        f"Warehouse product new quantity: {warehouse_product.current_quantity}"
                    )
                    
                except Exception as e:
                    logger.error(f"Error updating quantities for inflow item {item.id} after approval: {str(e)}")
                    transaction.set_rollback(True)
                    raise
            
            # Update warehouse total quantity
            if instance.destiny:
                instance.destiny.update_total_quantity()
                logger.info(f"Updated total quantity for warehouse {instance.destiny.id}")


# Modificar o signal existente para evitar duplicação
@receiver(post_save, sender=InflowItems)
def update_quantities_on_inflow_item_change(sender, instance, created, **kwargs):
    """
    Update quantities when inflow items are created or modified
    This only applies to items in already approved inflows or when adding items to approved inflows
    """
    # Verificar se o inflow está aprovado
    if instance.inflow.status != 'approved':
        logger.info(
            f"Skipping quantity update for inflow item {instance.id} because inflow status is '{instance.inflow.status}'"
        )
        return
    
    # Verificar se estamos no meio de uma aprovação de inflow
    # Se sim, a atualização será tratada pelo signal update_quantities_on_inflow_status_change
    if hasattr(instance.inflow, '_previous_status') and instance.inflow._previous_status != 'approved':
        logger.info(
            f"Skipping quantity update for inflow item {instance.id} because it's part of an inflow being approved"
        )
        return
    
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
                # New inflow item
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
                f"Updated quantities for inflow item {instance.id} (direct change). "
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
    """Subtract quantities when inflow is deleted, but only if inflow was completed"""
    
    # Verify if inflow was completed
    if not hasattr(instance, 'inflow') or instance.inflow.status != 'completed':
        logger.info(
            f"Skipping quantity subtraction for deleted inflow item {instance.id} because inflow status is not 'completed'"
        )
        return
    
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