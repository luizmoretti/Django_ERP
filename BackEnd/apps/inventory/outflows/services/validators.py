from rest_framework.exceptions import ValidationError
from ..models import Outflow, OutflowItems
import logging

logger = logging.getLogger(__name__)

class OutflowBusinessValidator:
    """Validator class for Outflow business rules"""
    
    @staticmethod
    def validate_company_access(data, user):
        """Validate company access permissions"""
        user_company = user.employeer.companie
        
        # Validate origin warehouse
        if data.get('origin') and data['origin'].companie != user_company:
            raise ValidationError("Invalid warehouse for user's company")
            
        # Validate destiny customer
        if data.get('destiny') and data['destiny'].companie != user_company:
            raise ValidationError("Invalid customer for user's company")
            
        logger.debug("Company access validated")
    
    @staticmethod
    def validate_outflow_status(outflow, expected_status="pending"):
        """Validate outflow status for operations"""
        if outflow.status != expected_status:
            raise ValidationError(f"Only {expected_status} outflows can be processed")
            
        logger.debug(f"Outflow status validated: {outflow.status}")
    
    @staticmethod
    def validate_outflow_items(outflow):
        """Validate outflow items"""
        if not outflow.items.exists():
            raise ValidationError("Cannot process outflow without items")
            
        logger.debug("Outflow items validated")
    
    @staticmethod
    def validate_rejection(rejection_reason):
        """Validate rejection reason"""
        if not rejection_reason or not rejection_reason.strip():
            raise ValidationError("A valid rejection reason is required")
            
        if len(rejection_reason) < 10:
            raise ValidationError("Rejection reason must be descriptive (min 10 characters)")
            
        logger.debug("Rejection reason validated")