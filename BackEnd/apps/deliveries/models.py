from django.db import models
from core.constants.choices import DELIVERY_STATUS_CHOICES
from .vehicles.models import Vehicle
from basemodels.models import BaseModel
from apps.inventory.product.models import Product
from apps.inventory.warehouse.models import Warehouse
from ..companies.customers.models import Customer 
from django.core.exceptions import ValidationError
from django.db.models import Sum
import datetime
from django.utils import timezone
from django.db import transaction
from django.db import IntegrityError

class Delivery(BaseModel):
    number = models.CharField(
        max_length=10, 
        null=True, 
        blank=True, 
        help_text='The number of the delivery'
    )
    origin = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='deliveries_origin', 
        help_text='The warehouse of the delivery'
    )
    destiny = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='deliveries_destiny', 
        help_text='The customer of the delivery'
    )
    driver = models.ForeignKey(
        Vehicle, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deliveries_driver', 
        help_text='The vehicle of the delivery'
    )
    status = models.CharField(
        max_length=100, 
        choices=DELIVERY_STATUS_CHOICES, 
        blank=True,
        help_text='The status of the delivery',
        default='pending'
    )
    
    # Fields for tracking
    is_tracking_enabled = models.BooleanField(
        default=True,
        help_text='If real-time tracking is enabled for this delivery'
    )
    estimated_start_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Estimated start time of the delivery'
    )
    actual_start_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Actual start time of the delivery'
    )
    estimated_delivery_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Estimated delivery time of the delivery'
    )
    actual_delivery_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Actual delivery time of the delivery'
    )
    
    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Delivery {self.number} from {self.origin} to {self.destiny}'
    
    
    def get_current_location(self):
        """Returns the most recent delivery location."""
        return self.location_updates.order_by('-created_at').first()
    
    def get_current_status(self):
        """Returns the most recent delivery status."""
        return self.status_updates.order_by('-created_at').first()
    
    def get_eta(self):
        """
        Calculates the estimated arrival time based on the current location and route.
        
        Returns:
            datetime: The estimated arrival time, or None if it cannot be calculated.
        """
        try:
            # Get the route information
            try:
                route = self.route
            except:
                return self.estimated_delivery_time
            
            # If no route is available, return the estimated delivery time
            if not route or not route.estimated_arrival:
                return self.estimated_delivery_time
            
            # Get the current location
            current_location = self.get_current_location()
            if not current_location:
                return route.estimated_arrival
            
            # If there's no speed data, return the route's estimated arrival
            if not current_location.speed or current_location.speed <= 0:
                return route.estimated_arrival
            
            # Get the route geometry
            if not route.route_geometry:
                return route.estimated_arrival
            
            # Calculate remaining distance
            from django.contrib.gis.geos import LineString
            from django.contrib.gis.db.models.functions import Distance
            
            # Create a line from the current location to the end of the route
            remaining_points = []
            
            # Find the closest point on the route to the current location
            closest_point_found = False
            min_distance = float('inf')
            closest_index = 0
            
            for i, point in enumerate(route.route_geometry):
                dist = current_location.location.distance(point)
                if dist < min_distance:
                    min_distance = dist
                    closest_index = i
                    closest_point_found = True
            
            # If we found a closest point, calculate the remaining route
            if closest_point_found:
                # Get the remaining points on the route
                remaining_points = list(route.route_geometry[closest_index:])
                
                if len(remaining_points) > 1:
                    # Calculate the remaining distance in meters
                    remaining_line = LineString(remaining_points)
                    remaining_distance = remaining_line.length
                    
                    # Calculate the estimated time to travel the remaining distance
                    # Speed is in km/h, convert to m/s
                    speed_m_s = current_location.speed * 1000 / 3600
                    if speed_m_s > 0:
                        remaining_time_seconds = remaining_distance / speed_m_s
                        
                        # Add the remaining time to the current time
                        return timezone.now() + datetime.timedelta(seconds=remaining_time_seconds)
            
            # If we couldn't calculate a new ETA, return the original estimate
            return route.estimated_arrival
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating ETA for delivery {self.id}: {str(e)}")
            return self.estimated_delivery_time
    
    
    
    
    def generate_unique_delivery_number(self):
        """
        Generate a unique delivery number.
        
        This method attempts to create a unique 5-digit delivery number
        by incrementing the last used number. It will retry up to 5 times
        in case of conflicts.
        
        Raises:
            IntegrityError: If unable to generate a unique number after max retries
        """
        if not self.number:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        last_delivery = (
                            Delivery.objects.select_for_update()
                            .order_by("-number")
                            .first()
                        )
                        if last_delivery and last_delivery.number:
                            try:
                                last_number = int(last_delivery.number)
                            except ValueError:
                                last_number = 0
                        else:
                            last_number = 0
                        new_number = last_number + 1
                        self.number = f"{new_number:05d}"
                        break
                except IntegrityError:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise IntegrityError(
                            "It was not possible to generate a unique delivery number after several attempts."
                        )
                        
    def save(self, *args, **kwargs):
        """
        Override the default save method to generate a unique delivery number.
        
        This method will be called when saving the Delivery instance.
        """
        self.generate_unique_delivery_number()
        super().save(*args, **kwargs)

class DeliveryItems(BaseModel):
    """
    Represents items in a delivery with quantities distributed by floor.
    
    This model tracks the quantity of products to be delivered to different floors
    of a building and automatically calculates the total.
    
    Attributes:
        delivery (ForeignKey): Reference to the Delivery
        product (ForeignKey): Reference to the Product being delivered
        total (PositiveIntegerField): Total quantity (automatically calculated)
    """
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    basement = models.PositiveIntegerField(default=0)
    first_floor = models.PositiveIntegerField(default=0)
    second_floor = models.PositiveIntegerField(default=0)
    third_floor = models.PositiveIntegerField(default=0)
    fourth_floor = models.PositiveIntegerField(default=0)
    attic = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Delivery Item'
        verbose_name_plural = 'Delivery Items'
        ordering = ['-created_at']
    
    def sum_total(self):
        """Calculate the total quantity across all floors."""
        return (
            self.basement +
            self.first_floor +
            self.second_floor +
            self.third_floor +
            self.fourth_floor +
            self.attic
        )
    
    def save(self, *args, **kwargs):
        """
        Override the default save method to calculate the total quantity.
        
        This method will be called when saving the DeliveryItems instance.
        """
        if self.total != self.sum_total():
            self.total = self.sum_total()
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return f'{self.product} - Total: {self.total} units'
    