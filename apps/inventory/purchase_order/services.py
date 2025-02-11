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
    def approve_order(order_id, user):
        """
        Aprova um pedido de compra
        
        Args:
            order_id: ID do pedido de compra
            user: Usuário que está aprovando o pedido
            
        Returns:
            PurchaseOrder: Pedido de compra atualizado
            
        Raises:
            ValidationError: Se o pedido não puder ser aprovado
        """
        with transaction.atomic():
            order = PurchaseOrder.objects.select_for_update().get(pk=order_id)
            
            if order.status != PurchaseOrder.Status.PENDING:
                raise ValidationError("Apenas pedidos pendentes podem ser aprovados")
                
            if not user.has_perm('purchase_order.can_approve_order'):
                raise ValidationError("Usuário não tem permissão para aprovar pedidos")
                
            order.status = PurchaseOrder.Status.APPROVED
            order.approved_by = user
            order.approved_at = timezone.now()
            order.save()
            
            return order
    
    @staticmethod
    def reject_order(order_id, user, reason):
        """
        Rejeita um pedido de compra
        
        Args:
            order_id: ID do pedido de compra
            user: Usuário que está rejeitando o pedido
            reason: Motivo da rejeição
            
        Returns:
            PurchaseOrder: Pedido de compra atualizado
            
        Raises:
            ValidationError: Se o pedido não puder ser rejeitado
        """
        with transaction.atomic():
            order = PurchaseOrder.objects.select_for_update().get(pk=order_id)
            
            if order.status != PurchaseOrder.Status.PENDING:
                raise ValidationError("Apenas pedidos pendentes podem ser rejeitados")
                
            if not user.has_perm('purchase_order.can_reject_order'):
                raise ValidationError("Usuário não tem permissão para rejeitar pedidos")
                
            order.status = PurchaseOrder.Status.REJECTED
            order.rejected_by = user
            order.rejected_at = timezone.now()
            order.rejection_reason = reason
            order.save()
            
            return order
    
    @staticmethod
    def cancel_order(order_id, user, reason):
        """
        Cancela um pedido de compra
        
        Args:
            order_id: ID do pedido de compra
            user: Usuário que está cancelando o pedido
            reason: Motivo do cancelamento
            
        Returns:
            PurchaseOrder: Pedido de compra atualizado
            
        Raises:
            ValidationError: Se o pedido não puder ser cancelado
        """
        with transaction.atomic():
            order = PurchaseOrder.objects.select_for_update().get(pk=order_id)
            
            if order.status not in [PurchaseOrder.Status.PENDING, PurchaseOrder.Status.APPROVED]:
                raise ValidationError("Apenas pedidos pendentes ou aprovados podem ser cancelados")
                
            if not user.has_perm('purchase_order.can_cancel_order'):
                raise ValidationError("Usuário não tem permissão para cancelar pedidos")
                
            order.status = PurchaseOrder.Status.CANCELLED
            order.cancelled_by = user
            order.cancelled_at = timezone.now()
            order.cancellation_reason = reason
            order.save()
            
            return order

class PurchaseOrderItemService:
    """Service for handling purchase order item operations"""
    
    @staticmethod
    def add_item(order_id, product_id, quantity, unit_price, user):
        """
        Adiciona um item ao pedido de compra
        
        Args:
            order_id: ID do pedido de compra
            product_id: ID do produto
            quantity: Quantidade
            unit_price: Preço unitário
            user: Usuário que está adicionando o item
            
        Returns:
            PurchaseOrderItem: Item adicionado
            
        Raises:
            ValidationError: Se o item não puder ser adicionado
        """
        with transaction.atomic():
            order = PurchaseOrder.objects.select_for_update().get(pk=order_id)
            
            if order.status != PurchaseOrder.Status.PENDING:
                raise ValidationError("Itens só podem ser adicionados a pedidos pendentes")
                
            if not user.has_perm('purchase_order.can_add_item'):
                raise ValidationError("Usuário não tem permissão para adicionar itens")
                
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
        Atualiza um item do pedido de compra
        
        Args:
            item_id: ID do item
            quantity: Nova quantidade (opcional)
            unit_price: Novo preço unitário (opcional)
            user: Usuário que está atualizando o item
            
        Returns:
            PurchaseOrderItem: Item atualizado
            
        Raises:
            ValidationError: Se o item não puder ser atualizado
        """
        with transaction.atomic():
            item = PurchaseOrderItem.objects.select_related('purchase_order').get(pk=item_id)
            
            if item.purchase_order.status != PurchaseOrder.Status.PENDING:
                raise ValidationError("Itens só podem ser atualizados em pedidos pendentes")
                
            if not user.has_perm('purchase_order.can_update_item'):
                raise ValidationError("Usuário não tem permissão para atualizar itens")
                
            if quantity is not None:
                item.quantity = quantity
            if unit_price is not None:
                item.unit_price = unit_price
                
            item.save()
            
            return item
    
    @staticmethod
    def remove_item(item_id, user):
        """
        Remove um item do pedido de compra
        
        Args:
            item_id: ID do item
            user: Usuário que está removendo o item
            
        Raises:
            ValidationError: Se o item não puder ser removido
        """
        with transaction.atomic():
            item = PurchaseOrderItem.objects.select_related('purchase_order').get(pk=item_id)
            
            if item.purchase_order.status != PurchaseOrder.Status.PENDING:
                raise ValidationError("Itens só podem ser removidos de pedidos pendentes")
                
            if not user.has_perm('purchase_order.can_remove_item'):
                raise ValidationError("Usuário não tem permissão para remover itens")
                
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
