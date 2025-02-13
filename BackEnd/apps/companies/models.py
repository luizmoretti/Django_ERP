from django.db import models
from uuid import uuid4
from core.constants.choices import COMPANIE_TYPE_CHOICES, COUNTRY_CHOICES


class Companie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(choices=COMPANIE_TYPE_CHOICES, max_length=50, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, blank=True, null=True, default='USA')
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey('employeers.Employeer', on_delete=models.SET_NULL, null=True, blank=True, related_name='companie_created_by')
    updated_by = models.ForeignKey('employeers.Employeer', on_delete=models.SET_NULL, null=True, blank=True, related_name='companie_updated_by')
    
    
    class Meta:
        verbose_name = 'Companie'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'[{self.type}] {self.name}'
    

class PickUpCompanieAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    companie = models.ForeignKey(Companie, on_delete=models.SET_NULL, null=True, blank=True, related_name='companie_pick_up_address')
    full_address = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    
    class Meta:
        verbose_name = 'Pick Up Companie Address'
        verbose_name_plural = 'Pick Up Companie Addresses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.full_address}'
    
    def get_full_address(self):
        return f'{self.companie.address}, {self.companie.city}, {self.companie.state} {self.companie.zip_code}'
    
    def save(self, *args, **kwargs):
        if not self.full_address:
            self.full_address = self.get_full_address()
        elif self.full_address != self.get_full_address():
            self.full_address = self.get_full_address()
        super().save(*args, **kwargs)
    
    
    