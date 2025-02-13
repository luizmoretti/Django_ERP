from django.db import models
from core.constants.choices import DELIVERY_STATUS_CHOICES
from .vehicles.models import Vehicle
from basemodels.models import BaseModel
from apps.inventory.product.models import Product
from apps.inventory.warehouse.models import Warehouse
from ..companies.customers.models import Customer 
from django.core.exceptions import ValidationError
from django.db.models import Sum
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
        null=True,
        blank=True,
        help_text='The status of the delivery'
    )
    
    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Delivery {self.number} from {self.origin} to {self.destiny}'
    
    
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
    