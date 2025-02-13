import logging
from django.db import models, transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Warehouse, WarehouseProduct

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Warehouse)
def store_previous_warehouse_values(sender, instance, **kwargs):
    """Store previous warehouse values for comparison"""
    if instance.pk:
        try:
            previous = Warehouse.objects.get(pk=instance.pk)
            instance._previous_limit = previous.limit
            instance._previous_quantity = previous.quantity
            logger.debug(f"Warehouse ID {instance.pk}: Previous values stored - Limit: {previous.limit}, Quantity: {previous.quantity}")
        except Warehouse.DoesNotExist:
            instance._previous_limit = 0
            instance._previous_quantity = 0
            logger.debug(f"Warehouse ID {instance.pk}: New record, previous values set to 0")
    else:
        instance._previous_limit = 0
        instance._previous_quantity = 0
        logger.debug("New Warehouse: previous values set to 0")

@receiver(post_save, sender=Warehouse)
def check_warehouse_capacity(sender, instance, **kwargs):
    """Log warning if warehouse is approaching capacity"""
    if instance.limit > 0:  # Only check if a limit is set
        # Warn if approaching capacity (90% or more)
        if instance.quantity >= (instance.limit * 0.9):
            logger.warning(f"Warehouse {instance.name} is at {(instance.quantity/instance.limit)*100:.1f}% capacity")

@receiver(pre_save, sender=WarehouseProduct)
def store_previous_warehouse_product_values(sender, instance, **kwargs):
    """Store previous warehouse product values for comparison"""
    if instance.pk:
        try:
            previous = WarehouseProduct.objects.get(pk=instance.pk)
            instance._previous_quantity = previous.current_quantity
        except WarehouseProduct.DoesNotExist:
            instance._previous_quantity = 0
    else:
        instance._previous_quantity = 0

@receiver(pre_save, sender=WarehouseProduct)
def validate_warehouse_product_capacity(sender, instance, **kwargs):
    """Validate warehouse capacity before saving warehouse product"""
    if not instance.warehouse.limit:  # No limit set
        return
        
    # Calculate total warehouse quantity including this product's change
    total_quantity = (
        WarehouseProduct.objects.filter(warehouse=instance.warehouse)
        .exclude(pk=instance.pk)
        .aggregate(total=models.Sum('current_quantity'))['total'] or 0
    )
    total_quantity += instance.current_quantity
    
    # Check if total would exceed limit
    if total_quantity > instance.warehouse.limit:
        logger.error(f"Operation would exceed warehouse capacity for {instance.warehouse.name}")
        logger.error(f"Current total: {total_quantity}, Limit: {instance.warehouse.limit}")
        raise ValidationError(
            f"Operation would exceed warehouse capacity. "
            f"Total after change: {total_quantity}, "
            f"Limit: {instance.warehouse.limit}"
        )
