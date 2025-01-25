from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
from core.constants.choices import USER_TYPE_CHOICES
from django.utils.translation import gettext_lazy as _

class NormalUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    
    This model represents all users in the system, including employees,
    customers, and suppliers. It includes additional fields for user
    type classification and tracking.
    
    Attributes:
        id (UUIDField): Primary key using UUID4
        password (CharField): Encrypted password string
        email (EmailField): Unique email for user identification
        type (CharField): User classification based on TYPE_CHOICES
        first_name (CharField): User's first name
        last_name (CharField): User's last name
        is_staff (BooleanField): Django admin access flag
        last_login (DateTimeField): Last login timestamp
        date_joined (DateTimeField): Account creation timestamp
        is_active (BooleanField): Account status flag
        img (ImageField): Profile picture
        ip (GenericIPAddressField): Last known IP address
        
    Relationships:
        - groups (ManyToManyField): Custom related name to avoid clashes
        - user_permissions (ManyToManyField): Custom related name to avoid clashes
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES, blank=True, null=True, default='Employee')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    img = models.ImageField(upload_to='users/', blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)

    # Add related_name to resolve the clash
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='normaluser_set',
        related_query_name='normaluser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='normaluser_set',
        related_query_name='normaluser'
    )
    
    
    
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
       ordering = ['-is_active']
        
    @property
    def full_name(self) -> str:
        """
        Returns the user's full name by combining first and last name.
        
        Returns:
            str: Concatenated first_name and last_name with space between
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_ip_on_login(self, request) -> 'NormalUser':
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
        """
        Overrides the default save method to ensure username matches email.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        self.username = self.email
        super().save(*args, **kwargs)