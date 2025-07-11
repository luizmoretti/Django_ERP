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
            ('update_status', gettext('Can update vehicle status')),
        ]
    
    def __str__(self):
        if self.nickname:
            return f"{self.nickname} - {self.plate_number}"
    
    @property
    def full_name(self) -> str:
        """Returns the full name/description of the vehicle"""
        return f"[{self.vehicle_type}] {self.nickname}-{self.plate_number}"