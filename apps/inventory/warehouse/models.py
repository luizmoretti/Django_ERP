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
    
    @cache_method_result(timeout=300, key_prefix='warehouse_total_quantity', cache_alias='default')
    def get_total_quantity(self):
        """Get cached total quantity of all products in warehouse"""
        return WarehouseProduct.objects.filter(
            warehouse=self
        ).aggregate(
            total=models.Sum('current_quantity')
        )['total'] or 0
    
    def update_total_quantity(self):
        """Recalculate total quantity and update cache"""
        total = self.get_total_quantity()
        self.quantity = total
        self.save()
        
        # Invalidate related caches
        invalidate_cache_key(get_cache_key('warehouse', id=self.id), cache_alias='default')
        invalidate_cache_key(f'warehouse_total_quantity:{self.__class__.__name__}:{self.id}', cache_alias='default')
    
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
        verbose_name = 'Product Warehouse'
        verbose_name_plural = 'Product Warehouses'
        ordering = ['-created_at']
    
    def clean(self):
        """Validate warehouse product quantities"""
        super().clean()
        
        # Prevent negative quantities
        if self.current_quantity < 0:
            raise ValidationError("Product quantity cannot be negative")
        
        # Calculate total warehouse quantity including this product
        total_quantity = (
            WarehouseProduct.objects.filter(warehouse=self.warehouse)
            .exclude(pk=self.pk)
            .aggregate(total=models.Sum('current_quantity'))['total'] or 0
        )
        total_quantity += self.current_quantity
        
        # Check warehouse capacity limit
        if self.warehouse.limit > 0 and total_quantity > self.warehouse.limit:
            raise ValidationError(
                f"Operation would exceed warehouse capacity. "
                f"Current: {total_quantity - self.current_quantity}, "
                f"Change: {self.current_quantity}, "
                f"Limit: {self.warehouse.limit}"
            )
    
    def save(self, *args, **kwargs):
        """Save the model with validation and cache invalidation"""
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Invalidate related caches
            warehouse_id = self.warehouse.id
            product_id = self.product.id
            
            invalidate_cache_key(get_cache_key('warehouse', id=warehouse_id), cache_alias='default')
            invalidate_cache_key(get_cache_key('product', id=product_id), cache_alias='default')
            invalidate_cache_key(get_cache_key('inventory', warehouse_id=warehouse_id, product_id=product_id), cache_alias='default')
            invalidate_cache_key(f'warehouse_total_quantity:{self.warehouse.__class__.__name__}:{warehouse_id}', cache_alias='default')
            
            self.warehouse.update_total_quantity()
