from django.db import models
from ..product.models import Product
from ..warehouse.models import Warehouse
from basemodels.models import BaseModel
from ..supplier.models import Supplier
from core.constants.choices import MOVEMENTS_STATUS_CHOICES

class Inflow(BaseModel):
    """Inflows
    Fields:
        origin: ForeignKey to Supplier : The supplier of the inflow
        destiny: ForeignKey to Warehouse : The warehouse of the inflow
        
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
    origin = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='inflows_origin', help_text='The supplier of the inflow')
    destiny = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='inflows_destiny', help_text='The warehouse of the inflow')
    status = models.CharField(
        max_length=20,
        choices=MOVEMENTS_STATUS_CHOICES,
        default='pending',
        help_text='Current status of the inflow'
    )
    
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        help_text='Reason for rejection if inflow was rejected'
    )
    
    
    class Meta:
        verbose_name = 'Inflow'
        verbose_name_plural = 'Inflows'
        ordering = ['-created_at']
        permissions = [
            ("can_approve_inflow", "Can approve inflow"),
            ("can_reject_inflow", "Can reject inflow"),
            ("can_generate_inflow_reports", "Can generate inflow reports")
        ]
        
    def __str__(self):
        return self.origin.name + ' -> ' + self.destiny.name
    
    
    @property
    def type(self):
        return "Entry"
    
    
class InflowItems(BaseModel):
    """ Inflow Items models is responsible for storing the each product that is part of an inflow
    Fields:
        inflow: ForeignKey to Inflow : id of the inflow the item is part of
        product: ForeignKey to Product : the products that are coming into stock
        quantity: int : The quantity of this product coming in
        
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
    inflow = models.ForeignKey(Inflow, on_delete=models.CASCADE, related_name='items', help_text='id of the inflow the item is part of')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inflow_items', help_text='The products that are coming into stock')
    quantity = models.PositiveIntegerField(default=0, help_text='The quantity of this product coming in')
    
    class Meta:
        verbose_name = 'Inflow Item'
        verbose_name_plural = 'Inflow Items'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.product.name