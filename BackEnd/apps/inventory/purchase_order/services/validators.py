"""
Validators for purchase order operations.
This module contains validation logic for purchase order operations.
"""
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Sum
from ..models import PurchaseOrder, PurchaseOrderItem
from apps.inventory.supplier.models import Supplier
from apps.inventory.product.models import Product
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderValidator:
    """Validator for purchase order operations"""
    
    @staticmethod
    def validate_purchase_order_data(data: dict) -> None:
        """
        Validates purchase order data
        
        Args:
            data: Dictionary containing purchase order data
            
        Raises:
            ValidationError: If the data is invalid
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating purchase order data: {data}")
        
        # Check required fields
        required_fields = ['supplier', 'expected_delivery', 'status']
        for field in required_fields:
            if field not in data:
                logger.error(f"[PURCHASE ORDER VALIDATOR] Missing required field: {field}")
                raise ValidationError({field: _(f"This field is required")})
        
        # Validate supplier exists
        try:
            supplier_id = data['supplier']
            if not Supplier.objects.filter(id=supplier_id).exists():
                logger.error(f"[PURCHASE ORDER VALIDATOR] Supplier does not exist: {supplier_id}")
                raise ValidationError({'supplier': _("Supplier does not exist")})
        except Exception as e:
            logger.error(f"[PURCHASE ORDER VALIDATOR] Error validating supplier: {str(e)}")
            raise ValidationError({'supplier': _("Invalid supplier")})
        
        # Validate status
        valid_statuses = ['draft', 'pending', 'approved', 'rejected', 'cancelled']
        if data['status'] not in valid_statuses:
            logger.error(f"[PURCHASE ORDER VALIDATOR] Invalid status: {data['status']}")
            raise ValidationError({'status': _(f"Status must be one of: {', '.join(valid_statuses)}")})
        
        # Validate items data
        if 'items_data' not in data or not data['items_data']:
            logger.error("[PURCHASE ORDER VALIDATOR] No items data provided")
            raise ValidationError({'items_data': _("At least one item is required")})
        
        # Validate each item
        for i, item_data in enumerate(data['items_data']):
            try:
                PurchaseOrderValidator.validate_purchase_order_item_data(item_data, i)
            except ValidationError as e:
                logger.error(f"[PURCHASE ORDER VALIDATOR] Error validating item {i}: {str(e)}")
                raise
    
    @staticmethod
    def validate_purchase_order_item_data(data: dict, index: int = 0) -> None:
        """
        Validates purchase order item data
        
        Args:
            data: Dictionary containing purchase order item data
            index: Index of the item in the items list (for error reporting)
            
        Raises:
            ValidationError: If the data is invalid
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating purchase order item data: {data}")
        
        # Check required fields
        required_fields = ['product', 'quantity', 'unit_price']
        for field in required_fields:
            if field not in data:
                logger.error(f"[PURCHASE ORDER VALIDATOR] Missing required field in item {index}: {field}")
                raise ValidationError({f'items_data[{index}].{field}': _(f"This field is required")})
        
        # Validate product exists
        try:
            product_id = data['product']
            if not Product.objects.filter(id=product_id).exists():
                logger.error(f"[PURCHASE ORDER VALIDATOR] Product does not exist: {product_id}")
                raise ValidationError({f'items_data[{index}].product': _("Product does not exist")})
        except Exception as e:
            logger.error(f"[PURCHASE ORDER VALIDATOR] Error validating product: {str(e)}")
            raise ValidationError({f'items_data[{index}].product': _("Invalid product")})
        
        # Validate quantity
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                logger.error(f"[PURCHASE ORDER VALIDATOR] Invalid quantity: {quantity}")
                raise ValidationError({f'items_data[{index}].quantity': _("Quantity must be greater than zero")})
        except (ValueError, TypeError):
            logger.error(f"[PURCHASE ORDER VALIDATOR] Invalid quantity type: {data['quantity']}")
            raise ValidationError({f'items_data[{index}].quantity': _("Quantity must be a number")})
        
        # Validate unit price
        try:
            unit_price = Decimal(data['unit_price'])
            if unit_price <= 0:
                logger.error(f"[PURCHASE ORDER VALIDATOR] Invalid unit price: {unit_price}")
                raise ValidationError({f'items_data[{index}].unit_price': _("Unit price must be greater than zero")})
        except (ValueError, TypeError, InvalidOperation):
            logger.error(f"[PURCHASE ORDER VALIDATOR] Invalid unit price type: {data['unit_price']}")
            raise ValidationError({f'items_data[{index}].unit_price': _("Unit price must be a number")})
    
    @staticmethod
    def validate_status_transition(order: PurchaseOrder, new_status: str, user) -> None:
        """
        Validates if a status transition is allowed
        
        Args:
            order: Purchase order
            new_status: New status
            user: User performing the transition
            
        Raises:
            ValidationError: If the transition is not allowed
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating status transition: {order.status} -> {new_status}")
        
        # Define allowed transitions
        allowed_transitions = {
            'draft': ['pending', 'cancelled'],
            'pending': ['approved', 'rejected', 'cancelled'],
            'approved': ['cancelled'],
            'rejected': [],
            'cancelled': []
        }
        
        # Check if transition is allowed
        if new_status not in allowed_transitions.get(order.status, []):
            logger.error(f"[PURCHASE ORDER VALIDATOR] Invalid status transition: {order.status} -> {new_status}")
            raise ValidationError(_("Invalid status transition"))
        
        # Check permissions based on transition
        permission_map = {
            'approved': 'purchase_order.can_approve_order',
            'rejected': 'purchase_order.can_reject_order',
            'cancelled': 'purchase_order.can_cancel_order'
        }
        
        if new_status in permission_map and not user.has_perm(permission_map[new_status]):
            logger.error(f"[PURCHASE ORDER VALIDATOR] User does not have permission for status transition: {new_status}")
            raise ValidationError(_("You do not have permission to perform this action"))
    
    @staticmethod
    def validate_order_has_items(order_id) -> None:
        """
        Validates that a purchase order has at least one item
        
        Args:
            order_id: ID of the purchase order
            
        Raises:
            ValidationError: If the order has no items
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating order has items: {order_id}")
        
        items_count = PurchaseOrderItem.objects.filter(purchase_order_id=order_id).count()
        if items_count == 0:
            logger.error(f"[PURCHASE ORDER VALIDATOR] Order has no items: {order_id}")
            raise ValidationError(_("Purchase order must have at least one item"))
    
    @staticmethod
    def validate_can_modify_order(order: PurchaseOrder) -> None:
        """
        Validates if an order can be modified
        
        Args:
            order: Purchase order
            
        Raises:
            ValidationError: If the order cannot be modified
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating order can be modified: {order.id}")
        
        if order.status not in ['draft', 'pending']:
            logger.error(f"[PURCHASE ORDER VALIDATOR] Cannot modify order with status: {order.status}")
            raise ValidationError(_("Only draft or pending orders can be modified"))
    
    @staticmethod
    def validate_can_add_item(order: PurchaseOrder) -> None:
        """
        Validates if an item can be added to an order
        
        Args:
            order: Purchase order
            
        Raises:
            ValidationError: If an item cannot be added
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating can add item to order: {order.id}")
        
        PurchaseOrderValidator.validate_can_modify_order(order)
    
    @staticmethod
    def validate_can_update_item(item: PurchaseOrderItem) -> None:
        """
        Validates if an item can be updated
        
        Args:
            item: Purchase order item
            
        Raises:
            ValidationError: If the item cannot be updated
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating can update item: {item.id}")
        
        PurchaseOrderValidator.validate_can_modify_order(item.purchase_order)
    
    @staticmethod
    def validate_can_remove_item(item: PurchaseOrderItem) -> None:
        """
        Validates if an item can be removed
        
        Args:
            item: Purchase order item
            
        Raises:
            ValidationError: If the item cannot be removed
        """
        logger.debug(f"[PURCHASE ORDER VALIDATOR] Validating can remove item: {item.id}")
        
        PurchaseOrderValidator.validate_can_modify_order(item.purchase_order)
        
        # Check if this is the last item
        items_count = PurchaseOrderItem.objects.filter(purchase_order=item.purchase_order).count()
        if items_count <= 1:
            logger.error(f"[PURCHASE ORDER VALIDATOR] Cannot remove last item from order: {item.purchase_order.id}")
            raise ValidationError(_("Cannot remove the last item from a purchase order"))