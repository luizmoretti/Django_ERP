from django.db import models
from ..product.models import Product
from ..warehouse.models import Warehouse
from basemodels.models import BaseModel
from apps.companies.customers.models import Customer
from core.constants.choices import MOVEMENTS_STATUS_CHOICES


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
    
    status = models.CharField(
        max_length=20,
        choices=MOVEMENTS_STATUS_CHOICES,
        default='pending',
        help_text='Current status of the outflow'
    )
    
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        help_text='Reason for rejection if outflow was rejected'
    )
    
    verbose_name = 'Outflow'
    verbose_name_plural = 'Outflows'
    ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.origin.name} -> {self.destiny.full_name}'
    
    @property
    def display_origin_address(self) -> str | None:
        """
        Gets the pickup address from the origin warehouse's company.
        # 
        Returns:
            str | None: The full address if available, None otherwise
    """
        try:
            if self.origin and self.origin.companie:
                # Busca o endereço de coleta através da relação reversa
                pickup_address = self.origin.companie.pick_up_companie_address_companie.first()
                if pickup_address:
                    return pickup_address.full_address
            return None
        except AttributeError:
            return None
        
    @property
    def display_destiny_address(self) -> str | None:
        """
        Gets the destiny address based on the customer's address if available.
        Returns:
            str | None: The full address if available, None otherwise
        """
        try:
            if self.destiny:
                project_address = self.destiny.customer_project_address.first()
                if project_address:
                    return f'{project_address.address}, {project_address.city}, {project_address.state}, {project_address.zip_code}, {project_address.country}'
            return f'{self.destiny.address}, {self.destiny.city}, {self.destiny.state}, {self.destiny.zip_code}, {self.destiny.country}'
        except AttributeError:
            return "Destiny not setted. Please set the destiny customer first."
            
    
class OutflowItems(BaseModel):
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
    outflow = models.ForeignKey(Outflow, on_delete=models.CASCADE, related_name='items', help_text='id of the outflow the item is part of')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='outflow_items', help_text='the products that are going out of the warehouse')
    quantity = models.PositiveIntegerField(default=0, help_text='The quantity of that will be transfered')
    
    verbose_name = 'Outflow Item'
    verbose_name_plural = 'Outflow Items'
    ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.outflow.origin.name} -> {self.outflow.destiny.full_name} - {self.product.name} - {self.quantity}'