from django.db import models
from uuid import uuid4
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, default='USA')
    complete_address = models.TextField(blank=True, null=True)
    tax_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(Employeer, blank=True, null=True, on_delete=models.SET_NULL, related_name='supplier_created_by')
    updated_by = models.ForeignKey(Employeer, blank=True, null=True, on_delete=models.SET_NULL, related_name='supplier_updated_by')
    companie = models.ForeignKey(Companie, blank=True, null=True, on_delete=models.SET_NULL, related_name='supplier_companie')
    
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['-created_at']
        
    def get_complete_address(self):
        return f"{self.address}, {self.city} - {self.zip_code}, {self.country}"
    
    def save(self, *args, **kwargs):
        # save the complete address when all address fields are filled
        if self.address and self.city and self.zip_code and self.country:
            self.complete_address = self.get_complete_address()
        super().save(*args, **kwargs)