from django.db import models
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from uuid import uuid4
from core.constants.choices import LEAD_STATUS_CHOICES
from basemodels.models import BaseAddressWithBaseModel, BaseModel
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
        another_billing_address (BooleanField): Indicates if the customer has another billing address, defaults to False
        another_shipping_address (BooleanField): Indicates if the customer has another shipping address, defaults to False
        
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
    
    def get_formatted_address(self):
        """
        Returns a formatted address string for this customer.
        This is used for delivery routing services like Google Maps.
        
        Returns:
            str: Formatted address string in the format "address, city, state zip_code, country"
                or empty string if customer has no address information.
        """
        address_parts = []
        
        if self.address:
            address_parts.append(self.address)
        
        city_state = []
        if self.city:
            city_state.append(self.city)
        
        if self.state:
            city_state.append(self.state)
            
        if city_state:
            address_parts.append(", ".join(city_state))
        
        if self.zip_code:
            address_parts.append(self.zip_code)
            
        if self.country:
            address_parts.append(self.country)
            
        return ", ".join(filter(None, address_parts))
    
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
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_address')
    
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
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_address')
    
    
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
        

class CustomerLeads(BaseModel):
    """
    Model to store business lead information collected from Google Local Search.
    
    This model stores potential customer leads gathered from external sources
    like the Google Local Search API. It can be used to track businesses
    that might be contacted for sales or marketing purposes.
    
    Attributes:
        name (CharField): Business name
        address (CharField): Business address
        phone (CharField): Business phone number
        website (CharField): Business website URL
        hours (CharField): Business operating hours
        rating (CharField): Business rating (stored as string to handle "NO RATING FOUND")
        reviews (CharField): Number of reviews (stored as string to handle "NO REVIEWS FOUND")
        category (CharField): Business category or type
        place_id (CharField): Google Maps place ID for future reference
        notes (CharField): Additional notes or observations
        status (CharField): Lead status (e.g., "New", "Contacted", "Converted", "Rejected")
        
    Inherits:
        BaseModel:
            id: UUIDField
            created_at: DateTimeField
            updated_at: DateTimeField
            created_by: ForeignKey to Employeer
            updated_by: ForeignKey to Employeer
            companie: ForeignKey to Companie
    """
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.CharField(max_length=255, blank=True)
    hours = models.CharField(max_length=255, blank=True)
    rating = models.CharField(max_length=50, blank=True)
    reviews = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100, blank=True)
    place_id = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=50, choices=LEAD_STATUS_CHOICES, default="New")
    
    class Meta:
        verbose_name = "Customer Lead"
        verbose_name_plural = "Customer Leads"
        ordering = ['-created_at', 'status']
    
    def __str__(self):
        return f"[{self.status}] {self.name}"