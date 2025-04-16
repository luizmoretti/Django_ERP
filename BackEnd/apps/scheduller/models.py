from django.db import models
from basemodels.models import BaseModel
from django.core.exceptions import ValidationError

class JobsTypeSchedullerRegister(BaseModel):
    """
    Model responsible for creating and managing custom job types for the scheduler system.
    
    This model stores predefined job types that can be assigned to scheduling entries,
    allowing for categorization and organization of scheduled activities.
    
    Attributes:
        name (CharField): Unique name identifier for the job type (max 100 chars)
        
    Inherits:
        BaseModel: Common fields for audit and multi-company support
    """
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = "Jobs Type Scheduller Register"
        verbose_name_plural = "Jobs Type Scheduller Registers"
        
    def __str__(self):
        return self.name
    
class Scheduller(BaseModel):
    """
    Model responsible for scheduling jobs within the system.
    
    This model manages scheduling entries, allowing for the allocation of one or more
    job types to specific times, dates, and locations. Each schedule can have multiple
    associated job types and tracks time boundaries for execution.
    
    Attributes:
        start_time (TimeField): The time when the scheduled job(s) should start
        end_time (TimeField): The time when the scheduled job(s) should end
        date (DateField): The date when the job(s) are scheduled
        jobs (ManyToManyField): The types of jobs associated with this schedule
        location (CharField): Physical or virtual location for the scheduled job(s)
        
    Inherits:
        BaseModel: Common fields for audit and multi-company support
    """
    start_time = models.TimeField(blank=True, null=True, auto_now_add=True)
    end_time = models.TimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    jobs = models.ManyToManyField(JobsTypeSchedullerRegister, related_name="scheduller", blank=True)
    location = models.CharField(max_length=250, blank=True, null=True)
    
    
    class Meta:
        verbose_name = "Scheduller"
        verbose_name_plural = "Schedullers"
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.location} | {self.date}'