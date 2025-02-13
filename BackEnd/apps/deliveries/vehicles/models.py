from django.db import models
from apps.companies.employeers.models import Employeer
from core.constants.choices import VEHICLE_COLOR_CHOICES, VEHICLE_TYPE_CHOICES, VEHICLE_MAKER_CHOICES
from basemodels.models import BaseModel


class Vehicle(BaseModel):
    name = models.CharField(max_length=50, null=True, blank=True, help_text='The name of the vehicle')
    plate = models.CharField(max_length=50, blank=True, null=True, help_text='The tag of the vehicle')
    driver = models.ForeignKey(Employeer, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_driver')
    drivers_license = models.CharField(max_length=50, blank=True, null=True, help_text='The driver license of the vehicle')
    vehicle_maker = models.CharField(max_length=50, choices=VEHICLE_MAKER_CHOICES, null=True, blank=True, help_text='The maker of the vehicle')
    vehicle_model = models.CharField(max_length=50, null=True, blank=True, help_text='The model of the vehicle')
    vehicle_color = models.CharField(max_length=50, choices=VEHICLE_COLOR_CHOICES, null=True, blank=True, help_text='The color of the vehicle')
    type = models.CharField(max_length=50, choices=VEHICLE_TYPE_CHOICES, null=True, blank=True, help_text='The type of the delivery vehicle')
    vehicle_is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
        ordering = ['-created_at']
    
    def is_active(self) -> bool:
        return self.vehicle_is_active
    
    def __str__(self):
        return f'{self.name} | {self.plate}'
    
class VehicleMilageHistory(BaseModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='milage_history')
    milage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='The milage of the vehicle')
    
    class Meta:
        verbose_name = 'Vehicle Milage History'
        verbose_name_plural = 'Vehicle Milage Histories'
        ordering = ['-created_at']
    
class VehicleMaintenance(BaseModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='vehicle_maintenances')
    reason = models.TextField(help_text='The reason of the maintenance')
    is_in_service = models.BooleanField(default=True, help_text='Whether the vehicle is still in service')
    
    is_scheduled = models.BooleanField(default=False, help_text='Whether the maintenance is scheduled')
    date_of_scheduled = models.DateTimeField(null=True, blank=True, help_text='The date of the maintenance')
    
    class Meta:
        verbose_name = 'Vehicle Maintenance'
        verbose_name_plural = 'Vehicle Maintenances'
        ordering = ['-created_at']
        
class VehicleMaintenanceHistory(BaseModel):
    vehicle_maintenance = models.ForeignKey(VehicleMaintenance, on_delete=models.CASCADE, related_name='maintenance_history')
    
    
    
