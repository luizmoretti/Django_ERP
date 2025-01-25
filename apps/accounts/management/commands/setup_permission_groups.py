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

    def has_permission(self, request, view):
        """
        Check if a user has permission to perform a specific action.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user_type = request.user.groups.first().name if request.user.groups.exists() else None
        logger.debug(f"Checking permissions for user type: {user_type}")
        
        model_permission_codename = self.__get_model_permission_codename(
            method=request.method,
            view=view,
            user_type=user_type
        )
        
        if model_permission_codename is None:
            logger.info(f"Permission not required for {request.method} in {view.__class__.__name__}")
            return True
            
        has_perm = request.user.has_perm(model_permission_codename)
        if not has_perm:
            logger.warning(f"Access denied: User {request.user} does not have permission {model_permission_codename}")
        return has_perm

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
            "Owner": lambda app_label: ["view", "add", "change", "delete"],  # Full access to all apps
            
            "CEO": lambda app_label: ["view", "add", "change", "delete"],  # Full access to all apps
            
            "Manager": lambda app_label: (
                ["view", "add", "change", "delete"] if app_label in [
                    "teams", "employees", "stores", "inventory", "categories",
                    "brands", "suppliers", "barcodes", "customers", "projects",
                    "invoices", "sales"
                ] else ["view", "add", "change"] if app_label in [
                    "OrderPurchase", "products", "inflows", "outflows",
                    "transfers", "deliveries"
                ] else ["view"]
            ),
            
            "Stock controller": lambda app_label: (
                ["view", "add", "change"] if app_label in [
                    "inflows", "outflows", "transfers", "products",
                    "suppliers", "barcodes"
                ] else ["view"] if app_label in [
                    "stores", "categories", "brands"
                ] else []
            ),
            
            "Stockist": lambda app_label: (
                ["view"] if app_label in ["products", "customers", "suppliers"]
                else ["view", "add", "change"] if app_label in ["inflows", "outflows", "transfers"]
                else ["view", "add"] if app_label in ["barcodes", "stores"]
                else []
            ),
            
            "Deliverer": lambda app_label: (
                ["view", "change"] if app_label == "deliveries"
                else []
            )
        }
        
        permission_getter = group_permissions.get(group_name)
        if not permission_getter:
            logger.warning(f"No action defined for the group {group_name}")
            return lambda app_label: []
            
        return permission_getter

    def __get_model_permission_codename(self, method, view, user_type=None):
        """
        Generate permission codename based on HTTP method and view.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            view: The view being accessed
            user_type (str, optional): Type of user
            
        Returns:
            str: Permission codename or None if not applicable
        """
        logger.debug(f"Generating permission codename for method {method} and view {view.__class__.__name__}")
        
        if hasattr(view, "queryset") and view.queryset is not None:
            model = view.queryset.model
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            
            # Get specific permissions for the current group's app
            permission_getter = self.__get_allowed_actions(user_type)
            actions = permission_getter(app_label)
            
            action = self.__get_action_sufix(method, actions)
            
            if action:
                permission = f"{app_label}.{action}_{model_name}"
                logger.debug(f"Permission codename generated: {permission}")
                return permission
            
            logger.debug(f"No corresponding action for method {method}")
            return None
            
        logger.debug("View has no queryset defined")
        return None

    def __get_action_sufix(self, method, allowed_actions):
        """
        Get the corresponding action suffix for an HTTP method.
        
        Args:
            method (str): HTTP method
            allowed_actions (list): List of allowed actions
            
        Returns:
            str: Action suffix or None if not allowed
        """
        method_map = {
            "GET": "view",
            "POST": "add",
            "PUT": "change",
            "PATCH": "change",
            "DELETE": "delete",
            "OPTIONS": "view",
            "HEAD": "view",
        }
        action = method_map.get(method)
        return action if action in allowed_actions else None

    def handle(self, *args, **kwargs):
        """
        Main command handler that sets up groups and permissions.
        Creates user groups and assigns appropriate permissions based on
        predefined mappings.
        """
        logger.info("Starting to configure groups and permissions")
        
        # App definitions for each user type
        apps_mapping = {
            # Executive Level
            "Owner": ['accounts', 'companies', 'customers', 'employeers', 'hr'],
            "CEO": [],
            "Admin": [],
            
            # Management Level
            "Manager": [],
            "HR": [],
            "Accountant": [],
            
            # Operational Level
            "Employee": [],
            "Stock_Controller": [],
            "Stocker": [],
            "Salesman": [],
            "Driver": [],
            "Deliveryman": [],
            
            # External Users
            "Customer": [],
            "Supplier": []
        }

        def get_filtered_permissions(apps, group_name):
            """
            Get filtered permissions for a specific group and set of apps.
            
            Args:
                apps (list): List of app names
                group_name (str): Name of the group
                
            Returns:
                list: List of Permission objects
            """
            logger.debug(f"Searching for group {group_name} permissions in apps: {apps}")
            permission_getter = self.__get_allowed_actions(group_name)
            
            all_permissions = []
            for app in apps:
                allowed_actions = permission_getter(app)
                if allowed_actions:
                    app_permissions = Permission.objects.filter(
                        content_type__app_label=app
                    ).filter(
                        codename__regex=r'^(' + '|'.join(allowed_actions) + ')_'
                    )
                    all_permissions.extend(app_permissions)
            
            logger.debug(f"Total permissions found: {len(all_permissions)}")
            return all_permissions

        if not USER_TYPE_CHOICES:
            logger.error("No user type defined in the system")
            self.stdout.write(self.style.ERROR("No user types defined."))
            return

        total_groups = len(USER_TYPE_CHOICES)
        logger.info(f"Processing {total_groups} user groups")

        for user_type, group_name in USER_TYPE_CHOICES:
            logger.info(f"Processing group: {group_name}")
            try:
                group, created = Group.objects.get_or_create(name=group_name)
                if created:
                    logger.info(f"New group created: {group_name}")
                else:
                    logger.info(f"Existing group updated: {group_name}")

                group.permissions.clear()
                logger.debug(f"Previous permissions removed from the group {group_name}")

                apps = apps_mapping.get(group_name, [])
                if not apps:
                    logger.warning(f"No app defined for the group {group_name}")
                    continue

                permissions = get_filtered_permissions(apps, group_name)

                if permissions:
                    permission_count = len(permissions)
                    group.permissions.add(*permissions)
                    logger.info(f"Added {permission_count} permissions to the group {group_name}")
                    
                    # Detailed permission logging for debugging
                    for perm in permissions:
                        logger.debug(f"Permission added to {group_name}: {perm.codename}")
                        
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully processed group: {group_name}")
                )
                
            except Exception as e:
                logger.error(f"Error processing group {group_name}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"Error processing group {group_name}: {str(e)}")
                )