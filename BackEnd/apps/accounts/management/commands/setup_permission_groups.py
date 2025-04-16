"""
Django Management Command for Setting Up Permission Groups

This module provides a Django management command that sets up user groups and their corresponding
permissions based on predefined user types and app mappings. It implements a sophisticated
permission system that controls access to different parts of the application based on user roles.

Key Features:
- Creates and configures user groups automatically
- Assigns specific permissions to each group based on app and action type
- Implements detailed logging for debugging and monitoring
- Supports granular permission control based on HTTP methods
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from core.constants.choices import USER_TYPE_CHOICES
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Django command to set up user groups and assign appropriate permissions.
    This command creates predefined groups and assigns them specific permissions
    based on their roles and allowed actions.
    """
    
    help = "Setup user groups and assign permissions"
    
    def __sync_user_permissions(self):
        """
        Synchronizes user permissions based on their groups.
        This ensures that users have all the permissions of the groups they belong to.
        """
        User = get_user_model()
        logger.info("Synchronizing user permissions")
        
        for user in User.objects.all():
            try:
                # Clear existing user permissions
                user.user_permissions.clear()
                
                # Add all permissions to the user's groups
                for group in user.groups.all():
                    permissions = group.permissions.all()
                    user.user_permissions.add(*permissions)
                    
                logger.info(f"Synchronized user permissions: {user.email}")
                
            except Exception as e:
                logger.error(f"Error synchronizing user permissions {user.email}: {str(e)}")
    

    def __get_custom_permissions(self, app_label):
        """
        Get custom permissions defined in models for a specific app.
        
        Args:
            app_label (str): The app label to get permissions from
            
        Returns:
            list: List of custom permission codenames
        """
        custom_permissions = []
        try:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                if hasattr(model._meta, 'permissions'):
                    model_perms = [perm[0] for perm in model._meta.permissions]
                    custom_permissions.extend(model_perms)
                    logger.debug(f"Found custom permissions for {model.__name__}: {model_perms}")
        except Exception as e:
            logger.error(f"Error getting custom permissions for app {app_label}: {str(e)}")
        
        return custom_permissions

    def __get_allowed_actions(self, group_name):
        """
        Get allowed actions for a specific group.
        
        Args:
            group_name (str): Name of the group
            
        Returns:
            function: Lambda function that returns list of allowed actions for given app
        """
        logger.debug(f"Getting allowed actions for group: {group_name}")
        
        # Define specific permissions per app for each group
        group_permissions = {
            "Owner": lambda app_label: (
                ["view", "add", "change", "delete"] + 
                (self.__get_custom_permissions(app_label) if app_label == "purchase_order" else [])
            ),
            
            "CEO": lambda app_label: (
                ["view", "add", "change", "delete"] + 
                (self.__get_custom_permissions(app_label) if app_label == "purchase_order" else [])
            ),
            
            "Admin": lambda app_label: (
                ["view", "add", "change", "delete"] + 
                (self.__get_custom_permissions(app_label) if app_label == "purchase_order" else [])
            ),
            
            "Manager": lambda app_label: (
                (["view", "add", "change", "delete"] + self.__get_custom_permissions(app_label))
                if app_label == "purchase_order" else
                ["view", "add", "change", "delete"] if app_label in [
                    "employeers", "hr", "warehouse", "inventory", "categories",
                    "brand", "supplier", "product", "customers"
                ] else ["view", "add", "change"] if app_label in [
                    "inflows", "outflows", "transfer", "vehicles"
                ] else ["view"] if app_label in [
                    "deliveries"
                ] else []
            ),
            
            "Stocker": lambda app_label: ["view"] if app_label in [
                "products", "suppliers", "barcodes", "warehouse", 
                "categories", "brands"
            ] else ['add', 'change', 'delete'] if app_label in [
                'inflows', 'outflows', 'transfers'
            ] else [],
            
            "Employee": lambda app_label: ["view_own_profile", "change_own_profile"] if app_label == "profiles" else [],
            
            "Salesman": lambda app_label: ["view"] if app_label in [
                "products", "categories", "brands", "customers"
            ] else [],
            
            "Driver": lambda app_label: ["view_own_delivery", "change_own_delivery_status"] if app_label in [
                "delivery"
            ] else [],
            
            "Customer": lambda app_label: ["view_own_delivery"] if app_label in [
                "delivery"
            ] else [],
            
            "Supplier": lambda app_label: ["view"] if app_label in [
                "products", "categories", "brands"
            ] else []
        }
        
        permission_getter = group_permissions.get(group_name)
        if not permission_getter:
            logger.warning(f"No action defined for the group {group_name}")
            return lambda app_label: []
            
        return permission_getter

    def handle(self, *args, **kwargs):
        """
        Main command handler that sets up groups and permissions.
        Creates user groups and assigns appropriate permissions based on
        predefined mappings.
        """
        logger.info("Starting permission groups setup")
        
        # Get all installed apps that start with 'apps.'
        installed_apps = [
            app.split('.')[-1] for app in settings.INSTALLED_APPS 
            if app.startswith('apps.')
        ]
        
        for group_name, _ in USER_TYPE_CHOICES:
            logger.info(f"Setting up group: {group_name}")
            
            try:
                # Create or get the group
                group, created = Group.objects.get_or_create(name=group_name)
                if created:
                    logger.info(f"Created new group: {group_name}")
                
                # Clear existing permissions
                group.permissions.clear()
                logger.debug(f"Cleared existing permissions for group: {group_name}")
                
                # Get allowed actions for this group
                allowed_actions = self.__get_allowed_actions(group_name)
                
                for app_label in installed_apps:
                    # Get all permissions for this app
                    content_types = ContentType.objects.filter(app_label=app_label)
                    app_permissions = Permission.objects.filter(content_type__in=content_types)
                    
                    # Get allowed permission codenames for this app
                    allowed_codenames = allowed_actions(app_label)
                    
                    # Add permissions that match the allowed codenames
                    permissions_to_add = []
                    for content_type in content_types:
                        model = content_type.model_class()
                        if model:
                            for action in allowed_codenames:
                                if action.startswith(('can_', 'view_', 'add_', 'change_', 'delete_')):
                                    codename = action
                                else:
                                    codename = f"{action}_{model._meta.model_name}"
                                permissions_to_add.append(codename)
                    
                    if permissions_to_add:
                        matching_permissions = app_permissions.filter(codename__in=permissions_to_add)
                        if matching_permissions:
                            group.permissions.add(*matching_permissions)
                            logger.debug(
                                f"Added {matching_permissions.count()} permissions for app "
                                f"{app_label} to group {group_name}"
                            )
                            
                            # Log individual permissions for debugging
                            for perm in matching_permissions:
                                logger.debug(f"Added permission to {group_name}: {perm.codename}")
                
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully configured group: {group_name}")
                )
                
            except Exception as e:
                logger.error(f"Error configuring group {group_name}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"Error configuring group {group_name}: {str(e)}")
                )
        
        # After processing all groups, sync user permissions
        self.__sync_user_permissions()
        
        logger.info("Permission groups setup completed successfully")