import logging
from typing import Optional, List, Union
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .models import Customer, CustomerProjectAddress, CustomerBillingAddress, CustomerLeads
from .utils.google_scraper_serpapi import GoogleLocalSearchService
from django.db import transaction
from django.db.models import Q

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
                customers = Customer.objects.filter(company_id=kwargs['company_id'])
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
        
        
class CustomerLeadBusinessValidator:
    """Validator for CustomerLead business rules"""
    
    def validate_company_access(self, data_or_instance, user):
        """Validate that user has access to company resources"""
        if hasattr(data_or_instance, 'company'):
            # Instance case
            if data_or_instance.company != user.employeer.company:
                logger.error(
                    f"[CUSTOMER LEAD VALIDATOR] - User does not have access to company",
                    extra={'user_id': user.id, 'company_id': data_or_instance.company.id}
                )
                raise ValidationError(_("You don't have access to this company's resources"))
        elif isinstance(data_or_instance, dict) and 'company' in data_or_instance:
            # Data dict case with company specified
            if data_or_instance['company'] != user.employeer.company:
                logger.error(
                    f"[CUSTOMER LEAD VALIDATOR] - User does not have access to company",
                    extra={'user_id': user.id, 'company_id': data_or_instance['company'].id}
                )
                raise ValidationError(_("You don't have access to this company's resources"))

    def validate_lead_data(self, data):
        """Validate lead data for creation or update"""
        # Validate required fields
        if not data.get('name'):
            logger.error("[CUSTOMER LEAD VALIDATOR] - Missing required name field")
            raise ValidationError(_("Business name is required"))
        
        # Additional validations can be added here (phone format, website format, etc.)

    def validate_search_query(self, query, location):
        """Validate search query parameters"""
        if not query:
            logger.error("[CUSTOMER LEAD VALIDATOR] - Missing required query parameter")
            raise ValidationError(_("Search query is required"))
        
        # Optional validation for location format, if needed
        return True

    def validate_leads_status_change(self, lead, new_status):
        """Validate that the status change is allowed"""
        current_status = lead.status
        
        # Define allowed status transitions
        # For example: New -> Contacted -> Qualified -> Converted/Rejected
        allowed_transitions = {
            "New": ["Contacted", "Rejected"],
            "Contacted": ["Qualified", "Rejected"],
            "Qualified": ["Converted", "Rejected"],
            "Converted": [],  # Terminal state
            "Rejected": ["New"]  # Can reopen a rejected lead
        }
        
        if new_status not in allowed_transitions.get(current_status, []):
            logger.error(
                f"[CUSTOMER LEAD VALIDATOR] - Invalid status transition: {current_status} -> {new_status}",
                extra={'lead_id': str(lead.id)}
            )
            raise ValidationError(_(f"Cannot change status from '{current_status}' to '{new_status}'"))
        
        return True
    
class CustomerLeadService:
    """Service for managing customer leads"""
    
    def __init__(self):
        self.validator = CustomerLeadBusinessValidator()
        self.scraper = GoogleLocalSearchService()
    
    @transaction.atomic
    def create_lead(self, data, user):
        """Create a new customer lead
        
        Args:
            data (dict): Data for creating lead
            user: User creating the lead
            
        Returns:
            CustomerLeads: Created lead instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate business rules
        self.validator.validate_lead_data(data)
        
        # Create lead - BaseModel will automatically set company, created_by, and updated_by
        lead = CustomerLeads.objects.create(**data)
        
        # Pass user to save method to ensure proper audit field values
        lead.save(user=user)
        
        logger.info(
            f"[CUSTOMER LEAD SERVICE] - Lead created successfully",
            extra={'lead_id': str(lead.id), 'created_by': user.id}
        )
        return lead
    
    @transaction.atomic
    def update_lead(self, instance, data, user):
        """Update an existing customer lead
        
        Args:
            instance: CustomerLeads instance to update
            data (dict): Data for updating lead
            user: User updating the lead
            
        Returns:
            CustomerLeads: Updated lead instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate business rules
        self.validator.validate_company_access(instance, user)
        
        # Update status if provided
        if 'status' in data and data['status'] != instance.status:
            self.validator.validate_leads_status_change(instance, data['status'])
        
        # Update fields
        for field, value in data.items():
            if field not in ['company', 'created_at', 'updated_at', 'created_by', 'updated_by']:  # Skip audit fields
                setattr(instance, field, value)
        
        instance.save(user=user)
        
        logger.info(
            f"[CUSTOMER LEAD SERVICE] - Lead updated successfully",
            extra={'lead_id': str(instance.id), 'updated_by': user.id}
        )
        return instance
    
    @transaction.atomic
    def delete_lead(self, instance, user):
        """Delete a customer lead
        
        Args:
            instance: CustomerLeads instance to delete
            user: User deleting the lead
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate business rules
        self.validator.validate_company_access(instance, user)
        
        lead_id = str(instance.id)
        instance.delete()
        
        logger.info(
            f"[CUSTOMER LEAD SERVICE] - Lead deleted successfully",
            extra={'lead_id': lead_id, 'deleted_by': user.id}
        )
    
    @transaction.atomic
    def update_lead_status(self, lead_id, new_status, user, notes=None):
        """Update the status of a lead
        
        Args:
            lead_id: ID of the lead to update
            new_status: New status value
            user: User updating the status
            notes: Optional notes about the status change
            
        Returns:
            CustomerLeads: Updated lead instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            lead = CustomerLeads.objects.get(id=lead_id, company=user.employeer.company)
        except CustomerLeads.DoesNotExist:
            logger.error(
                f"[CUSTOMER LEAD SERVICE] - Lead not found",
                extra={'lead_id': lead_id, 'user_id': user.id}
            )
            raise ValidationError(_("Lead not found"))
        
        # Validate status change
        self.validator.validate_leads_status_change(lead, new_status)
        
        # Update status
        lead.status = new_status
        
        # Add notes if provided
        if notes:
            if lead.notes:
                lead.notes += f"\n[{new_status}] {notes}"
            else:
                lead.notes = f"[{new_status}] {notes}"
        
        lead.save(user=user)
        
        logger.info(
            f"[CUSTOMER LEAD SERVICE] - Lead status updated to {new_status}",
            extra={'lead_id': str(lead.id), 'updated_by': user.id}
        )
        return lead
    
    def generate_leads_from_search(self, query, location, user, limit=None, include_all_pages=False):
        """Generate leads from Google Local search results
        
        Args:
            query (str): Search term provided by user
            location (str, optional): Location to search from
            user: User generating the leads
            limit (int, optional): Maximum number of results to return
            include_all_pages (bool): Whether to retrieve results from all pages
            
        Returns:
            dict: Summary of results including created and existing leads
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate search query
        self.validator.validate_search_query(query, location)
        
        # Get business data from Google Local Search
        business_data = self.scraper.search_local_businesses_sync(
            query=query,
            location=location,
            limit=limit,
            include_all_pages=include_all_pages
        )
        
        if not business_data:
            return {
                "total_results": 0,
                "new_leads": 0,
                "existing_leads": 0,
                "leads": [],
                "message": "No new leads were generated."
            }
        
        # Process the business data to create leads
        created_leads = []
        existing_leads = []
        
        with transaction.atomic():
            
            #Preparation for mass verification
            place_ids = [b.get('place_id') for b in business_data if b.get('place_id')]
            name_addresses = [(b.get('name'), b.get('address')) for b in business_data 
                              if b.get('name') and b.get('address')]
        
            #Efficient lead search
            existing_by_place_id = {
                lead.place_id: lead for lead in 
                CustomerLeads.objects.filter(
                    place_id__in=place_ids,
                    companie=user.employeer.companie
                )
            }
        
            # Search by name+address for those without place_id
            name_address_filter = Q()
            for name, address in name_addresses:
                name_address_filter |= Q(name=name, address=address)
        
            existing_by_name_address = {}
            if name_address_filter:
                for lead in CustomerLeads.objects.filter(
                    name_address_filter,
                    companie=user.employeer.companie
                ):
                    existing_by_name_address[(lead.name, lead.address)] = lead
        
            #Constants for comparisons - convert to set for more efficient comparisons
            info_placeholders = set(["", None, "INFO NOT INCLUDED", "NO RATING FOUND", 
                            "NO REVIEWS FOUND", "NO PHONE FOUND", "NO WEBSITE FOUND"])
            
            #Preparing bulk create and update lists
            leads_to_create = []
            leads_to_update = []
            
            for business in business_data:
                # Check if lead already exists by place_id or name+address
                existing_lead = None
                if business.get('place_id') and business['place_id'] in existing_by_place_id:
                    existing_lead = existing_by_place_id[business['place_id']]                    
                elif business.get('name') and business.get('address'):
                    key = (business['name'], business['address'])
                    existing_lead = existing_by_name_address.get(key)
                
                if not existing_lead and business.get('name') and business.get('address'):
                    existing_lead = CustomerLeads.objects.filter(
                        name=business['name'],
                        address=business['address'],
                        companie=user.employeer.companie
                    ).first()
                
                if existing_lead:
                    #Update existing lead with any new information
                    updated = False
                    for field, value in business.items():
                        if not isinstance(value, dict) and value not in info_placeholders:
                            if not isinstance(getattr(existing_lead, field, None), dict) and getattr(existing_lead, field, None) in info_placeholders:
                                setattr(existing_lead, field, value)
                                updated = True
                    
                    if updated:
                        leads_to_update.append(existing_lead)
                    existing_leads.append(existing_lead)
                else:
                    # Create new lead - don't set audit fields as they're handled by BaseModel
                    lead_data = {
                        'name': business['name'],
                        'address': business['address'] if business['address'] not in info_placeholders else "",
                        'phone': business['phone'] if business['phone'] not in info_placeholders else "",
                        'website': business['website'] if business['website'] not in info_placeholders else "",
                        'hours': business['hours'] if business['hours'] not in info_placeholders else "",
                        'rating': business['rating'] if business['rating'] not in info_placeholders else "",
                        'reviews': business['reviews'] if business['reviews'] not in info_placeholders else "",
                        'category': business['category'] if business['category'] not in info_placeholders else "",
                        'place_id': business['place_id'] if business['place_id'] not in info_placeholders else "",
                        'status': "New",
                    }
                    
                    # Add to bulk_create list instead of creating individually
                    new_lead = CustomerLeads(**lead_data)
                    leads_to_create.append(new_lead)
            
            # Bulk create for new leads
            if leads_to_create:
                # It is not possible to use bulk_create directly due to the custom save() method of BaseModel
                # that needs to process audit fields. We create smaller batches for efficiency
                batch_size = 100
                for i in range(0, len(leads_to_create), batch_size):
                    batch = leads_to_create[i:i + batch_size]
                    for lead in batch:
                        lead.save(user=user)  # Save with user for audit fields
                    created_leads.extend(batch)
                
                logger.info(
                    f"[CUSTOMER LEAD SERVICE] - Created {len(created_leads)} leads in bulk operation",
                    extra={'batch_count': len(created_leads) // batch_size + (1 if len(created_leads) % batch_size > 0 else 0)}
                )
            
            # Bulk update for existing leads
            if leads_to_update:
                # Same limit for bulk_update due to the custom save() method
                batch_size = 100
                for i in range(0, len(leads_to_update), batch_size):
                    batch = leads_to_update[i:i + batch_size]
                    for lead in batch:
                        lead.save(user=user)  # Save with user for audit fields
                
                logger.info(
                    f"[CUSTOMER LEAD SERVICE] - Updated {len(leads_to_update)} leads in bulk operation",
                    extra={'batch_count': len(leads_to_update) // batch_size + (1 if len(leads_to_update) % batch_size > 0 else 0)}
                )
        
        logger.info(
            f"[CUSTOMER LEAD SERVICE] - Leads generated successfully: {len(created_leads)} new, {len(existing_leads)} existing",
            extra={
                'query': query, 
                'location': location, 
                'total_results': len(business_data),
                'user_id': user.id
            }
        )
        
        # Determine appropriate message based on number of new leads
        if len(created_leads) > 0:
            message = f"Successfully generated {len(created_leads)} new leads."
        else:
            message = "No new leads were generated."
        
        return {
            "total_results": len(business_data),
            "new_leads": len(created_leads),
            "existing_leads": len(existing_leads),
            "leads": created_leads + existing_leads,
            "message": message
        }