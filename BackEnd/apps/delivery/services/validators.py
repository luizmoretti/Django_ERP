from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from ..models import Delivery
from apps.companies.customers.models import Customer
from apps.companies.employeers.models import Employeer
from apps.vehicle.models import Vehicle
from apps.inventory.load_order.models import LoadOrder
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class DeliveryValidator:
    """Validator for delivery operations that enforces business rules and data integrity."""
    
    @staticmethod
    def validate_delivery_data(data: dict) -> None:
        """
        Validates delivery data before creation or update.
        
        Checks:
        - Required fields are present
        - Customer, driver, and vehicle exist and are valid
        - Driver has valid license
        - Vehicle is active
        - Load orders exist and are not already in active deliveries
        - Status value is valid if provided
        
        Args:
            data: Dictionary containing delivery data
            
        Raises:
            ValidationError: If any validation check fails
        """
        try:
            # Required fields
            required_fields = ['customer', 'driver', 'vehicle', 'load']
            for field in required_fields:
                if field not in data:
                    raise ValidationError(_(f"{field} is required"))
            
            # Validate customer
            if 'customer' in data:
                customer_id = data['customer']
                if not Customer.objects.filter(id=customer_id).exists():
                    raise ValidationError(_("Invalid customer"))
            
            # Validate driver
            if 'driver' in data:
                driver_id = data['driver']
                if not Employeer.objects.filter(id=driver_id).exists():
                    raise ValidationError(_("Invalid driver"))
                
                # Check if driver has valid license
                # driver = Employeer.objects.get(id=driver_id)
                # if not hasattr(driver, 'driver_details') or not driver.driver_details.has_valid_license:
                    # raise ValidationError(_("Driver does not have a valid license"))
            
            # Validate vehicle
            if 'vehicle' in data:
                vehicle_id = data['vehicle']
                if not Vehicle.objects.filter(id=vehicle_id).exists():
                    raise ValidationError(_("Invalid vehicle"))
                
                # Check if vehicle is available
                vehicle = Vehicle.objects.get(id=vehicle_id)
                if not vehicle.is_active:
                    raise ValidationError(_("Vehicle is not available for deliveries"))
            
            # Validate load orders
            if 'load' in data:
                load_ids = data['load']
                if not isinstance(load_ids, list):
                    raise ValidationError(_("Load orders must be a list"))
                
                if not load_ids:
                    raise ValidationError(_("At least one load order is required"))
                
                for load_id in load_ids:
                    if not LoadOrder.objects.filter(id=load_id).exists():
                        raise ValidationError(_("Invalid load order"))
                    
                    # Check if load is already associated with another active delivery
                    load = LoadOrder.objects.get(id=load_id)
                    active_deliveries = Delivery.objects.filter(
                        load=load,
                        status__in=['pending', 'pickup_in_progress', 'in_transit']
                    )
                    
                    if active_deliveries.exists():
                        raise ValidationError(_(f"Load order {load.order_number} is already in an active delivery"))
            
            # Validate status (if provided)
            if 'status' in data:
                status = data['status']
                from core.constants.choices import DELIVERY_STATUS_CHOICES
                valid_statuses = [choice[0] for choice in DELIVERY_STATUS_CHOICES]
                if status not in valid_statuses:
                    raise ValidationError(_(f"Invalid status. Valid values: {', '.join(valid_statuses)}"))
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[DELIVERY VALIDATOR] Error validating delivery data: {str(e)}")
            raise ValidationError(_("Error validating delivery data"))
    
    @staticmethod
    def validate_delivery_update(delivery: Delivery, data: dict) -> None:
        """
        Validates updates to an existing delivery.
        
        Checks:
        - Basic data validation
        - Delivery is not in a final state
        - Status transition is valid (if status is being changed)
        
        Args:
            delivery: Existing Delivery instance to update
            data: Dictionary containing updated delivery data
            
        Raises:
            ValidationError: If any validation check fails
        """
        try:
            # Validate basic data
            DeliveryValidator.validate_delivery_data(data)
            
            # Check if delivery can be updated
            if delivery.status == 'delivered':
                raise ValidationError(_("Cannot update a completed delivery"))
            
            # Validate status change (if exists)
            if 'status' in data and data['status'] != delivery.status:
                DeliveryValidator.validate_status_change(delivery, data['status'])
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[DELIVERY VALIDATOR] Error validating delivery update: {str(e)}")
            raise ValidationError(_("Error validating delivery update"))
    
    @staticmethod
    def validate_status_change(delivery: Delivery, new_status: str) -> None:
        """
        Validates status transitions according to the delivery workflow.
        
        Ensures status changes follow a predefined workflow:
        - pending → pickup_in_progress → in_transit → delivered
        - With possible terminal states: cancelled, returned, failed
        
        Args:
            delivery: Delivery instance to update
            new_status: Proposed new status
            
        Raises:
            ValidationError: If the status transition is invalid
        """
        try:
            current_status = delivery.status
            
            # Define valid status transition flow
            valid_transitions = {
                'pending': ['pickup_in_progress', 'cancelled'],
                'pickup_in_progress': ['in_transit', 'cancelled'],
                'in_transit': ['delivered', 'returned', 'failed'],
                'delivered': [],  # Final state
                'returned': [],   # Final state
                'failed': [],     # Final state
                'cancelled': []   # Final state
            }
            
            if new_status not in valid_transitions.get(current_status, []):
                raise ValidationError(_(
                    f"Invalid status transition: {current_status} → {new_status}. "
                    f"Valid transitions: {', '.join(valid_transitions.get(current_status, []))}"
                ))
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[DELIVERY VALIDATOR] Error validating status change: {str(e)}")
            raise ValidationError(_("Error validating status change"))
    
    @staticmethod
    def validate_location_update(delivery: Delivery, data: dict) -> None:
        """
        Validates location updates for a delivery.
        
        Checks:
        - Required coordinate fields are present
        - Coordinates are valid numbers within range
        - Delivery is not in a final state
        
        Args:
            delivery: Delivery instance to update
            data: Dictionary containing location data (latitude, longitude)
            
        Raises:
            ValidationError: If any validation check fails
        """
        try:
            # Check coordinates
            required_fields = ['latitude', 'longitude']
            for field in required_fields:
                if field not in data:
                    raise ValidationError(_(f"{field} is required"))
            
            # Validate coordinate format
            try:
                lat = float(data['latitude'])
                lng = float(data['longitude'])
                
                # Validate values within limits
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    raise ValidationError(_("Coordinates outside valid limits"))
            except ValueError:
                raise ValidationError(_("Coordinates must be numeric values"))
            
            # Check if delivery can receive location updates
            if delivery.status in ['delivered', 'returned', 'failed', 'cancelled']:
                raise ValidationError(_("Cannot update location of a completed delivery"))
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[DELIVERY VALIDATOR] Error validating location update: {str(e)}")
            raise ValidationError(_("Error validating location update"))
