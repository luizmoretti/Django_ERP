from django.db import models, transaction
from django.core.exceptions import ValidationError
from basemodels.models import BaseModel
from ..product.models import Product
from core.cache import cache_method_result, invalidate_cache_key, get_cache_key

class Warehouse(BaseModel):
    """
    Fields:
        name: str
        limit: int: The maximum quantity of the product that warehouse can hold
        quantity: int: The current quantity of the product that warehouse has
        product: ForeignKey to Product
        
    Meta:
        verbose_name: str
        verbose_name_plural: str
        ordering: list
        
    Inheritance:
        BaseModel{
            id: UUIDField
            companie: ForeignKey to Companie
            created_at: DateTimeField
            updated_at: DateTimeField
            created_by: ForeignKey to Employeer
            updated_by: ForeignKey to Employeer
        }
    """
    name = models.CharField(max_length=100, blank=True, null=True)
    limit = models.BigIntegerField(default=0, blank=True, null=True, help_text='The maximum quantity of the product that warehouse can hold')
    quantity = models.BigIntegerField(default=0, blank=True, null=True, help_text='The current quantity of the product that warehouse has')
    
    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def get_total_quantity(self):
        """Get total quantity of all products in warehouse"""
        return WarehouseProduct.objects.filter(
            warehouse=self
        ).aggregate(
            total=models.Sum('current_quantity')
        )['total'] or 0
    
    def update_total_quantity(self):
        """Recalculate total quantity and update cache"""
        # First invalidate the cache
        invalidate_cache_key(get_cache_key('warehouse', id=self.id), cache_alias='default')
        invalidate_cache_key(f'warehouse_total_quantity:{self.__class__.__name__}:{self.id}', cache_alias='default')
        
        # Then get the fresh total
        total = WarehouseProduct.objects.filter(
            warehouse=self
        ).aggregate(
            total=models.Sum('current_quantity')
        )['total'] or 0
        
        # Update the quantity
        self.quantity = total
        self.save()
    
    def get_formatted_address(self):
        """
        Returns a formatted address string from the company associated with this warehouse.
        This is used for delivery routing services like Google Maps.
        
        Returns:
            str: Formatted address string in the format "address, city, state zip_code, country"
                or empty string if no company is associated or company has no address.
        """
        if not self.companie:
            return ""
            
        address_parts = []
        
        if self.companie.address:
            address_parts.append(self.companie.address)
        
        city_state = []
        if self.companie.city:
            city_state.append(self.companie.city)
        
        if self.companie.state:
            city_state.append(self.companie.state)
            
        if city_state:
            address_parts.append(", ".join(city_state))
        
        if self.companie.zip_code:
            address_parts.append(self.companie.zip_code)
            
        if self.companie.country:
            address_parts.append(self.companie.country)
            
        return ", ".join(filter(None, address_parts))
    
    def clean(self):
        """Validate warehouse limit against current quantity"""
        super().clean()
        if self.limit > 0 and self.quantity > self.limit:
            raise ValidationError(f"Warehouse {self.name} exceeds capacity: {self.quantity}/{self.limit}")
    
    def save(self, *args, **kwargs):
        """Save with validation and cache invalidation"""
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Invalidate warehouse caches
        invalidate_cache_key(get_cache_key('warehouse', id=self.id), cache_alias='default')
        invalidate_cache_key('warehouse_list:GET:/api/v1/warehouse/', cache_alias='default')
        invalidate_cache_key(f'warehouse_detail:GET:/api/v1/warehouse/{self.id}/', cache_alias='default')
        
class WarehouseProduct(BaseModel):
    """
    Fields:
        warehouse: ForeignKey to Warehouse
        product: ForeignKey to Product
        current_quantity: int: The current quantity of this product in the warehouse
    
    Meta:
        verbose_name: str
        verbose_name_plural: str
        ordering: list
        
    Inheritance:
        BaseModel{
            id: UUIDField
            companie: ForeignKey to Companie
            created_at: DateTimeField
            updated_at: DateTimeField
            created_by: ForeignKey to Employeer
            updated_by: ForeignKey to Employeer
        }
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_warehouses')
    current_quantity = models.BigIntegerField(default=0, blank=True, null=True, help_text='The current quantity of this product in the warehouse')
    
    class Meta:
        verbose_name = 'Warehouse Product'
        verbose_name_plural = 'Warehouse Products'
        ordering = ['warehouse', 'product']
        unique_together = ('warehouse', 'product')
        
    def __str__(self):
        return f"{self.warehouse.name} - {self.product.name}: {self.current_quantity}"
        
    def clean(self):
        """Validate warehouse product quantity"""
        super().clean()
        if self.current_quantity < 0:
            raise ValidationError(f"Product {self.product.name} quantity cannot be negative in warehouse {self.warehouse.name}")
            
        if self.warehouse.limit > 0:
            # Calculate total excluding this product's current quantity
            other_products_total = (
                WarehouseProduct.objects.filter(warehouse=self.warehouse)
                .exclude(pk=self.pk)
                .aggregate(total=models.Sum('current_quantity'))['total'] or 0
            )
            
            # Add this product's new quantity
            total = other_products_total + self.current_quantity
            
            if total > self.warehouse.limit:
                raise ValidationError(
                    f"Adding {self.current_quantity} of {self.product.name} would exceed "
                    f"warehouse {self.warehouse.name} capacity. "
                    f"Current total: {other_products_total}, "
                    f"New total would be: {total}, "
                    f"Limit: {self.warehouse.limit}"
                )
    
    def save(self, *args, **kwargs):
        """Save with validation and cache invalidation"""
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Invalidate warehouse caches
            invalidate_cache_key(get_cache_key('warehouse', id=self.warehouse.id), cache_alias='default')
            invalidate_cache_key(f'warehouse_total_quantity:{self.warehouse.__class__.__name__}:{self.warehouse.id}', cache_alias='default')
            invalidate_cache_key('warehouse_list:GET:/api/v1/warehouse/', cache_alias='default')
            invalidate_cache_key(f'warehouse_detail:GET:/api/v1/warehouse/{self.warehouse.id}/', cache_alias='default')
            
            # Update warehouse total quantity
            self.warehouse.update_total_quantity()