from django.db import models
from basemodels.models import BaseModel


class Brand(BaseModel):
    """Brand
    Fields:
        name: str
        
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
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name