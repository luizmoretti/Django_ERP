from django.db import models
from apps.accounts.models import NormalUser
from apps.companies.models import Companie
from uuid import uuid4

class Employeer(models.Model):
    """
    Employee model representing company staff members.
    
    This model stores employee information and manages relationships with
    user accounts and companies. It includes personal details, contact
    information, and automatic data management features.
    
    Attributes:
        id (UUIDField): Primary key using UUID4
        user (OneToOneField): Associated user account
        first_name (CharField): Employee's first name
        last_name (CharField): Employee's last name
        age (PositiveIntegerField): Calculated from date_of_birth
        date_of_birth (DateField): Birth date for age calculation
        email (EmailField): Unique contact email
        phone (CharField): Contact phone number
        address (CharField): Physical address
        city (CharField): City location
        zip_code (CharField): Postal/ZIP code
        created_at (DateTimeField): Timestamp of record creation
        updated_at (DateTimeField): Timestamp of last update
        created_by (ForeignKey): User who created the record
        updated_by (ForeignKey): User who last updated the record
        companie (ForeignKey): Associated company
    
    Relationships:
        - One-to-One with NormalUser through user field
        - Many-to-one with Companie through companie field
        - Created by one NormalUser (many-to-one through created_by)
        - Updated by one NormalUser (many-to-one through updated_by)
    
    Properties:
        default_contact: Returns a dictionary with email and phone
        
    Methods:
        calculate_age: Computes age from date_of_birth
        get_user_full_name: Retrieves full name from associated user
        auto_insert_user: Sets created_by and updated_by fields
        save: Overridden to handle automatic field population
    
    Note:
        The save method automatically:
        - Calculates age if not provided
        - Sets name from user if not provided
        - Sets email from user if not provided
        - Sets created_by and updated_by fields
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    user = models.OneToOneField(
        NormalUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employeer_user'
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        NormalUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employeer_created_by'
    )
    updated_by = models.ForeignKey(
        NormalUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employeer_updated_by'
    )
    companie = models.ForeignKey(
        Companie,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employeer_companie'
    )
    
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['first_name', 'last_name']
    
    def __str__(self) -> str:
        """
        Returns string representation of the employee.
        
        Returns:
            str: Employee's full name
        """
        return f'{self.first_name} {self.last_name}'
    
    @property
    def default_contact(self) -> dict:
        """
        Returns default contact information.
        
        Returns:
            dict: Dictionary containing email and phone
        """
        return {'Email': self.email, 'Phone': self.phone}
    
    def calculate_age(self) -> int:
        """
        Calculates age based on date of birth.
        
        Returns:
            int: Calculated age, or None if date_of_birth not set
        """
        if self.date_of_birth:
            import datetime
            today = datetime.date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def get_user_full_name(self) -> tuple:
        """
        Retrieves full name from associated user.
        
        Returns:
            tuple: (first_name, last_name) from associated user
        """
        if self.user:
            return self.user.first_name, self.user.last_name
        return None, None
    
    def get_full_name(self) -> str:
        """
        Returns full name of the employee.
        
        Returns:
            str: Employee's full name
        """
        return f"{self.first_name} {self.last_name}"
    
    def auto_insert_user(self) -> None:
        """
        Automatically sets created_by and updated_by fields.
        
        Sets both fields to the associated user if not already set.
        """
        if self.user:
            if not self.created_by:
                self.created_by = self.user
            if not self.updated_by:
                self.updated_by = self.user
    
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
        if self.date_of_birth:
            self.age = self.calculate_age()
        
        if (not self.first_name or not self.last_name) and self.user:
            self.first_name, self.last_name = self.get_user_full_name()
            
        if not self.email and self.user:
            self.email = self.user.username
            
        self.auto_insert_user()
        super().save(*args, **kwargs)