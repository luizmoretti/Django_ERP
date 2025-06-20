from django.db import models
from ..warehouse.models import Warehouse
from basemodels.models import BaseModel
from ..product.models import Product
from core.constants.choices import MOVEMENTS_STATUS_CHOICES

class Transfer(BaseModel):
    """Transfer model
    
    Fields:
        origin: ForeignKey to Warehouse : The warehouse of the transfer
        destiny: ForeignKey to Warehouse : The warehouse of the transfer
        
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
    origin = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_origin', help_text='The warehouse of the transfer')
    destiny = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_destiny', help_text='The warehouse of the transfer')

    status = models.CharField(
        max_length=20,
        choices=MOVEMENTS_STATUS_CHOICES,
        default='pending',
        help_text='Current status of the transfer'
    )

    rejection_reason = models.TextField(
        null=True,
        blank=True,
        help_text='Reason for rejection if transfer was rejected'
    )
    
    
    
    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'
        ordering = ['-created_at']
        
    def __str__(self):
        return str(self.id)
    
    @property
    def type(self) -> str:
        return "Transfer"
    
class TransferItems(BaseModel):
    """Transfer Items model is responsible for storing the each product that is part of a transfer
    
    Fields:
        transfer: ForeignKey to Transfer : id of the transfer the item is part of
        product: ForeignKey to Product : the products that are coming into stock
        quantity: int : The quantity of this product coming in
        
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
    transfer = models.ForeignKey(Transfer, on_delete=models.SET_NULL, null=True, blank=True, related_name='items', help_text='id of the transfer the item is part of')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transfer_items', help_text='the products that are coming into stock')
    quantity = models.PositiveIntegerField(default=0, help_text='The quantity of that will be transfered')
    
    class Meta:
        verbose_name = 'Transfer Item'
        verbose_name_plural = 'Transfer Items'
        ordering = ['-created_at']