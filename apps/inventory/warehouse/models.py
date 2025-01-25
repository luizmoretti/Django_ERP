from django.db import models
from basemodels.models import BaseModel
from ..product.models import Product

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
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
    
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
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='product_warehouses')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_warehouses')
    current_quantity = models.BigIntegerField(default=0, blank=True, null=True, help_text='The current quantity of this product in the warehouse')
    
    class Meta:
        verbose_name = 'Product Warehouse'
        verbose_name_plural = 'Product Warehouses'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.warehouse.name + ' - ' + self.product.name
