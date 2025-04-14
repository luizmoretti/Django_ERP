from django.db import models
from basemodels.models import BaseModel
from django.core.exceptions import ValidationError

class JobsTypeSchedullerRegister(BaseModel):
    """ Model responsible for create custom jobs names"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = "Jobs Type Scheduller Register"
        verbose_name_plural = "Jobs Type Scheduller Registers"
        
    def __str__(self):
        return self.name
    
class Scheduller(BaseModel):
    """ Model responsable for schedule one job"""
    start_time = models.TimeField(blank=True, null=True, auto_now_add=True)
    end_time = models.TimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    jobs = models.ManyToManyField(JobsTypeSchedullerRegister, related_name="scheduller", null=True, blank=True, on_delete=models.CASCADE)
    location = models.CharField(max_length=250, blank=True, null=True)
    
    
    class Meta:
        verbose_name = "Scheduller"
        verbose_name_plural = "Schedullers"
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.location} | {self.date}'
    
    