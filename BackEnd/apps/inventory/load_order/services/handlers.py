from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from ..models import LoadOrder, LoadOrderItem
from apps.inventory.product.models import Product
from apps.companies.customers.models import Customer
from apps.deliveries.vehicles.models import Vehicle
from .validators import LoadOrderValidator
import logging

logger = logging.getLogger(__name__)

class LoadOrderHandler:
    """Handler for load order operations"""
    
    @staticmethod
    @transaction.atomic
    def create_load_order(data: dict, created_by) -> LoadOrder:
        """Create a new load order with items"""
        try:
            # Validate data
            LoadOrderValidator.validate_load_order_data(data)
            
            # Get related objects
            customer = Customer.objects.get(id=data['customer'])
            vehicle = Vehicle.objects.get(id=data['load_to'])
            
            # Create load order
            load_order = LoadOrder(
                customer=customer,
                load_to=vehicle,
                load_date=data['load_date'],
                created_by=created_by,
                updated_by=created_by,
                companie=created_by.companie
            )
            load_order.save()
            
            # Create items
            for item_data in data['items_data']:
                product = Product.objects.get(id=item_data['product'])
                LoadOrderItem.objects.create(
                    load_order=load_order,
                    product=product,
                    quantity=item_data['quantity'],
                    created_by=created_by,
                    updated_by=created_by,
                    companie=created_by.companie
                )
            
            logger.info(f"[LOAD ORDER HANDLER] Created load order {load_order.order_number}")
            return load_order
            
        except ValidationError as e:
            logger.error(f"[LOAD ORDER HANDLER] Validation error creating load order: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[LOAD ORDER HANDLER] Error creating load order: {str(e)}")
            raise ValidationError(_("Error creating load order"))
    
    @staticmethod
    @transaction.atomic
    def update_load_order(load_order: LoadOrder, data: dict, updated_by) -> LoadOrder:
        """Update an existing load order"""
        try:
            # Validate data
            LoadOrderValidator.validate_load_order_data(data)
            
            # Update related objects if provided
            if 'customer' in data:
                load_order.customer = Customer.objects.get(id=data['customer'])
            if 'load_to' in data:
                load_order.load_to = Vehicle.objects.get(id=data['load_to'])
            if 'load_date' in data:
                load_order.load_date = data['load_date']
            
            load_order.updated_by = updated_by
            load_order.save()
            
            # Update items if provided
            if 'items_data' in data:
                # Delete existing items
                load_order.items.all().delete()
                
                # Create new items
                for item_data in data['items_data']:
                    product = Product.objects.get(id=item_data['product'])
                    LoadOrderItem.objects.create(
                        load_order=load_order,
                        product=product,
                        quantity=item_data['quantity'],
                        created_by=updated_by,
                        updated_by=updated_by,
                        companie=updated_by.companie
                    )
            
            logger.info(f"[LOAD ORDER HANDLER] Updated load order {load_order.order_number}")
            return load_order
            
        except ValidationError as e:
            logger.error(f"[LOAD ORDER HANDLER] Validation error updating load order: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[LOAD ORDER HANDLER] Error updating load order: {str(e)}")
            raise ValidationError(_("Error updating load order"))
    
    @staticmethod
    @transaction.atomic
    def delete_load_order(load_order: LoadOrder) -> None:
        """Delete a load order and its items"""
        try:
            order_number = load_order.order_number
            load_order.delete()
            logger.info(f"[LOAD ORDER HANDLER] Deleted load order {order_number}")
            
        except Exception as e:
            logger.error(f"[LOAD ORDER HANDLER] Error deleting load order: {str(e)}")
            raise ValidationError(_("Error deleting load order"))