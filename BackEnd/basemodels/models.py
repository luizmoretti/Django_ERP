from django.db import models
from uuid import uuid4
from apps.companies.models import Companie
from core.constants.choices import COUNTRY_CHOICES, STATE_CHOICES
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AnonymousUser

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    companie = models.ForeignKey(Companie, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_companie')
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    created_by = models.ForeignKey('employeers.Employeer', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by')
    updated_by = models.ForeignKey('employeers.Employeer', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by')
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        # get the actual user
        user = kwargs.pop('user', None)
        # Auto-populate created_by and updated_by fields based in the employeer that the actual user it's associated with
        if not user or isinstance(user, AnonymousUser):
            from crum import get_current_user
            user = get_current_user()
        
        if user and not isinstance(user, AnonymousUser):
            try:
                # Late import of Employer to avoid circular import
                from apps.companies.employeers.models import Employeer
                
                # Skip employeer association if this is an Employeer instance being created
                if not isinstance(self, Employeer):
                    employeer = Employeer.objects.get(user=user)
                    if not self.created_by: # Only set created_by if it's a new instance
                        self.created_by = employeer
                    self.updated_by = employeer
                    
                    # If the companie is not set, set it based on the companie associated with the employeer
                    if not self.companie and employeer.companie:
                        self.companie = employeer.companie
            except Employeer.DoesNotExist:
                # Only raise error if this is not an Employeer instance being created
                if not isinstance(self, Employeer):
                    raise ValidationError('User does not exist or is not associated with an employee')
            
        super().save(*args, **kwargs)
            
        
class BaseAddressWithBaseModel(BaseModel):
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default='USA')
    
    class Meta:
        abstract = True