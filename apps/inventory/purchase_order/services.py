"""
Services for handling purchase order operations.
This module contains business logic for purchase order operations,
particularly focused on change detection.
"""
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
        
        # Verifica se a quantidade mudou
        if old_instance.quantity != new_instance.quantity:
            changes['quantity_changed'] = True
            changes['old_quantity'] = old_instance.quantity
            changes['new_quantity'] = new_instance.quantity
        
        # Verifica se o preço mudou
        if old_instance.unit_price != new_instance.unit_price:
            changes['price_changed'] = True
            changes['old_price'] = old_instance.unit_price
            changes['new_price'] = new_instance.unit_price
        
        return changes
