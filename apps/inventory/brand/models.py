from django.db import models
from basemodels.models import BaseModel


class Brand(BaseModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name