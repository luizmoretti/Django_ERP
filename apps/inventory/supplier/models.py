from django.db import models
from basemodels.models import BaseAddressWithBaseModel

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