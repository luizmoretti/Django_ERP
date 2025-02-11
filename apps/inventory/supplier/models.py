from django.db import models
from basemodels.models import BaseAddressWithBaseModel, BaseModel
from ..product.models import Product

class Supplier(BaseAddressWithBaseModel):
    """Supplier
    Fields:
        name : str
        tax_number : str : The tax number of the supplier
        
    inheritance:
        BaseAddressWithBaseModel{
            id: UUIDField : Inherited from BaseModel
            companie: ForeignKey to Companie : Inherited from BaseModel
            
            phone: CharField
            email: EmailField
            address: CharField
            city: CharField
            state: CharField 
            zip_code: CharField
            country: CharField
            
            created_at: DateTimeField : Inherited from BaseModel
            updated_at: DateTimeField : Inherited from BaseModel
            created_by: ForeignKey to Employeer : Inherited from BaseModel
            updated_by: ForeignKey to Employeer : Inherited from BaseModel
        }
    
    """
    name = models.CharField(max_length=155, blank=True, null=True)
    tax_number = models.CharField(max_length=50, blank=True, null=True, help_text='The tax number of the supplier')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['-created_at']
        
    @property
    def full_address_display(self):
        return f"{self.address}, {self.city} - {self.zip_code}, {self.country}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class SupplierProductPrice(BaseModel):
    """Track historical and current prices for products by supplier
    
    Fields:
        supplier: ForeignKey to Supplier - The supplier
        product: ForeignKey to Product - The product
        unit_price: DecimalField - Current price per unit
        last_purchase_date: DateField - Date of last purchase
        is_current: BooleanField - Whether this is the current price
        
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
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='product_prices',
        help_text='The supplier'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='supplier_prices',
        help_text='The product'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Current price per unit'
    )
    last_purchase_date = models.DateField(
        auto_now=True,
        help_text='Date of last purchase'
    )
    is_current = models.BooleanField(
        default=True,
        help_text='Whether this is the current price',
        db_index=True  # Adicionar índice para melhor performance em queries
    )
    
    class Meta:
        verbose_name = 'Supplier Product Price'
        verbose_name_plural = 'Supplier Product Prices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['supplier', 'product', 'is_current'])  # Índice composto para melhor performance
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.supplier.name}: ${self.unit_price}"