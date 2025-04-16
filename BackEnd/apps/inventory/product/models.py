from django.db import models
from basemodels.models import BaseModel
from ..categories.models import Category
from ..brand.models import Brand

class Product(BaseModel):
    """Product
    Fields:
        name: str
        description: str : The description of the product
        quantity: int : The total quantity of the product
        brand: ForeignKey to Brand : The brand of the product
        category: ForeignKey to Category : The category of the product

    Meta:
        verbose_name: str
        verbose_name_plural: str
        ordering: list
    """
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True, help_text='The description of the product')
    quantity = models.PositiveIntegerField(default=0, help_text='The total quantity of the product')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', help_text='The brand of the product')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', help_text='The category of the product')
    supplier = models.ForeignKey('supplier.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='products', help_text='The suppliers of the product')
    
    
    # Price fields
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Current price of the product'
    )
    
    # Trash Hold Fields for warehouse low_stock notification
    min_quantity = models.PositiveIntegerField(default=0, help_text='The minimum quantity of the product that should be in stock')
    max_quantity = models.PositiveIntegerField(default=0, help_text='The maximum quantity of the product that should be in stock')
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    
class ProductSku(BaseModel):
    """ProductSku Models is responsible for storing the skus of the products
    Fields:
        product: ForeignKey to Product : The product of the sku
        sku: str : The sku of the product
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus', help_text='The product of the sku')
    sku = models.CharField(max_length=100, blank=True, null=True, help_text='The sku of the product')
    
    class Meta:
        verbose_name = 'Product Sku'
        verbose_name_plural = 'Product Skus'
        ordering = ['-created_at']
        
class ProductInStoreID(BaseModel):
    """ProductSupplierID Models is responsible for storing the supplier ids of the products
    Fields:
        product: ForeignKey to Product : The product of the sku
        supplier: ForeignKey to Supplier : The supplier of the product
        in_store_id: str : The id of the product in the supplier store
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
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='store_ids', help_text='The product of the sku')
    in_store_id = models.CharField(max_length=100, blank=True, null=True, help_text='The id of the product in the supplier store')
