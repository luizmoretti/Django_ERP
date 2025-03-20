from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from apps.vehicle.models import Vehicle
from apps.companies.employeers.models import Employeer
from .validators import VehicleBusinessValidator

import logging

logger = logging.getLogger(__name__)


class VehicleService:
    """Service for vehicle operations
    
    This service provides business logic for vehicle-related operations,
    including creation, updates, and status management.
    """
    
    def __init__(self):
        self.validator = VehicleBusinessValidator()
        
    @transaction.atomic
    def create_vehicle(self, data, user):
        """Create a new vehicle
        
        Args:
            data (dict): Data for creating vehicle
            user: User creating the vehicle
            
        Returns:
            Vehicle: Created vehicle instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Validate business rules
            self.validator.validate_company_access(data, user)
            
            # Set audit fields
            data['companie'] = user.companie
            data['created_by'] = user
            data['updated_by'] = user
            
            # Create vehicle
            vehicle = Vehicle.objects.create(**data)
            
            logger.info(f"[VEHICLE SERVICE] - Vehicle {vehicle.plate_number} created successfully", 
                       extra={'vehicle_id': str(vehicle.id)})
            return vehicle
            
        except ValidationError as e:
            logger.warning(f"[VEHICLE SERVICE] - Validation error creating vehicle: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[VEHICLE SERVICE] - Error creating vehicle: {str(e)}")
            raise ValidationError(_("Error creating vehicle"))
    
    @transaction.atomic
    def update_vehicle(self, instance, data, user):
        """Update an existing vehicle
        
        Args:
            instance (Vehicle): Vehicle to update
            data (dict): Updated data
            user: User updating the vehicle
            
        Returns:
            Vehicle: Updated vehicle instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Validate business rules
            self.validator.validate_company_access(instance, user)
            
            # Update fields
            for field, value in data.items():
                setattr(instance, field, value)
            
            # Update audit fields
            instance.updated_by = user
            instance.save()
            
            logger.info(f"[VEHICLE SERVICE] - Vehicle {instance.plate_number} updated successfully", 
                       extra={'vehicle_id': str(instance.id)})
            return instance
            
        except ValidationError as e:
            logger.warning(f"[VEHICLE SERVICE] - Validation error updating vehicle: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[VEHICLE SERVICE] - Error updating vehicle: {str(e)}")
            raise ValidationError(_("Error updating vehicle"))
    
    @transaction.atomic
    def delete_vehicle(self, instance, user):
        """Delete a vehicle
        
        Args:
            instance (Vehicle): Vehicle to delete
            user: User deleting the vehicle
            
        Raises:
            ValidationError: If deletion is not allowed or fails
        """
        try:
            # Validate business rules
            self.validator.validate_company_access(instance, user)
            self.validator.validate_vehicle_can_be_deleted(instance)
            
            # Store reference for logging
            plate_number = instance.plate_number
            vehicle_id = str(instance.id)
            
            # Delete the vehicle
            instance.delete()
            
            logger.info(f"[VEHICLE SERVICE] - Vehicle {plate_number} deleted successfully", 
                       extra={'vehicle_id': vehicle_id})
            
        except ValidationError as e:
            logger.warning(f"[VEHICLE SERVICE] - Validation error deleting vehicle: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[VEHICLE SERVICE] - Error deleting vehicle: {str(e)}")
            raise ValidationError(_("Error deleting vehicle"))
    
    @transaction.atomic
    def assign_driver(self, vehicle_id, driver_id, user):
        """Assign a driver to a vehicle
        
        Args:
            vehicle_id: ID of the vehicle
            driver_id: ID of the driver to assign
            user: User making the assignment
            
        Returns:
            Vehicle: Updated vehicle instance
            
        Raises:
            ValidationError: If assignment fails
        """
        try:
            # Validate permissions
            if not user.has_perm('vehicle.assign_driver'):
                raise ValidationError(_("You do not have permission to assign drivers"))
            
            # Get vehicle and validate access
            vehicle = Vehicle.objects.get(id=vehicle_id)
            self.validator.validate_company_access(vehicle, user)
            
            # Get driver
            driver = Employeer.objects.filter(
                id=driver_id,
                companie=user.companie
            ).first()
            
            if not driver:
                raise ValidationError(_("Driver not found"))
            
            # Assign driver
            vehicle.assigned_driver = driver
            vehicle.updated_by = user
            vehicle.save()
            
            logger.info(
                f"[VEHICLE SERVICE] - Driver {driver.first_name} {driver.last_name} assigned to vehicle {vehicle.plate_number}",
                extra={'vehicle_id': str(vehicle.id), 'driver_id': str(driver.id)}
            )
            
            return vehicle
            
        except Vehicle.DoesNotExist:
            logger.warning(f"[VEHICLE SERVICE] - Vehicle with ID {vehicle_id} not found")
            raise ValidationError(_("Vehicle not found"))
        except ValidationError as e:
            logger.warning(f"[VEHICLE SERVICE] - Validation error assigning driver: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[VEHICLE SERVICE] - Error assigning driver: {str(e)}")
            raise ValidationError(_("Error assigning driver to vehicle"))
    
    @transaction.atomic
    def update_vehicle_status(self, instance, is_active, user):
        """Update a vehicle's active status
        
        Args:
            instance (Vehicle): Vehicle to update
            is_active (bool): New active status
            user: User updating the status
            
        Returns:
            Vehicle: Updated vehicle instance
            
        Raises:
            ValidationError: If update fails
        """
        try:
            # Validate business rules
            self.validator.validate_company_access(instance, user)
            
            # Check permissions
            if not user.has_perm('vehicle.update_status'):
                raise ValidationError(_("You do not have permission to update vehicle status"))
            
            # Update status
            instance.is_active = is_active
            instance.updated_by = user
            instance.save()
            
            status_msg = "activated" if is_active else "deactivated"
            logger.info(f"[VEHICLE SERVICE] - Vehicle {instance.plate_number} {status_msg} successfully", 
                       extra={'vehicle_id': str(instance.id)})
            return instance
            
        except ValidationError as e:
            logger.warning(f"[VEHICLE SERVICE] - Validation error updating vehicle status: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[VEHICLE SERVICE] - Error updating vehicle status: {str(e)}")
            raise ValidationError(_("Error updating vehicle status"))