from ..models import Vehicle, VehicleMilageHistory, VehicleMaintenance, VehicleMaintenanceHistory
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from apps.companies.models import Companie
from django.core.exceptions import ValidationError
from django.db import transaction


class VehicleServices:
    @staticmethod
    def get_vehicle_by_id(id: str) -> Vehicle:
        """
        Retrieve a vehicle by its ID
        
        Args:
            id (str): The ID of the vehicle to retrieve
            
        Returns:
            Vehicle: The retrieved vehicle
            
        Raises:
            Vehicle.DoesNotExist: If no vehicle with the given ID exists
        """
        return Vehicle.objects.get(id=id)
    
    @staticmethod
    def get_vehicles_by_company(companie: Companie) -> List[Vehicle]:
        """
        Retrieve all vehicles for a given company
        
        Args:
            companie (Companie): The company to get vehicles for
            
        Returns:
            List[Vehicle]: List of vehicles belonging to the company
        """
        return Vehicle.objects.filter(companie=companie)
    
    @staticmethod
    def create_vehicle(vehicle: Vehicle) -> Vehicle:
        """
        Create a new vehicle
        
        Args:
            vehicle (Vehicle): The vehicle instance to create
            
        Returns:
            Vehicle: The created vehicle
            
        Raises:
            ValidationError: If the vehicle data is invalid
        """
        vehicle.full_clean()  # Validate model
        vehicle.save()
        return vehicle
    
    @staticmethod
    def update_vehicle(id: int, data: Dict[str, Any]) -> Vehicle:
        """
        Update a vehicle with the given data
        
        Args:
            id (int): The ID of the vehicle to update
            data (Dict[str, Any]): Dictionary of fields to update
            
        Returns:
            Vehicle: The updated vehicle
            
        Raises:
            Vehicle.DoesNotExist: If no vehicle with the given ID exists
            ValidationError: If the update data is invalid
        """
        vehicle = Vehicle.objects.get(id=id)
        for field, value in data.items():
            setattr(vehicle, field, value)
        vehicle.full_clean()  # Validate model
        vehicle.save()
        return vehicle
    
    @staticmethod
    def delete_vehicle(id: str) -> None:
        """
        Delete a vehicle by its ID
        
        Args:
            id (str): The ID of the vehicle to delete
            
        Raises:
            Vehicle.DoesNotExist: If no vehicle with the given ID exists
        """
        vehicle = Vehicle.objects.get(id=id)  # This will raise DoesNotExist if not found
        vehicle.delete()
    
    @staticmethod
    def record_mileage(vehicle: Vehicle, mileage: int) -> VehicleMilageHistory:
        """
        Record a new mileage reading for a vehicle
        
        Args:
            vehicle (Vehicle): The vehicle to record mileage for
            mileage (int): The current mileage reading
            
        Returns:
            VehicleMilageHistory: The created mileage history record
            
        Raises:
            ValidationError: If the mileage is less than the previous reading
        """
        # Get last mileage reading
        last_reading = VehicleMilageHistory.objects.filter(vehicle=vehicle).order_by('-created_at').first()
        if last_reading and mileage < last_reading.milage:
            raise ValidationError("New mileage reading cannot be less than previous reading")
            
        mileage_history = VehicleMilageHistory(vehicle=vehicle, milage=mileage)
        mileage_history.save()
        return mileage_history


class VehicleMaintenanceServices:
    @staticmethod
    def get_vehicle_maintenance_by_vehicle(vehicle: Vehicle) -> List[VehicleMaintenance]:
        """
        Get all maintenance records for a vehicle
        
        Args:
            vehicle (Vehicle): The vehicle to get maintenance records for
            
        Returns:
            List[VehicleMaintenance]: List of maintenance records
        """
        return VehicleMaintenance.objects.filter(vehicle=vehicle)
    
    @staticmethod
    def create_vehicle_maintenance(vehicle_maintenance: VehicleMaintenance) -> VehicleMaintenance:
        """
        Create a new maintenance record
        
        Args:
            vehicle_maintenance (VehicleMaintenance): The maintenance record to create
            
        Returns:
            VehicleMaintenance: The created maintenance record
            
        Raises:
            ValidationError: If the maintenance data is invalid
        """
        vehicle_maintenance.full_clean()  # Validate model
        vehicle_maintenance.save()
        return vehicle_maintenance
    
    @staticmethod
    def schedule_vehicle_maintenance(vehicle_maintenance: VehicleMaintenance, scheduled_date: datetime) -> VehicleMaintenance:
        """
        Schedule a vehicle maintenance by setting is_scheduled to True and the scheduled date
        
        Args:
            vehicle_maintenance (VehicleMaintenance): The maintenance to be scheduled
            scheduled_date (datetime): The date when the maintenance is scheduled to occur
            
        Returns:
            VehicleMaintenance: The updated maintenance object
            
        Raises:
            ValidationError: If the scheduled date is in the past
        """
        if scheduled_date < datetime.now():
            raise ValidationError("Cannot schedule maintenance for a past date")
            
        vehicle_maintenance.is_scheduled = True
        vehicle_maintenance.date_of_scheduled = scheduled_date
        vehicle_maintenance.save()
        return vehicle_maintenance
    
    @staticmethod
    def complete_maintenance(maintenance: VehicleMaintenance, completion_notes: Optional[str] = None) -> VehicleMaintenanceHistory:
        """
        Mark a maintenance as completed and create a maintenance history record
        
        Args:
            maintenance (VehicleMaintenance): The maintenance to complete
            completion_notes (Optional[str]): Optional notes about the completed maintenance
            
        Returns:
            VehicleMaintenanceHistory: The created maintenance history record
        """
        with transaction.atomic():
            # Update maintenance status
            maintenance.is_in_service = False
            maintenance.save()
            
            # Create maintenance history record
            history = VehicleMaintenanceHistory(
                vehicle_maintenance=maintenance,
                notes=completion_notes
            )
            history.save()
            
            return history
    
    @staticmethod
    def get_upcoming_maintenance(days: int = 7) -> List[VehicleMaintenance]:
        """
        Get list of scheduled maintenance due within specified number of days
        
        Args:
            days (int): Number of days to look ahead (default: 7)
            
        Returns:
            List[VehicleMaintenance]: List of upcoming maintenance
        """
        future_date = datetime.now() + relativedelta(days=days)
        return VehicleMaintenance.objects.filter(
            is_scheduled=True,
            is_in_service=True,
            date_of_scheduled__lte=future_date
        ).order_by('date_of_scheduled')