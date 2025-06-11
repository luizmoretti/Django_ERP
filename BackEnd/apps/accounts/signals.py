"""
Django Signals for Account Management

This module provides signal handlers for user-related operations:
1. Creating company records for new users when appropriate
2. Creating employee records automatically when new users are registered
3. Assigning users to their appropriate permission groups based on user type
4. Synchronizing user permissions based on group changes

Key Features:
- Automatic company record creation
- Automatic employee record creation
- Permission group assignment and synchronization
- Error handling and logging
- Transaction management
"""

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db import transaction
from .models import User
from core.constants.choices import USER_TYPE_CHOICES
from django.contrib.auth.models import AnonymousUser
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
import logging
from django.contrib.auth import user_logged_in
from functools import lru_cache

logger = logging.getLogger(__name__)


# --------------------------------
# Utility Functions
# --------------------------------

@lru_cache(maxsize=32)
def get_user_type_from_group_name(group_name):
    """
    Get the user type from the group name.
    
    Args:
        group_name (str): The name of the group to look up
    
    Returns:
        str: The user type associated with the group name
    """
    for user_type, group in USER_TYPE_CHOICES:
        if group == group_name:
            return user_type
    return None


@lru_cache(maxsize=32)
def get_group_name_from_user_type(user_type):
    """
    Get the group name from the user type.
    
    Args:
        user_type (str): The user type to look up
    
    Returns:
        str: The group name associated with the user type
    """
    for type_choice, group in USER_TYPE_CHOICES:
        if type_choice == user_type:
            return group
    return None


def refresh_user_permission_cache(user):
    """
    Refresh a user's permission cache by clearing cached attributes.
    
    Args:
        user: The user instance whose permission cache should be refreshed
    """
    for cache_attr in ('_perm_cache', '_user_perm_cache', '_group_perm_cache'):
        if hasattr(user, cache_attr):
            delattr(user, cache_attr)


def sync_user_permissions(user):
    """
    Synchronize a user's permissions based on their group memberships.
    
    Args:
        user: The user instance whose permissions should be synced
    """
    # Clear user's permissions
    user.user_permissions.clear()
    
    # Add all permissions from all user's groups
    permissions_to_add = []
    for group in user.groups.all().prefetch_related('permissions'):
        group_permissions = list(group.permissions.all())
        if group_permissions:
            permissions_to_add.extend(group_permissions)
    
    # Bulk add permissions if any exist to reduce DB queries
    if permissions_to_add:
        user.user_permissions.add(*permissions_to_add)
    
    # Refresh user's permission cache
    refresh_user_permission_cache(user)


# --------------------------------
# User Creation and Initial Setup
# --------------------------------

@receiver(post_save, sender=User)
def create_company_for_user(sender, instance, created, **kwargs):
    """
    Signal handler to create a company record for new users when appropriate.
    This signal runs before create_employee_and_assign_group.
    
    Creates a new company for users with specific user types (CEO, Owner, Admin)
    or superusers. The company will be associated with the employee record in 
    the subsequent signal.
    
    Args:
        sender: The model class (User)
        instance: The actual user instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if not created:  # Only execute on user creation
        return
        
    from crum import get_current_user
    creator = get_current_user()
    if not creator or isinstance(creator, AnonymousUser):
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


@receiver(post_save, sender=User)
def create_employee_and_assign_group(sender, instance, created, **kwargs):
    """
    Signal handler to create employee record and assign permission group for new users.
    
    This handler performs two main tasks:
    1. Creates an Employeer record for the new user if one doesn't exist
    2. Assigns the user to their appropriate permission group based on user_type
    
    Args:
        sender: The model class (User)
        instance: The actual user instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if not created:  # Only execute on user creation
        return
        
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
            if instance.user_type:  # Only proceed if user_type is set
                try:
                    group = Group.objects.get(name=instance.user_type)
                    instance.groups.add(group)
                    logger.info(f"User {instance.email} added to group {instance.user_type}")
                except Group.DoesNotExist:
                    logger.error(f"Permission group {instance.user_type} does not exist")
                
    except Exception as e:
        logger.error(f"Error in post_save signal for user {instance.email}: {str(e)}")
        raise


# --------------------------------
# Permission Management
# --------------------------------

@receiver(post_save, sender=Group)
def resync_user_permissions(sender, instance, created, **kwargs):
    """
    Signal to re-sync user permissions when a group is created or updated.
    
    This signal handler ensures that when group permissions are modified,
    all users in that group have their permissions properly updated to
    reflect the changes.
    
    Args:
        sender: The model class (Group)
        instance: The actual group instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    try:
        # Get all users in the group - use select_for_update to prevent race conditions
        users = instance.user_set.all().select_for_update()
        
        # Process users in chunks to avoid memory issues with large groups
        CHUNK_SIZE = 100
        users_count = users.count()
        
        for i in range(0, users_count, CHUNK_SIZE):
            with transaction.atomic():
                user_chunk = users[i:i+CHUNK_SIZE]
                for user in user_chunk:
                    sync_user_permissions(user)
        
        logger.info(f"User permissions successfully re-synced for {users_count} users in group {instance.name}")
    except Exception as e:
        logger.error(f"Error re-syncing user permissions for group {instance.name}: {str(e)}")
        raise


@receiver(m2m_changed, sender=User.groups.through)
def sync_user_permissions_on_group_change(sender, instance, action, pk_set, **kwargs):
    """
    Signal handler to sync user permissions when user-group relationship changes.
    
    This ensures that when a user is added to or removed from a group,
    their individual permissions are updated accordingly.
    
    Args:
        sender: The intermediate model class (User.groups.through)
        instance: The instance being modified (User instance)
        action: The type of change ('post_add', 'post_remove', 'post_clear')
        pk_set: Set of PKs being added/removed (Group PKs)
        **kwargs: Additional keyword arguments
    """
    # Only process after the groups have been added/removed
    if action not in ['post_add', 'post_remove', 'post_clear']:
        return
    
    try:
        with transaction.atomic():
            # Use the utility function to sync permissions
            sync_user_permissions(instance)
            logger.info(f"User permissions successfully re-synced for user {instance.email}")
    except Exception as e:
        logger.error(f"Error re-syncing user permissions for user {instance.email}: {str(e)}")
        raise


@receiver(post_save, sender=User)
def update_user_group_on_type_change(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    Signal handler to update user's group membership when user_type changes.
    
    When an existing user has their user_type changed, this handler:
    1. Detects the user_type change
    2. Adds the user to the appropriate group based on the new user_type
    3. Removes the user from their previous type-based group
    
    Args:
        sender: The model class (User)
        instance: The actual user instance
        created: Boolean indicating if this is a new record
        raw: Boolean, True if the model is being loaded from a fixture
        using: Database alias being used
        update_fields: Fields being updated in the save method
        **kwargs: Additional keyword arguments
    """
    # Skip for new users as they're handled by create_employee_and_assign_group
    if created or raw:
        return
    
    # Skip if no specific fields were updated or if user_type wasn't among them
    if update_fields is not None and 'user_type' not in update_fields:
        return
        
    # Skip if user_type isn't set
    new_group_name = instance.user_type
    if not new_group_name:
        return
    
    # Add a flag to prevent recursive calls or duplicate processing
    if getattr(instance, '_is_updating_groups', False):
        logger.debug(f"Skipping duplicate group update for user {instance.email}")
        return
    
    try:
        # Set the flag to prevent recursive processing
        instance._is_updating_groups = True
        
        # Use a separate transaction to ensure changes are committed
        with transaction.atomic():
            try:
                # Try to get the group - if it doesn't exist, we'll raise an error early
                try:
                    new_group = Group.objects.get(name=new_group_name)
                except Group.DoesNotExist:
                    logger.warning(f"Group {new_group_name} does not exist, cannot update user's group membership")
                    return
                
                # Force reload the instance to ensure we have the latest data and lock it
                user = User.objects.select_for_update().get(pk=instance.pk)
                
                # Get all valid user type codes (the first element of each tuple in USER_TYPE_CHOICES)
                valid_type_codes = {user_type for user_type, _ in USER_TYPE_CHOICES}
                
                # Get the current groups associated with the user
                current_groups = list(user.groups.all())
                
                # Identify which current groups are associated with user types
                # A group is a "type group" if its name matches one of the user type codes
                current_type_groups = [g for g in current_groups if g.name in valid_type_codes]
                
                # Log current group state for debugging
                logger.info(f"User {user.email} current groups: {[g.name for g in current_groups]}")
                logger.info(f"User {user.email} current type groups: {[g.name for g in current_type_groups]}")
                
                # Check if the user already has the correct configuration
                is_in_correct_group = new_group in current_groups
                has_other_type_groups = any(g for g in current_type_groups if g.name != new_group_name)
                
                if not is_in_correct_group or has_other_type_groups:
                    logger.info(f"Updating groups for user {user.email}: current type groups={[g.name for g in current_type_groups]}, target={new_group_name}")
                    
                    # Remove from ALL type groups directly using the M2M through model
                    if current_type_groups:
                        # Collect IDs of all type groups to remove
                        groups_to_remove_ids = [g.id for g in current_type_groups]
                        
                        # Use a direct query to efficiently remove all type groups at once
                        removed_count = user.groups.through.objects.filter(
                            user_id=user.pk, 
                            group_id__in=groups_to_remove_ids
                        ).delete()[0]
                        
                        logger.info(f"Removed {removed_count} type-based group associations for user {user.email}")
                        
                        # Log individual removals for clarity
                        for group in current_type_groups:
                            logger.info(f"User {user.email} removed from group {group.name}")
                    
                    # Add to new group if not already in it
                    if not is_in_correct_group:
                        user.groups.add(new_group)
                        logger.info(f"User {user.email} added to group {new_group_name} based on user_type change")
                    
                    # Manually sync permissions
                    sync_user_permissions(user)
                    logger.info(f"Permissions explicitly synced for user {user.email}")
                    
                    # Verify the changes applied correctly
                    user.refresh_from_db()
                    updated_groups = list(user.groups.all())
                    logger.info(f"User's groups after update: {[g.name for g in updated_groups]}")
                    
                    # Extra verification step - check again if the user is in exactly the right type groups
                    type_groups_after = [g for g in updated_groups if g.name in valid_type_codes]
                    expected_type_groups = [new_group_name]
                    
                    if [g.name for g in type_groups_after] != expected_type_groups:
                        logger.warning(f"Group synchronization incomplete! User {user.email} has type groups {[g.name for g in type_groups_after]} instead of just {expected_type_groups}")
                        
                        # Emergency correction - try again with a more direct approach
                        logger.info(f"Attempting emergency correction of groups for user {user.email}")
                        
                        # Remove ALL groups that match user types
                        direct_remove_count = 0
                        for group_to_remove in type_groups_after:
                            if group_to_remove.name != new_group_name:
                                user.groups.remove(group_to_remove)
                                direct_remove_count += 1
                        
                        if direct_remove_count > 0:
                            logger.info(f"Emergency correction: removed {direct_remove_count} extra type groups")
                            
                            # Verify again
                            user.refresh_from_db()
                            final_groups = list(user.groups.all())
                            logger.info(f"User's groups after emergency correction: {[g.name for g in final_groups]}")
                else:
                    logger.debug(f"User {user.email} already has the correct group configuration")
            
            except Exception as e:
                logger.error(f"Error updating group for user {instance.email} on type change: {str(e)}", exc_info=True)
                raise
    finally:
        # Always reset the flag, even if an exception occurred
        instance._is_updating_groups = False


# --------------------------------
# User IP Tracking
# --------------------------------

@receiver(user_logged_in)
def update_user_ip(sender, user, request, **kwargs):
    """
    Signal to update user's IP address when they log in
    
    Args:
        sender: The signal sender
        user: The user who just logged in
        request: The HTTP request object
        **kwargs: Additional keyword arguments
    """
    if hasattr(user, 'get_ip_on_login'):
        user.get_ip_on_login(request)


@receiver(post_save, sender=User)
def ensure_ip_on_create(sender, instance, created, **kwargs):
    """
    Signal to ensure IP address is saved when a user is created
    
    Args:
        sender: The model class (User)
        instance: The actual user instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created and not instance.ip and hasattr(instance, '_request'):
        instance.get_ip_on_login(instance._request)