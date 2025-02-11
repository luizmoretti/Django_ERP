"""
Purchase Order notification handlers
"""
import logging
from apps.notifications.base import BaseNotificationHandler
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from ..models import PurchaseOrder, PurchaseOrderItem
from ..services import PurchaseOrderItemChangeService
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)
from decimal import Decimal

logger = logging.getLogger(__name__)


class PurchaseOrderNotificationHandler(BaseNotificationHandler):
    """Handler for purchase order notifications."""
    
    @staticmethod
    @receiver(post_save, sender=PurchaseOrder, dispatch_uid='notify_order_created')
    def notify_order_created(sender, instance, created, **kwargs):
        """
        Notifica sobre criação de novo pedido.
        Automaticamente chamado quando um novo PurchaseOrder é criado.
        """
        if not created:  # Se não é uma nova ordem, ignora
            return
            
        def send_notification():
            try:
                # Recarrega a ordem para ter certeza que temos os dados mais recentes
                order = PurchaseOrder.objects.get(pk=instance.pk)
                
                handler = PurchaseOrderNotificationHandler()
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ORDER'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'supplier': order.supplier.name,
                    'total': float(order.total)
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ORDER_CREATED']] % {
                    'order_number': order.order_number,
                    'supplier': order.supplier.name,
                    'total': float(order.total)
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ORDER_CREATED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
                    
            except Exception as e:
                logger.error(f"Error sending order created notification: {str(e)}")
                raise
        
        # Agenda o envio da notificação para depois que a transação for commitada
        from django.db import transaction
        transaction.on_commit(send_notification)
    
    @staticmethod
    @receiver(post_save, sender=PurchaseOrder, dispatch_uid='notify_order_updated')
    def notify_order_updated(sender, instance, created, **kwargs):
        """
        Notifica sobre atualização de pedido de compra.
        Automaticamente chamado quando um PurchaseOrder é atualizado.
        """
        if created:
            return
            
        try:
            # Verifica se houve mudança em algum campo além do total
            old_instance = sender.objects.get(pk=instance.pk)
            if (old_instance.supplier_id == instance.supplier_id and 
                old_instance.status == instance.status and
                old_instance.expected_delivery == instance.expected_delivery and
                old_instance.notes == instance.notes and
                old_instance.total == instance.total):
                return
            
            # Se apenas o total mudou, não notifica (pois já foi notificado na mudança do item)
            if (old_instance.supplier_id == instance.supplier_id and 
                old_instance.status == instance.status and
                old_instance.expected_delivery == instance.expected_delivery and
                old_instance.notes == instance.notes):
                return
            
            handler = PurchaseOrderNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ORDER'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'order_id': str(instance.id),
                'order_number': instance.order_number,
                'supplier': instance.supplier.name,
                'total': float(instance.total)
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ORDER_UPDATED']] % {
                'order_number': instance.order_number,
                'total': float(instance.total)
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ORDER_UPDATED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending order update notification: {str(e)}")
            raise
    
    @staticmethod
    @receiver(pre_save, sender=PurchaseOrder, dispatch_uid='notify_order_status_changed')
    def notify_order_status_changed(sender, instance, **kwargs):
        """
        Notifica sobre mudança de status do pedido.
        Automaticamente chamado antes de salvar um PurchaseOrder.
        """
        if not instance.pk:
            return
            
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status == instance.status:
                return
            
            handler = PurchaseOrderNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ORDER'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['INFO'],
                'order_id': str(instance.id),
                'order_number': instance.order_number,
                'supplier': instance.supplier.name,
                'old_status': old_instance.status,
                'new_status': instance.status
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ORDER_STATUS_CHANGED']] % {
                'order_number': instance.order_number,
                'old_status': old_instance.status,
                'new_status': instance.status
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ORDER_STATUS_CHANGED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['INFO'],
                data=data
            )
                
        except sender.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error sending order status change notification: {str(e)}")
            raise
    
    @staticmethod
    @receiver(post_save, sender=PurchaseOrderItem, dispatch_uid='notify_item_added')
    def notify_item_added(sender, instance, created, **kwargs):
        """
        Notifica quando um novo item é adicionado a um pedido existente.
        Automaticamente chamado quando um PurchaseOrderItem é criado.
        """
        if not created:  # Se não é um novo item, ignora
            return
            
        # Verifica se a ordem foi criada há mais de 1 segundo
        # Isso indica que é uma ordem existente, não uma nova ordem sendo criada com seus itens
        if (instance.purchase_order.created_at - instance.created_at).total_seconds() > 1:
            try:
                handler = PurchaseOrderNotificationHandler()
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ITEM'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(instance.purchase_order.id),
                    'order_number': instance.purchase_order.order_number,
                    'supplier': instance.purchase_order.supplier.name,
                    'product': instance.product.name,
                    'quantity': instance.quantity,
                    'total': float(instance.purchase_order.total)
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_ADDED']] % {
                    'product': instance.product.name,
                    'order_number': instance.purchase_order.order_number,
                    'quantity': instance.quantity,
                    'total': float(instance.purchase_order.total)
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_ADDED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
                
            except Exception as e:
                logger.error(f"Error handling item added notification: {str(e)}")
                raise
    
    @staticmethod
    @receiver(pre_save, sender=PurchaseOrderItem, dispatch_uid='notify_item_changes')
    def notify_item_changes(sender, instance, **kwargs):
        """
        Notifica sobre mudanças em quantidade e preço do item.
        Automaticamente chamado antes de salvar um PurchaseOrderItem.
        """
        if not instance.pk:  # Se é um novo item, não verifica mudanças
            return
            
        try:
            handler = PurchaseOrderNotificationHandler()
            old_instance = sender.objects.get(pk=instance.pk)
            changes = PurchaseOrderItemChangeService.check_changes(instance, old_instance)
            
            if not (changes['quantity_changed'] or changes['price_changed']):
                return
            
            # Calcula o novo total do pedido
            order = instance.purchase_order
            new_total = 0
            for item in order.items.all():
                if item.pk == instance.pk:
                    # Para o item sendo atualizado, usa os novos valores
                    new_total += Decimal(str(instance.unit_price)) * Decimal(str(instance.quantity))
                else:
                    # Para os outros itens, usa os valores atuais
                    new_total += item.calculate_total()
            
            # Notifica mudança de quantidade
            if changes['quantity_changed']:
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ITEM'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(instance.purchase_order.id),
                    'order_number': instance.purchase_order.order_number,
                    'supplier': instance.purchase_order.supplier.name,
                    'product': instance.product.name,
                    'old_quantity': changes['old_quantity'],
                    'new_quantity': changes['new_quantity'],
                    'total': float(new_total)  # Usa o novo total calculado
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_QUANTITY_CHANGED']] % {
                    'product': instance.product.name,
                    'order_number': instance.purchase_order.order_number,
                    'old_quantity': changes['old_quantity'],
                    'new_quantity': changes['new_quantity'],
                    'total': float(new_total)  # Usa o novo total calculado
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_QUANTITY_CHANGED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
            
            # Notifica mudança de preço
            if changes['price_changed']:
                recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['PRICE'])
                recipient_ids = [str(user.id) for user in recipients]
                
                data = {
                    'type': SEVERITY_TYPES['INFO'],
                    'order_id': str(instance.purchase_order.id),
                    'order_number': instance.purchase_order.order_number,
                    'supplier': instance.purchase_order.supplier.name,
                    'product': instance.product.name,
                    'old_price': float(changes['old_price']),
                    'new_price': float(changes['new_price']),
                    'total': float(new_total)  # Usa o novo total calculado
                }
                
                message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_PRICE_CHANGED']] % {
                    'product': instance.product.name,
                    'order_number': instance.purchase_order.order_number,
                    'old_price': float(changes['old_price']),
                    'new_price': float(changes['new_price']),
                    'total': float(new_total)  # Usa o novo total calculado
                }
                
                handler.send_to_recipients(
                    recipient_ids=recipient_ids,
                    title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_PRICE_CHANGED']],
                    message=message,
                    app_name=APP_NAME,
                    notification_type=SEVERITY_TYPES['INFO'],
                    data=data
                )
                
        except sender.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error handling item changes notification: {str(e)}")
            raise
    
    @staticmethod
    @receiver(post_delete, sender=PurchaseOrderItem, dispatch_uid='notify_item_deleted')
    def notify_item_deleted(sender, instance, **kwargs):
        """
        Notifica sobre remoção de item do pedido.
        Automaticamente chamado quando um PurchaseOrderItem é deletado.
        """
        try:
            handler = PurchaseOrderNotificationHandler()
            recipients = handler.get_recipients_by_type(*RECIPIENT_TYPES['ITEM'])
            recipient_ids = [str(user.id) for user in recipients]
            
            data = {
                'type': SEVERITY_TYPES['WARNING'],
                'order_id': str(instance.purchase_order.id),
                'order_number': instance.purchase_order.order_number,
                'supplier': instance.purchase_order.supplier.name,
                'product': instance.product.name
            }
            
            message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['ITEM_DELETED']] % {
                'product': instance.product.name,
                'order_number': instance.purchase_order.order_number
            }
            
            handler.send_to_recipients(
                recipient_ids=recipient_ids,
                title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['ITEM_DELETED']],
                message=message,
                app_name=APP_NAME,
                notification_type=SEVERITY_TYPES['WARNING'],
                data=data
            )
                
        except Exception as e:
            logger.error(f"Error sending item deletion notification: {str(e)}")
            raise