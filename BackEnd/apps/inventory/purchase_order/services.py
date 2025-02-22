"""
Services for handling purchase order operations.
This module contains business logic for purchase order operations.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import PurchaseOrder, PurchaseOrderItem

class PurchaseOrderService:
    """Service for handling purchase order operations"""
    
    @staticmethod
    def approve_order(order, user):
        """
        Approves a purchase order
        
        Args:
            order: Purchase order to be approved
            user: User who is approving the order
            
        Returns:
            PurchaseOrder: Updated purchase order
            
        Raises:
            ValidationError: If the order cannot be approved
        """
        with transaction.atomic():
            if order.status != 'pending':
                raise ValidationError("Only pending orders can be approved")
                
            if not user.has_perm('purchase_order.can_approve_order'):
                raise ValidationError("User does not have permission to approve orders")
                
            order.status = 'approved'
            order.updated_by = user.employeer
            order.save()
            
            return order
    
    @staticmethod
    def reject_order(order_id, user, reason):
        """
        Rejects a purchase order
        
        Args:
            order_id: ID of the purchase order
            user: User who is rejecting the order
            reason: Reason for rejection
            
        Returns:
            PurchaseOrder: Updated purchase order
            
        Raises:
            ValidationError: If the order cannot be rejected
        """
        with transaction.atomic():
            order = PurchaseOrder.objects.select_for_update().get(pk=order_id)
            
            if order.status != 'pending':
                raise ValidationError("Only pending orders can be rejected")
                
            if not user.has_perm('purchase_order.can_reject_order'):
                raise ValidationError("User does not have permission to reject orders")
                
            order.status = 'rejected'
            order.updated_by = user.employeer
            order.notes = reason
            order.save()
            
            return order
    
    @staticmethod
    def cancel_order(order_id, user, reason):
        """
        Cancels a purchase order
        
        Args:
            order_id: ID of the purchase order
            user: User who is cancelling the order
            reason: Reason for cancellation
            
        Returns:
            PurchaseOrder: Updated purchase order
            
        Raises:
            ValidationError: If the order cannot be cancelled
        """
        with transaction.atomic():
            order = PurchaseOrder.objects.select_for_update().get(pk=order_id)
            
            if order.status not in ['pending', 'approved']:
                raise ValidationError("Only pending or approved orders can be cancelled")
                
            if not user.has_perm('purchase_order.can_cancel_order'):
                raise ValidationError("User does not have permission to cancel orders")
                
            order.status = 'cancelled'
            order.cancelled_by = user.employeer
            order.cancelled_at = timezone.now()
            order.cancellation_reason = reason
            order.save()
            
            return order

class PurchaseOrderItemService:
    """Service for handling purchase order item operations"""
    
    @staticmethod
    def add_item(order_id, product_id, quantity, unit_price, user):
        """
        Adds an item to the purchase order
        
        Args:
            order_id: ID of the purchase order
            product_id: ID of the product
            quantity: Quantity
            unit_price: Unit price
            user: User who is adding the item
            
        Returns:
            PurchaseOrderItem: Added item
            
        Raises:
            ValidationError: If the item cannot be added
        """
        with transaction.atomic():
            order = PurchaseOrder.objects.select_for_update().get(pk=order_id)
            
            if order.status != 'pending':
                raise ValidationError("Items can only be added to pending orders")
                
            if not user.has_perm('purchase_order.can_add_item'):
                raise ValidationError("User does not have permission to add items")
                
            item = PurchaseOrderItem(
                purchase_order=order,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price
            )
            item.save()
            
            return item
    
    @staticmethod
    def update_item(item_id, quantity=None, unit_price=None, user=None):
        """
        Updates a purchase order item
        
        Args:
            item_id: ID of the item
            quantity: New quantity (optional)
            unit_price: New unit price (optional)
            user: User who is updating the item
            
        Returns:
            PurchaseOrderItem: Updated item
            
        Raises:
            ValidationError: If the item cannot be updated
        """
        with transaction.atomic():
            item = PurchaseOrderItem.objects.select_related('purchase_order').get(pk=item_id)
            
            if item.purchase_order.status != 'pending':
                raise ValidationError("Items can only be updated in pending orders")
                
            if not user.has_perm('purchase_order.can_update_item'):
                raise ValidationError("User does not have permission to update items")
                
            if quantity is not None:
                item.quantity = quantity
            if unit_price is not None:
                item.unit_price = unit_price
                
            item.save()
            
            return item
    
    @staticmethod
    def remove_item(item_id, user):
        """
        Removes a purchase order item
        
        Args:
            item_id: ID of the item
            user: User who is removing the item
            
        Raises:
            ValidationError: If the item cannot be removed
        """
        with transaction.atomic():
            item = PurchaseOrderItem.objects.select_related('purchase_order').get(pk=item_id)
            
            if item.purchase_order.status != 'pending':
                raise ValidationError("Items can only be removed from pending orders")
                
            if not user.has_perm('purchase_order.can_remove_item'):
                raise ValidationError("User does not have permission to remove items")
                
            item.delete()

class PurchaseOrderItemChangeService:
    """Service for handling changes in purchase order items"""
    
    @staticmethod
    def check_changes(new_instance, old_instance):
        """
        Check for changes in quantity or price and return the changes detected
        
        Args:
            new_instance: The new PurchaseOrderItem instance being saved
            old_instance: The existing PurchaseOrderItem instance from the database
            
        Returns:
            dict: Dictionary containing the changes detected:
                {
                    'quantity_changed': bool,
                    'price_changed': bool,
                    'old_quantity': int (if quantity changed),
                    'new_quantity': int (if quantity changed),
                    'old_price': decimal (if price changed),
                    'new_price': decimal (if price changed)
                }
        """
        changes = {
            'quantity_changed': False,
            'price_changed': False
        }
        
        # Check if the quantity has changed
        if old_instance.quantity != new_instance.quantity:
            changes['quantity_changed'] = True
            changes['old_quantity'] = old_instance.quantity
            changes['new_quantity'] = new_instance.quantity
        
        # Check if the price has changed
        if old_instance.unit_price != new_instance.unit_price:
            changes['price_changed'] = True
            changes['old_price'] = old_instance.unit_price
            changes['new_price'] = new_instance.unit_price
        
        return changes
