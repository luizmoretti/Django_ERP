from django.db import models
from basemodels.models import BaseModel
from apps.inventory.product.models import Product
from apps.companies.customers.models import Customer
from apps.vehicle.models import Vehicle
from django.db import transaction, IntegrityError

class LoadOrder(BaseModel):
    order_number = models.CharField(max_length=100, blank=True, null=True, help_text='The order number of the load order')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, help_text='The customer that the load order is going to')
    load_to = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, help_text='The vehicle that the load order is going to')
    load_date = models.DateField(null=True, blank=True, help_text='The date of the load order')
    
    class Meta:
        verbose_name = 'Load Order'
        verbose_name_plural = 'Load Orders'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.order_number
    
    
    def generate_unique_order_number(self):
        """
        Generate a unique order number.
        
        This method attempts to create a unique 5-digit order number
        by incrementing the last used number. It will retry up to 5 times
        in case of conflicts.
        
        Raises:
            IntegrityError: If unable to generate a unique number after max retries
        """
        if not self.order_number:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        last_load_order = (
                            LoadOrder.objects.select_for_update()
                            .order_by("-order_number")
                            .first()
                        )
                        if last_load_order and last_load_order.order_number:
                            try:
                                last_number = int(last_load_order.order_number)
                            except ValueError:
                                last_number = 0
                        else:
                            last_number = 0
                        new_number = last_number + 1
                        self.order_number = f"{new_number:05d}"
                        return self.order_number
                except IntegrityError:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise IntegrityError(
                            "It was not possible to generate a unique delivery number after several attempts."
                        )
    
    def save(self, *args, **kwargs):
        """
        Override the default save method to generate a unique order number.
        
        This method will be called when saving the LoadOrder instance.
        """
        self.generate_unique_order_number()
        super().save(*args, **kwargs)
        
    
    
    
class LoadOrderItem(BaseModel):
    load_order = models.ForeignKey(LoadOrder, on_delete=models.CASCADE, related_name='items', help_text='The load order that the item is part of')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='load_order_product', help_text='The product that the item is')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text='The quantity of the product that the item is')
    
    class Meta:
        verbose_name = 'Load Order Item'
        verbose_name_plural = 'Load Order Items'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.load_order.order_number
    