from rest_framework.exceptions import ValidationError
from ..models import Inflow, InflowItems
import logging

logger = logging.getLogger(__name__)

class InflowBusinessValidator:
    """
    Business validation service for Inflow operations
    Handles complex business rules and access control
    """
    
    @staticmethod
    def validate_company_access(data, user):
        """
        Validate that all resources belong to user's company
        
        Args:
            data (dict): Data containing company-related resources
            user: User attempting the operation
            
        Raises:
            ValidationError: If user tries to access resources from another company
        """
        user_company = user.employeer_user.companie
        
        # Validate origin supplier
        if data.get('origin') and data['origin'].companie != user_company:
            raise ValidationError("Invalid supplier for user's company")
            
        # Validate destiny warehouse
        if data.get('destiny') and data['destiny'].companie != user_company:
            raise ValidationError("Invalid warehouse for user's company")
            
        logger.debug(
            "Company access validated",
            extra={
                'user_id': user.id,
                'company_id': user_company.id
            }
        )
    
    @staticmethod
    def validate_inflow_status(inflow, expected_status="pending"):
        """
        Validate inflow status for operations
        
        Args:
            inflow (Inflow): Inflow to validate
            expected_status (str): Expected status for the operation
            
        Raises:
            ValidationError: If inflow status doesn't match expected
        """
        if inflow.status != expected_status:
            raise ValidationError(f"Only {expected_status} inflows can be processed")
            
        logger.debug(
            f"Inflow status validated: {inflow.status}",
            extra={
                'inflow_id': inflow.id,
                'status': inflow.status
            }
        )
    
    @staticmethod
    def validate_inflow_items(inflow):
        """
        Validate inflow items for business rules
        
        Args:
            inflow (Inflow): Inflow to validate
            
        Raises:
            ValidationError: If items validation fails
        """
        if not inflow.items.exists():
            raise ValidationError("Cannot process inflow without items")
            
        # Add any additional item-related business rules here
        logger.debug(
            "Inflow items validated",
            extra={
                'inflow_id': inflow.id,
                'items_count': inflow.items.count()
            }
        )
    
    @staticmethod
    def validate_rejection(rejection_reason):
        """
        Validate rejection business rules
        
        Args:
            rejection_reason (str): Reason for rejection
            
        Raises:
            ValidationError: If rejection validation fails
        """
        if not rejection_reason or not rejection_reason.strip():
            raise ValidationError("A valid rejection reason is required")
            
        if len(rejection_reason) < 10:
            raise ValidationError("Rejection reason must be descriptive (min 10 characters)")
            
        logger.debug("Rejection reason validated")
