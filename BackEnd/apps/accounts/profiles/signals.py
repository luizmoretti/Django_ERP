"""
Django Signals for User Profile Management

This module provides signal handlers for operations related to user profiles:
1. Automatic profile creation when a new user is registered (excluding external users)
2. Synchronization of basic data between user and profile

Key Features:
- Automatic profile creation for internal users only
- Maintenance of data consistency
- Integration with the audit system
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Profile
import logging
from crum import get_current_user

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create an automatic profile when a new user is registered.
    
    This handler checks if the user is new and creates a profile associated with the user.
    The profile inherits basic user information, such as name and email.
    
    NOTE: Profiles are only created for internal users (employees), not for external 
    users like Customers and Suppliers, to maintain consistency with the Employee 
    creation logic.
    
    Args:
        sender: A class of the model (User)
        instance: An instance of the user
        created: Boolean indicating if this is a new record
        **kwargs: Additional arguments
    """
    # Skip if not a new user or if the user already has a profile
    if not created:
        return
        
    # Skip profile creation for external users (Customer, Supplier)
    # This maintains consistency with the Employee creation logic
    if instance.user_type in ['Customer', 'Supplier']:
        logger.info(f"Skipping profile creation for external user type: {instance.user_type} ({instance.email})")
        return
        
    # Check if the profile already exists to avoid duplicates
    if hasattr(instance, 'profile'):
        return
        
    try:
        with transaction.atomic():
            # Get the current user (creator) for audit
            creator = get_current_user()
            
            # Create the profile with basic user data
            profile = Profile.objects.create(
                user=instance,
                email=instance.email,
                # Default preferences (can be customized)
                preferences={
                    'theme': 'light',
                    'notifications': True,
                    'language': 'pt-br'
                },
                # Assign to the same company as the creator if available
                companie=getattr(creator, 'employeer', None).companie if creator and hasattr(creator, 'employeer') else None
            )
            
            logger.info(f"Profile created automatically for user {instance.email}")
    except Exception as e:
        logger.error(f"Error creating profile for user {instance.email}: {str(e)}", exc_info=True)
        # Do not re-raise the exception to allow the user to be created even if the profile creation fails