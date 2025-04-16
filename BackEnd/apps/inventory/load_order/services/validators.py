from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from apps.inventory.product.models import Product
from apps.companies.customers.models import Customer
from apps.deliveries.vehicles.models import Vehicle
from datetime import date
import logging

logger = logging.getLogger(__name__)

class LoadOrderValidator:
    """Validator for load order operations"""
    
    @staticmethod
    def validate_load_order_data(data: dict) -> None:
        """Validate load order data"""
        try:
            # Required fields
            required_fields = ['load_to', 'customer', 'items_data']
            for field in required_fields:
                if field not in data:
                    raise ValidationError(_(f"{field} is required"))
            
            # Validate customer
            if not Customer.objects.filter(id=data['customer']).exists():
                raise ValidationError(_("Invalid customer"))
                
            # Validate vehicle
            if not Vehicle.objects.filter(id=data['load_to']).exists():
                raise ValidationError(_("Invalid vehicle"))
            
            # Validate load date
            if 'load_date' in data:
                if data['load_date'] < date.today():
                    raise ValidationError(_("Load date cannot be in the past"))
            
            # Validate items
            if not data['items_data']:
                raise ValidationError(_("At least one item is required"))
                
            LoadOrderValidator.validate_items_data(data['items_data'])
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[LOAD ORDER VALIDATOR] Error validating load order data: {str(e)}")
            raise ValidationError(_("Error validating load order data"))
    
    @staticmethod
    def validate_items_data(items_data: list) -> None:
        """Validate load order items data"""
        try:
            if not isinstance(items_data, list):
                raise ValidationError(_("Items data must be a list"))
            
            for item in items_data:
                # Required fields
                if not item.get('product'):
                    raise ValidationError(_("Product is required for all items"))
                if not item.get('quantity'):
                    raise ValidationError(_("Quantity is required for all items"))
                
                # Validate product
                if not Product.objects.filter(id=item['product']).exists():
                    raise ValidationError(_("Invalid product"))
                
                # Validate quantity
                if item['quantity'] <= 0:
                    raise ValidationError(_("Quantity must be positive"))
                
                # Validate product stock
                product = Product.objects.get(id=item['product'])
                if product.quantity < item['quantity']:
                    raise ValidationError(_(f"Insufficient stock for product {product.name}"))
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[LOAD ORDER VALIDATOR] Error validating items data: {str(e)}")
            raise ValidationError(_("Error validating items data"))
    
    @staticmethod
    def validate_vehicle_capacity(vehicle: Vehicle, items_data: list) -> None:
        """Validate if vehicle has capacity for all items"""
        try:
            total_quantity = sum(item['quantity'] for item in items_data)
            if total_quantity > vehicle.capacity:
                raise ValidationError(_("Total quantity exceeds vehicle capacity"))
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[LOAD ORDER VALIDATOR] Error validating vehicle capacity: {str(e)}")
            raise ValidationError(_("Error validating vehicle capacity"))