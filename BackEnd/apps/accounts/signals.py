"""
Django Signals for Account Management

This module provides signal handlers for user-related operations:
1. Creating company records for new users when appropriate
2. Creating employee records automatically when new users are registered
3. Assigning users to their appropriate permission groups based on user type

Key Features:
- Automatic company record creation
- Automatic employee record creation
- Permission group assignment
- Error handling and logging
- Transaction management
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db import transaction
from .models import NormalUser
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
import logging
from django.contrib.auth import user_logged_in

logger = logging.getLogger(__name__)

@receiver(post_save, sender=NormalUser)
def create_company_for_user(sender, instance, created, **kwargs):
    """
    Signal handler to create a company record for new users when appropriate.
    This signal runs before create_employee_and_assign_group.
    
    Creates a new company for users with specific user types (CEO, Owner, Admin)
    or superusers. The company will be associated with the employee record in 
    the subsequent signal.
    
    Args:
        sender: The model class (NormalUser)
        instance: The actual user instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created:  # Only execute on user creation
        if instance.user_type in ['CEO', 'Owner', 'Admin'] or instance.is_superuser:
            try:
                with transaction.atomic():
                    logger.info(f"Creating company for user {instance.email}")
                    company = Companie.objects.create(
                        name=f"{instance.first_name}'s Company",
                        type='Headquarters',
                        email=instance.email,
                        is_active=True
                    )
                    # Store the company ID in the user instance for use in the next signal
                    instance._company_id = company.id
                    logger.info(f"Company created successfully for {instance.email} with the name: {company.name}")
                    
            except Exception as e:
                logger.error(f"Error creating company for user {instance.email}: {str(e)}")
                raise

@receiver(post_save, sender=NormalUser)
def create_employee_and_assign_group(sender, instance, created, **kwargs):
    """
    Signal handler to create employee record and assign permission group for new users.
    
    This handler performs two main tasks:
    1. Creates an Employeer record for the new user if one doesn't exist
    2. Assigns the user to their appropriate permission group based on user_type
    
    Args:
        sender: The model class (NormalUser)
        instance: The actual user instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created:  # Only execute on user creation
        try:
            with transaction.atomic():
                # Create employee record if user_type is appropriate
                if instance.user_type not in ['Customer', 'Supplier']:
                    logger.info(f"Creating employee record for user {instance.email}")
                    
                    # Get the company if it was created in the previous signal
                    company = None
                    if hasattr(instance, '_company_id'):
                        company = Companie.objects.get(id=instance._company_id)
                    
                    employee = Employeer.objects.create(
                        user=instance,
                        name=f"{instance.first_name} {instance.last_name}",
                        email=instance.email,
                        companie=company  # This will be None for regular employees
                    )
                    logger.info(f"Employee record created successfully for {instance.email}")
                
                # Assign user to appropriate permission group
                group_name = instance.user_type
                try:
                    group = Group.objects.get(name=group_name)
                    instance.groups.add(group)
                    logger.info(f"User {instance.email} added to group {group_name}")
                except Group.DoesNotExist:
                    logger.error(f"Permission group {group_name} does not exist")
                    
        except Exception as e:
            logger.error(f"Error in post_save signal for user {instance.email}: {str(e)}")
            # Re-raise the exception to ensure proper error handling
            raise


@receiver(user_logged_in)
def update_user_ip(sender, user, request, **kwargs):
    """
    Signal para atualizar o IP do usuário quando ele faz login
    """
    if hasattr(user, 'get_ip_on_login'):
        user.get_ip_on_login(request)

@receiver(post_save, sender=NormalUser)
def ensure_ip_on_create(sender, instance, created, **kwargs):
    """
    Signal para garantir que o IP seja salvo na criação do usuário
    """
    if created and not instance.ip and hasattr(instance, '_request'):
        instance.get_ip_on_login(instance._request)