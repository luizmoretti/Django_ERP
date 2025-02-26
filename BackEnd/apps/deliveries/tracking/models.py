from django.db import models
from basemodels.models import BaseModel
from apps.deliveries.models import Delivery
from apps.deliveries.vehicles.models import Vehicle
from django.contrib.gis.db import models as gis_models

# Definir as opções de status para as entregas
DELIVERY_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_transit', 'In Transit'),
    ('delivered', 'Delivered'),
    ('returned', 'Returned'),
    ('failed', 'Failed'),
]

class DeliveryLocationUpdate(BaseModel):
    """
    Stores location updates for deliveries.
    Each update contains GPS coordinates and timestamp.
    """
    delivery = models.ForeignKey(
        Delivery, 
        on_delete=models.CASCADE, 
        related_name='location_updates',
        help_text='The delivery associated with this location update'
    )
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='location_updates',
        help_text='The vehicle that sent this location update'
    )
    # Using GeoDjango to store coordinates
    location = gis_models.PointField(
        help_text='GPS coordinates (longitude, latitude)'
    )
    accuracy = models.FloatField(
        null=True, 
        blank=True,
        help_text='Accuracy of the location in meters'
    )
    speed = models.FloatField(
        null=True, 
        blank=True,
        help_text='Speed in km/h'
    )
    heading = models.FloatField(
        null=True, 
        blank=True,
        help_text='Heading in degrees (0-360)'
    )
    
    class Meta:
        verbose_name = 'Location Update'
        verbose_name_plural = 'Location Updates'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Location of {self.delivery.number} at {self.created_at}'

class DeliveryRoute(BaseModel):
    """
    Stores information about the planned route for a delivery.
    """
    delivery = models.OneToOneField(
        Delivery, 
        on_delete=models.CASCADE, 
        related_name='route',
        help_text='The delivery associated with this route'
    )
    estimated_distance = models.FloatField(
        null=True, 
        blank=True,
        help_text='Estimated distance in km'
    )
    estimated_duration = models.DurationField(
        null=True, 
        blank=True,
        help_text='Estimated duration of the trip'
    )
    estimated_arrival = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Estimated arrival time'
    )
    # Store the route as a LineString (series of points)
    route_geometry = gis_models.LineStringField(
        null=True, 
        blank=True,
        help_text='Route geometry as LineString'
    )
    # Store additional route data (instructions, waypoints, etc.)
    route_data = models.JSONField(
        null=True, 
        blank=True,
        help_text='Additional route data in JSON format'
    )
    
    class Meta:
        verbose_name = 'Delivery Route'
        verbose_name_plural = 'Delivery Routes'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Route for {self.delivery.number}'

class DeliveryStatusUpdate(BaseModel):
    """
    Stores status updates for deliveries.
    """
    delivery = models.ForeignKey(
        Delivery, 
        on_delete=models.CASCADE, 
        related_name='status_updates',
        help_text='The delivery associated with this status update'
    )
    status = models.CharField(
        max_length=100, 
        choices=DELIVERY_STATUS_CHOICES,
        help_text='The new status of the delivery'
    )
    location_update = models.ForeignKey(
        DeliveryLocationUpdate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='status_updates',
        help_text='The location update associated with this status change'
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text='Additional notes about the status change'
    )
    
    class Meta:
        verbose_name = 'Status Update'
        verbose_name_plural = 'Status Updates'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Status of {self.delivery.number} changed to {self.status}'