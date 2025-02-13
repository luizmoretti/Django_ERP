import logging
from typing import Optional, List, Union
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .models import Customer, CustomerProjectAddress, CustomerBillingAddress

logger = logging.getLogger(__name__)

class CustomerService:
    @staticmethod
    def get_customers(**kwargs) -> Union[Optional[Customer], List[Customer]]:
        """
        Flexible method to retrieve customer(s) based on provided criteria.
        
        Args:
            **kwargs: Keyword arguments for filtering customers
                Supported filters:
                - id (str): Customer UUID
                - first_name (str): Customer's first name
                - last_name (str): Customer's last name
                - company_id (str): UUID of the company
                
        Returns:
            Union[Optional[Customer], List[Customer]]: 
            - Single Customer instance if searching by id or full name
            - List of Customer instances if searching by company_id
            - None if no match found for single customer search
        """
        try:
            # Case 1: Search by customer ID
            if 'id' in kwargs:
                customer = Customer.objects.get(id=kwargs['id'])
                logger.info(f'[SERVICES] Customer {customer.full_name()} retrieved by id {kwargs["id"]}')
                return customer
                
            # Case 2: Search by full name
            elif all(key in kwargs for key in ['first_name', 'last_name']):
                customer = Customer.objects.get(
                    first_name=kwargs['first_name'],
                    last_name=kwargs['last_name']
                )
                logger.info(f'[SERVICES] Customer {customer.full_name()} retrieved')
                return customer
                
            # Case 3: Search by company ID
            elif 'company_id' in kwargs:
                customers = Customer.objects.filter(companie_id=kwargs['company_id'])
                logger.info(f'[SERVICES] Found {customers.count()} customers for company {kwargs["company_id"]}')
                return list(customers)
                
            else:
                logger.error('[SERVICES] Invalid search criteria provided')
                raise ValueError('[SERVICES] Invalid search criteria. Must provide either id, full name, or company_id')
                
        except ObjectDoesNotExist:
            search_criteria = ' '.join(f'{k}={v}' for k, v in kwargs.items())
            logger.error(f'[SERVICES] Customer not found with criteria: {search_criteria}')
            return None if 'company_id' not in kwargs else []
    
    @staticmethod
    def create_customer(customer_data: dict) -> Optional[Customer]:
        """
        Create a new customer with validation.
        
        Args:
            customer_data (dict): Dictionary containing customer data
            
        Returns:
            Optional[Customer]: Created customer instance if successful, None if validation fails
            
        Raises:
            ValidationError: If required fields are missing or invalid
        """
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in customer_data or not customer_data[field]:
                    raise ValidationError(f'Missing required field: {field}')
            
            customer = Customer.objects.create(**customer_data)
            logger.info(f'Customer {customer.full_name()} created successfully')
            
            # Create default addresses if needed
            if not customer.another_billing_address:
                CustomerBillingAddress.objects.create(customer=customer)
            
            if not customer.another_shipping_address:
                CustomerProjectAddress.objects.create(customer=customer)
                
            return customer
            
        except ValidationError as e:
            logger.error(f'Validation error creating customer: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'Error creating customer: {str(e)}')
            return None