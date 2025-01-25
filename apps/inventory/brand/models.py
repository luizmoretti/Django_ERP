from django.db import models
from apps.companies.models import Companie
from apps.companies.employeers.models import Employeer
from uuid import uuid4

class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    companie = models.ForeignKey(Companie, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand_companie')
    created_by = models.ForeignKey(Employeer, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand_created_by')
    updated_by = models.ForeignKey(Employeer, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name