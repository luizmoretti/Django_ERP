from django.db import models
from ..product.models import Product
from ..warehouse.models import Warehouse
from basemodels.models import BaseModel
from apps.companies.customers.models import Customer


class Outflow(BaseModel):
    """
    Fields:
        origin: ForeignKey to Warehouse : The warehouse of the outflow
        destiny: ForeignKey to Customer : The customer of the outflow
        product: ForeignKey to Product : The product of the outflow
        quantity: int : The quantity of the product that is being removed from the warehouse
        
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
    origin = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='outflows_origin', help_text='The warehouse of the outflow')
    destiny = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='outflows_destiny', help_text='The customer of the outflow')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='outflows', help_text='The product of the outflow')
    quantity = models.PositiveIntegerField(default=0, help_text='The quantity of the product that is being removed from the warehouse')
    
    verbose_name = 'Outflow'
    verbose_name_plural = 'Outflows'
    ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.origin.name} - {self.destiny.name} - {self.product.name} - {self.quantity}'
    
class OutflowItems(models.Model):
    """ Outflow Items model is responsible for storing the each product that is part of a outflow
    fields:
        outflow: ForeignKey to Outflow : id of the outflow the item is part of
        product: ForeignKey to Product : the products that are going out of the warehouse
        quantity: int : The quantity of this product going out of the warehouse
        
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
    outflow = models.ForeignKey(Outflow, on_delete=models.CASCADE, related_name='outflow_items', help_text='id of the outflow the item is part of')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='outflow_items', help_text='the products that are going out of the warehouse')
    quantity = models.PositiveIntegerField(default=0, help_text='The quantity of that will be transfered')
    
    verbose_name = 'Outflow Item'
    verbose_name_plural = 'Outflow Items'
    ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.outflow.origin.name} -> {self.outflow.destiny.name} - {self.product.name} - {self.quantity}'