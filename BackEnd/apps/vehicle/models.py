from django.db import models
from django.utils.translation import gettext
from django.core.validators import RegexValidator
from basemodels.models import BaseModel
from core.constants.choices import (
    VEHICLE_TYPE_CHOICES, 
    VEHICLE_MAKER_CHOICES, 
    VEHICLE_COLOR_CHOICES
)
from apps.companies.employeers.models import Employeer


class Vehicle(BaseModel):
    """
    Model representing a vehicle in the system.
    
    This model stores all information related to vehicles used for deliveries,
    including identification, technical specifications, documentation, and status.
    """
    # Identification
    plate_number = models.CharField(
        max_length=20, 
        unique=True, 
        help_text=gettext('License plate number of the vehicle')
    )
    nickname = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=gettext('Nickname or common name for the vehicle')
    )
    
    # Vehicle details
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_TYPE_CHOICES, 
        help_text=gettext('Type of vehicle')
    )
    maker = models.CharField(
        max_length=50, 
        choices=VEHICLE_MAKER_CHOICES, 
        help_text=gettext('Manufacturer of the vehicle')
    )
    color = models.CharField(
        max_length=20, 
        choices=VEHICLE_COLOR_CHOICES, 
        help_text=gettext('Color of the vehicle')
    )
    
    # Technical specifications
    vin = models.CharField(
        max_length=17, 
        validators=[
            RegexValidator(
                regex=r'^[A-HJ-NPR-Z0-9]{17}$',
                message=gettext('VIN must be 17 characters and not include I, O, or Q')
            )
        ],
        unique=True,
        verbose_name=gettext('VIN'),
        help_text=gettext('Vehicle Identification Number')
    )
    capacity_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text=gettext('Maximum weight capacity in pounds')
    )
    capacity_volume = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text=gettext('Maximum volume capacity in cubic feet')
    )
    
    # Documentation and legal
    insurance_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=gettext('Insurance policy number')
    )
    insurance_expiry = models.DateField(
        blank=True, 
        null=True, 
        help_text=gettext('Insurance policy expiry date')
    )
    registration_expiry = models.DateField(
        blank=True, 
        null=True, 
        help_text=gettext('Vehicle registration expiry date')
    )
    
    # Maintenance and status
    last_maintenance_date = models.DateField(
        blank=True, 
        null=True, 
        help_text=gettext('Date of last maintenance')
    )
    next_maintenance_date = models.DateField(
        blank=True, 
        null=True, 
        help_text=gettext('Scheduled date for next maintenance')
    )
    odometer = models.PositiveIntegerField(
        default=0, 
        help_text=gettext('Current odometer reading in miles')
    )
    fuel_level = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.0, 
        help_text=gettext('Current fuel level (percentage)')
    )
    is_active = models.BooleanField(
        default=True, 
        help_text=gettext('Whether the vehicle is currently active and available for use')
    )
    
    # Assignment
    assigned_driver = models.ForeignKey(
        Employeer, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='vehicles',
        help_text=gettext('Driver currently assigned to this vehicle')
    )
    
    class Meta:
        verbose_name = gettext('Vehicle')
        verbose_name_plural = gettext('Vehicles')
        ordering = ['plate_number']
        permissions = [
            ('assign_driver', gettext('Can assign drivers to vehicles')),
            ('record_maintenance', gettext('Can record maintenance for vehicles')),
            ('update_status', gettext('Can update vehicle status')),
        ]
    
    def __str__(self):
        if self.nickname:
            return f"{self.nickname} ({self.plate_number})"
        return f"{self.maker} {self.model} - {self.plate_number}"
    
    @property
    def full_name(self):
        """Returns the full name/description of the vehicle"""
        return f"{self.year} {self.maker} {self.model} ({self.color})"
    
    @property
    def maintenance_due(self):
        """Check if maintenance is due based on the next_maintenance_date"""
        from datetime import date
        if not self.next_maintenance_date:
            return False
        return self.next_maintenance_date <= date.today()
    
    @property
    def documentation_valid(self):
        """Check if all documentation is valid and not expired"""
        from datetime import date
        today = date.today()
        
        if not self.insurance_expiry or not self.registration_expiry:
            return False
            
        return (self.insurance_expiry > today and 
                self.registration_expiry > today)


class VehicleMaintenanceRecord(BaseModel):
    """
    Model representing a maintenance record for a vehicle.
    
    This model tracks all maintenance activities performed on vehicles,
    including routine maintenance, repairs, and inspections.
    """
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE, 
        related_name='maintenance_records',
        help_text=gettext('Vehicle that received maintenance')
    )
    
    # Maintenance details
    maintenance_type = models.CharField(
        max_length=100, 
        help_text=gettext('Type of maintenance performed')
    )
    description = models.TextField(
        help_text=gettext('Detailed description of the maintenance performed')
    )
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text=gettext('Cost of the maintenance')
    )
    
    # Service information
    service_date = models.DateField(
        help_text=gettext('Date when the maintenance was performed')
    )
    odometer_reading = models.PositiveIntegerField(
        help_text=gettext('Odometer reading at the time of maintenance')
    )
    performed_by = models.CharField(
        max_length=255, 
        help_text=gettext('Person or company that performed the maintenance')
    )
    
    # Documentation
    invoice_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=gettext('Invoice or reference number for the maintenance')
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text=gettext('Additional notes about the maintenance')
    )
    
    # Follow-up
    next_maintenance_date = models.DateField(
        blank=True, 
        null=True, 
        help_text=gettext('Recommended date for next maintenance')
    )
    next_maintenance_odometer = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        help_text=gettext('Recommended odometer reading for next maintenance')
    )
    
    class Meta:
        verbose_name = gettext('Maintenance Record')
        verbose_name_plural = gettext('Maintenance Records')
        ordering = ['-service_date']
    
    def __str__(self):
        return f"{self.vehicle} - {self.maintenance_type} ({self.service_date})"
    
    def save(self, *args, **kwargs):
        """
        Override save method to update the vehicle's last_maintenance_date
        and next_maintenance_date when a maintenance record is created.
        """
        super().save(*args, **kwargs)
        
        # Update the vehicle's maintenance dates
        vehicle = self.vehicle
        
        # Update last maintenance date if this is the most recent record
        if (not vehicle.last_maintenance_date or 
            self.service_date >= vehicle.last_maintenance_date):
            vehicle.last_maintenance_date = self.service_date
        
        # Update next maintenance date if provided
        if self.next_maintenance_date:
            if (not vehicle.next_maintenance_date or 
                self.next_maintenance_date < vehicle.next_maintenance_date):
                vehicle.next_maintenance_date = self.next_maintenance_date
        
        # Update odometer if it's higher than current reading
        if self.odometer_reading > vehicle.odometer:
            vehicle.odometer = self.odometer_reading
            
        vehicle.save(update_fields=[
            'last_maintenance_date', 
            'next_maintenance_date', 
            'odometer'
        ])


class VehicleFuelRecord(BaseModel):
    """
    Model representing a fuel record for a vehicle.
    
    This model tracks all fuel purchases and consumption for vehicles,
    helping to monitor fuel efficiency and costs.
    """
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE, 
        related_name='fuel_records',
        help_text=gettext('Vehicle that received fuel')
    )
    
    # Fuel details
    date = models.DateField(
        help_text=gettext('Date of the fuel purchase')
    )
    odometer_reading = models.PositiveIntegerField(
        help_text=gettext('Odometer reading at the time of fueling')
    )
    fuel_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        help_text=gettext('Amount of fuel added in gallons')
    )
    fuel_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text=gettext('Total cost of the fuel purchase')
    )
    fuel_type = models.CharField(
        max_length=50, 
        default='Regular',
        help_text=gettext('Type of fuel purchased')
    )
    
    # Location
    station_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=gettext('Name of the fuel station')
    )
    location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text=gettext('Location where fuel was purchased')
    )
    
    # Additional information
    full_tank = models.BooleanField(
        default=True, 
        help_text=gettext('Whether the tank was filled completely')
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text=gettext('Additional notes about the fuel purchase')
    )
    
    class Meta:
        verbose_name = gettext('Fuel Record')
        verbose_name_plural = gettext('Fuel Records')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.vehicle} - {self.date} ({self.fuel_amount} gal)"
    
    @property
    def price_per_gallon(self):
        """Calculate the price per gallon for this fuel purchase"""
        if self.fuel_amount > 0:
            return self.fuel_cost / self.fuel_amount
        return 0
    
    def save(self, *args, **kwargs):
        """
        Override save method to update the vehicle's odometer and fuel level
        when a fuel record is created.
        """
        super().save(*args, **kwargs)
        
        # Update the vehicle's odometer if this reading is higher
        vehicle = self.vehicle
        if self.odometer_reading > vehicle.odometer:
            vehicle.odometer = self.odometer_reading
            
        # Update fuel level if tank was filled completely
        if self.full_tank:
            vehicle.fuel_level = 100.0
            
        vehicle.save(update_fields=['odometer', 'fuel_level'])
