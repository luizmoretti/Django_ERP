from django.db import models
from basemodels.models import BaseModel

# Create your models here.
class Category(BaseModel):
    """Category
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
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['-created_at']

    def __str__(self):
        return self.name