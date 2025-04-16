from django.db import models
from django.conf import settings
from basemodels.models import BaseAddressWithBaseModel
from core.constants.choices import PAYROLL_CHOICES, PAYMENT_CHOICES

class Employeer(BaseAddressWithBaseModel):
    """
    Employee model representing company staff members.
    
    This model stores employee information and manages relationships with
    user accounts and companies. It includes personal details, contact
    information, and automatic data management features.
    
    Fields:
        user (OneToOneField): Associated user account
        name (CharField): Employee's name
        date_of_birth (DateField): Birth date for age calculation
        age (PositiveIntegerField): Calculated from date_of_birth
        hire_date (DateField): Date of employment
        termination_date (DateField): Date of termination (if applicable)
        payroll_schedule (CharField): Payroll schedule
        payment_type (CharField): Payment type
        rate (DecimalField): Hourly rate or monthly salary
    
    Inherits:
        BaseAddressWithBaseModel{
            id: UUIDField : Inherited from BaseModel
            companie: ForeignKey to Companie : Inherited from BaseModel
            
            phone: CharField
            email: EmailField
            address: CharField
            city: CharField
            state: CharField 
            zip_code: CharField
            country: CharField
            
            created_at: DateTimeField : Inherited from BaseModel
            updated_at: DateTimeField : Inherited from BaseModel
            created_by: ForeignKey to Employeer : Inherited from BaseModel
            updated_by: ForeignKey to Employeer : Inherited from BaseModel
        }
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='employeer'
    )
    name = models.CharField(max_length=100, blank=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True, auto_now_add=True)
    termination_date = models.DateField(blank=True, null=True)
    payroll_schedule = models.CharField(max_length=50, choices=PAYROLL_CHOICES, blank=True, null=True)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_CHOICES, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    
    
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def default_contact(self) -> dict:
        """
        Returns default contact information.
        
        Returns:
            dict: Dictionary containing email and phone
        """
        return {'Email': self.email, 'Phone': self.phone}
    
    @property
    def display_name(self) -> str:
        """
        Returns a display name for the employee.
        
        Returns:
            str: Display name
        """
        return f'{self.name}'
    
    def save(self, *args, **kwargs) -> None:
        """
        Overridden save method with automatic field population.
        
        Handles:
        - Age calculation from date_of_birth
        - Name population from associated user
        - Email population from user username
        - Created_by and updated_by fields
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Always recalculate age if date_of_birth is set
            
        if not self.name:
            self.name = self.user.first_name + ' ' + self.user.last_name
            
        if not self.email and self.user:
            self.email = self.user.email
        super().save(*args, **kwargs)