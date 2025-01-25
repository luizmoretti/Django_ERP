from django.db import models
from apps.companies.hr.models import Employeer
from uuid import uuid4
from apps.companies.models import Companie
from core.constants.choices import COUNTRY_CHOICES
from apps.companies.employeers.models import Employeer

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    companie = models.ForeignKey(Companie, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_companie')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey(Employeer, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by')
    updated_by = models.ForeignKey(Employeer, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by')
    
    class Meta:
        abstract = True
        
        
class BaseAddressWithBaseModel(BaseModel):
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default='USA')
    
    class Meta:
        abstract = True