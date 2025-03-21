from django.db import models
from core.constants.choices import DELIVERY_STATUS_CHOICES
from basemodels.models import BaseModel
from apps.companies.customers.models import Customer
from apps.companies.employeers.models import Employeer
from apps.vehicle.models import Vehicle
from apps.inventory.load_order.models import LoadOrder

class Delivery(BaseModel):
    load = models.ManyToManyField(LoadOrder, related_name='delivery', help_text='The load that the delivery is for')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='delivery', help_text='The customer that the delivery is for')
    driver = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='delivery', help_text='The driver that the delivery is for')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='delivery', help_text='The vehicle that the delivery is for')
    status = models.CharField(max_length=35, choices=DELIVERY_STATUS_CHOICES, default='pending', help_text='The status of the delivery')
    
    ### Delivery Tracking Fields
    current_location = models.JSONField(null=True, blank=True, help_text='Latitude/Longitude')
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True) 
    
    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.customer.name} - {self.vehicle.nickname} - {self.status}'
    
    

class DeliveryCheckpoint(BaseModel):
    delivery = models.ForeignKey('Delivery', on_delete=models.CASCADE, related_name='checkpoints')
    location = models.JSONField()  # Latitude/Longitude
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=35, choices=DELIVERY_STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='checkpoints/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Delivery Checkpoint'
        verbose_name_plural = 'Delivery Checkpoints'
        ordering = ['-created_at']
        
