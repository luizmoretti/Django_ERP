from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from apps.vehicle.models import Vehicle

import logging

logger = logging.getLogger(__name__)


class VehicleBusinessValidator:
    """Business validator for Vehicle operations
    
    This class provides validation methods for business rules related to vehicles,
    including company access and operation constraints.
    """
    
    def validate_company_access(self, instance_or_data, user):
        """Validate that the user has access to the company associated with a vehicle
        
        Args:
            instance_or_data: Either a Vehicle instance or data dict for a new vehicle
            user: User attempting the operation
            
        Raises:
            ValidationError: If user does not have access to the company
        """
        # When instance is a Vehicle object
        if isinstance(instance_or_data, Vehicle):
            if instance_or_data.companie != user.companie:
                logger.warning(f"[VEHICLE VALIDATOR] - User {user} attempted to access vehicle from different company")
                raise ValidationError(_("You do not have permission to access this vehicle"))
        
        # When we have data for a new vehicle
        elif isinstance(instance_or_data, dict) and 'companie' in instance_or_data:
            if instance_or_data['companie'] != user.companie:
                logger.warning(f"[VEHICLE VALIDATOR] - User {user} attempted to create vehicle for different company")
                raise ValidationError(_("You cannot create a vehicle for a different company"))
    
    def validate_vehicle_can_be_deleted(self, vehicle):
        """Validate that a vehicle can be deleted
        
        Checks if the vehicle has any dependencies that prevent deletion.
        
        Args:
            vehicle: Vehicle instance to check
            
        Raises:
            ValidationError: If vehicle cannot be deleted
        """
        # Check if vehicle is being used in active load orders
        load_order_relations = self._get_related_load_orders(vehicle)
        if load_order_relations and load_order_relations.exists():
            logger.warning(f"[VEHICLE VALIDATOR] - Cannot delete vehicle {vehicle.plate_number} with associated load orders")
            raise ValidationError(_("Cannot delete vehicle that is associated with load orders"))
    
    def validate_plate_number(self, plate_number, instance=None):
        """Validate that a plate number is unique
        
        Args:
            plate_number: Plate number to validate
            instance: Optional current vehicle instance (for updates)
            
        Raises:
            ValidationError: If plate number is not unique
        """
        query = Vehicle.objects.filter(plate_number=plate_number)
        
        # Exclude current instance for updates
        if instance:
            query = query.exclude(id=instance.id)
            
        if query.exists():
            logger.warning(f"[VEHICLE VALIDATOR] - Duplicate plate number: {plate_number}")
            raise ValidationError(_("A vehicle with this plate number already exists"))
    
    def validate_vin(self, vin, instance=None):
        """Validate that a VIN is unique
        
        Args:
            vin: VIN to validate
            instance: Optional current vehicle instance (for updates)
            
        Raises:
            ValidationError: If VIN is not unique
        """
        query = Vehicle.objects.filter(vin=vin)
        
        # Exclude current instance for updates
        if instance:
            query = query.exclude(id=instance.id)
            
        if query.exists():
            logger.warning(f"[VEHICLE VALIDATOR] - Duplicate VIN: {vin}")
            raise ValidationError(_("A vehicle with this VIN already exists"))
    
    def validate_driver_assignment(self, driver_id, user):
        """Validate that a driver can be assigned to a vehicle
        
        Args:
            driver_id: ID of the driver to assign
            user: User performing the assignment
            
        Raises:
            ValidationError: If driver assignment is not valid
        """
        from apps.companies.employeers.models import Employeer
        
        # Check if driver exists in the same company
        driver = Employeer.objects.filter(
            id=driver_id,
            companie=user.companie
        ).first()
        
        if not driver:
            logger.warning(f"[VEHICLE VALIDATOR] - Invalid driver assignment: Driver {driver_id} not found")
            raise ValidationError(_("Driver not found"))
        
        # Additional validation could be added here:
        # - Check if driver has required licenses
        # - Check if driver is already assigned to another vehicle
        # - Check if driver is active
    
    def _get_related_load_orders(self, vehicle):
        """Get load orders related to a vehicle
        
        This is a helper method to check dependencies for deletion.
        
        Args:
            vehicle: Vehicle instance
            
        Returns:
            QuerySet: Related load orders, if any
        """
        # Try to import the load order model if it exists
        try:
            # Assuming there's a related load order model that has a relation to vehicles
            # Adjust the import path and query according to your actual implementation
            from apps.logistics.models import LoadOrder
            return LoadOrder.objects.filter(vehicle=vehicle)
        except ImportError:
            # If the model doesn't exist, return None
            return None