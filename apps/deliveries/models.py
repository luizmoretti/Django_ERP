from django.db import models
from core.constants.choices import DELIVERY_STATUS_CHOICES
from basemodels.models import BaseModel
from apps.inventory.warehouse.models import Warehouse
from ..companies.customers.models import Customer, CustomerProjectAddress
from ..companies.models import PickUpCompanieAddress
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
    # vehicle = models.CharField(
    #     max_length=100, 
    #     choices=DELIVERY_VEHICLE_CHOICES, 
    #     null=True, 
    #     blank=True, 
    #     help_text='The vehicle of the delivery'
    # )
    status = models.CharField(
        max_length=100, 
        choices=DELIVERY_STATUS_CHOICES, 
        null=True, 
        blank=True,
        help_text='The status of the delivery'
    )
    
    pick_up_address = models.ForeignKey(
        PickUpCompanieAddress, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='deliveries_pick_up_address', 
        help_text='The pick up address of the delivery'
    )
    
    delivery_address = models.ForeignKey(
        CustomerProjectAddress, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='deliveries_delivery_address', 
        help_text='The delivery address of the delivery'
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
    