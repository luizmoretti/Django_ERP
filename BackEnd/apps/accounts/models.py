from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from uuid import uuid4
from core.constants.choices import USER_TYPE_CHOICES
from django.utils.translation import gettext
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is mandatory')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('The superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('The superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)





class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    
    This model represents all users in the system, including employees,
    customers, and suppliers. It includes additional fields for user
    type classification and tracking.
    
    Attributes:
        id (UUIDField): Primary key using UUID4
        user_type (CharField): User classification based on TYPE_CHOICES
        ip (GenericIPAddressField): Last known IP address
        
    Note:
        All other fields are inherited from AbstractUser:
        - username
        - email
        - first_name
        - last_name
        - password
        - is_staff
        - is_active
        - is_superuser
        - last_login
        - date_joined
        - groups
        - user_permissions
    """
    username = None  # Remove username field
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES, blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    email = models.EmailField(unique=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = gettext('User')
        verbose_name_plural = gettext('Users')
        swappable = 'AUTH_USER_MODEL'
        
    def __str__(self):
        return self.email
    
    def clean(self):
        super().clean()
        self.email = self.email.lower()
    
    def get_ip_on_login(self, request) -> 'User':
        """
        Updates the user's IP address based on the login request.
        
        Args:
            request: The HTTP request object containing IP information
            
        Returns:
            NormalUser: Returns self for method chaining
            
        Note:
            Handles both direct IP and forwarded IP (behind proxy)
        """
        if request and hasattr(request, 'META'):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                self.ip = x_forwarded_for.split(',')[0]
            else:
                self.ip = request.META.get('REMOTE_ADDR')
            self.save(update_fields=['ip'])
        return self
    
    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)