from django.db import models
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from uuid import uuid4
from core.constants.choices import COUNTRY_CHOICES
from basemodels.models import BaseAddressWithBaseModel
import logging

logger = logging.getLogger(__name__)

# Create your models here.
class Customer(BaseAddressWithBaseModel):
    """
    Customer model representing client entities in the system.
    
    This model stores essential customer information including contact details
    and relationships with companies and employees who manage the customer
    record.
    
    Attributes:
        id (UUIDField): Primary key using UUID4
        name (CharField): Customer's name or business name
        address (CharField): Physical address (max length: 200)
        city (CharField): City location
        state (CharField): State location
        zip_code (CharField): Postal/ZIP code
        country (CharField): Country location, defaults to 'USA'
        phone (CharField): Contact phone number
        email (EmailField): Contact email address
        is_active (BooleanField): Indicates if the customer is active, defaults to True
        companie (ForeignKey): Associated company
        created_by (ForeignKey): Employee who created the record
        updated_by (ForeignKey): Employee who last updated the record
        created_at (DateTimeField): Timestamp of record creation
        updated_at (DateTimeField): Timestamp of last update
    
    Relationships:
        - Belongs to one Companie (many-to-one through companie field)
        - Created by one Employeer (many-to-one through created_by field)
        - Updated by one Employeer (many-to-one through updated_by field)
    
    Note:
        All foreign key relationships use SET_NULL on deletion to maintain
        data integrity and history.
        
    Inherits:
        BaseAddressWithBaseModel{
            id: UUIDField : Inherited from BaseModel
            address: CharField
            city: CharField 
            state: CharField
            zip_code: CharField 
            country: CharField 
            phone: CharField 
            email: EmailField 
            created_at: DateTimeField : Inherited from BaseModel
            updated_at: DateTimeField : Inherited from BaseModel
            created_by: ForeignKey to Employeer : Inherited from BaseModel
            updated_by: ForeignKey to Employeer : Inherited from BaseModel
        }
    """
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    another_billing_address = models.BooleanField(default=False)
    another_shipping_address = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']
    
    def full_name(self) -> str:
        """
        Returns full name of the customer.
        
        Returns:
            str: Customer's full name
        """
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self) -> str:
        """
        Returns string representation of the customer.
        
        Returns:
            str: Customer's name
        """
        return self.full_name()
    
class CustomerProjectAddress(BaseAddressWithBaseModel):
    """
    Customer project address model representing project addresses associated with
    customers.
    
    Attributes:
        customer (ForeignKey): Customer to which the project address is associated
    
    Relationships:
        - Belongs to one Customer (many-to-one through customer field)
    
    Note:
        All foreign key relationships use SET_NULL on deletion to maintain
        data integrity and history.
        
    Inherits:
        BaseAddressWithBaseModel{
            id: UUIDField : Inherited from BaseModel
            address: CharField
            city: CharField 
            state: CharField
            zip_code: CharField 
            country: CharField 
            phone: CharField 
            email: EmailField 
            created_at: DateTimeField : Inherited from BaseModel
            updated_at: DateTimeField : Inherited from BaseModel
            created_by: ForeignKey to Employeer : Inherited from BaseModel
            updated_by: ForeignKey to Employeer : Inherited from BaseModel
        }
    """
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_project_address_customer')
    
    class Meta:
        verbose_name = 'Customer Project Address'
        verbose_name_plural = 'Customer Project Addresses'
        ordering = ['-created_at']
        
    def __str__(self):
        """
        Returns string representation of the customer project address.
        
        Returns:
            str: Customer project address
        """
        return f'{self.address}, {self.city}, {self.state}, {self.zip_code}, {self.country}'
    
    @staticmethod
    def check_another_shipping_address(customer_instance:Customer) -> bool:
        """
        Checks if another shipping address is set.
        
        Returns:
            bool: True if another shipping address is set to True, False otherwise
        """
        return customer_instance.another_shipping_address
    
    def populate_customer_project_address(self, customer_instance:Customer):
        """
        Populates the customer project address fields with the provided customer instance if another shipping address is not set.
        
        
        Args:
            customer_instance (Customer): Customer instance to populate the project address fields from
        """
        if not self.check_another_shipping_address(customer_instance):
            self.address = customer_instance.address
            self.city = customer_instance.city
            self.state = customer_instance.state
            self.zip_code = customer_instance.zip_code
            self.country = customer_instance.country
            self.phone = customer_instance.phone if customer_instance.phone else None
            self.email = customer_instance.email if customer_instance.email else None
        
    def save(self, *args, **kwargs):
        """
        Custom save method to update customer project address if another shipping address is not set.
        """
        self.populate_customer_project_address(self.customer)
        super().save(*args, **kwargs)
        
class CustomerBillingAddress(BaseAddressWithBaseModel):
    """
    Customer billing address model representing billing addresses associated with
    customers.
    
    Attributes:
        customer (ForeignKey): Customer to which the billing address is associated
    
    Relationships:
        - Belongs to one Customer (many-to-one through customer field)
    
    Note:
        All foreign key relationships use SET_NULL on deletion to maintain
        data integrity and history.
        
    Inherits:
        BaseAddressWithBaseModel{
            id: UUIDField : Inherited from BaseModel
            address: CharField
            city: CharField 
            state: CharField
            zip_code: CharField 
            country: CharField 
            phone: CharField 
            email: EmailField 
            created_at: DateTimeField : Inherited from BaseModel
            updated_at: DateTimeField : Inherited from BaseModel
            created_by: ForeignKey to Employeer : Inherited from BaseModel
            updated_by: ForeignKey to Employeer : Inherited from BaseModel
        }
    """
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_billing_address_customer')
    
    
    class Meta:
        verbose_name = 'Customer Billing Address'
        verbose_name_plural = 'Customer Billing Addresses'
        ordering = ['-created_at']
        
    def __str__(self):
        """
        Returns string representation of the customer billing address.
        
        Returns:
            str: Customer billing address
        """
        return f'{self.address}, {self.city}, {self.state}, {self.zip_code}, {self.country}'
    
    @staticmethod
    def check_another_billing_address(customer_instance:Customer) -> bool:
        """
        Checks if another billing address is set.
        
        Returns:
            bool: True if another billing address is set to True, False otherwise
        """
        return customer_instance.another_billing_address
    
    
    def populate_customer_billing_address(self, customer_instance:Customer):
        """
        Populates the customer billing address fields with the provided customer instance if another billing address is not set.
        
        
        Args:
            customer_instance (Customer): Customer instance to populate the billing address fields from
        """
        if not self.check_another_billing_address(customer_instance):
            self.address = customer_instance.address
            self.city = customer_instance.city
            self.state = customer_instance.state
            self.zip_code = customer_instance.zip_code
            self.country = customer_instance.country
            self.phone = customer_instance.phone if customer_instance.phone else None
            self.email = customer_instance.email if customer_instance.email else None
            
    def save(self, *args, **kwargs):
        """
        Custom save method to update customer billing address if another billing address is not set.
        """
        self.populate_customer_billing_address(self.customer)
        super().save(*args, **kwargs)