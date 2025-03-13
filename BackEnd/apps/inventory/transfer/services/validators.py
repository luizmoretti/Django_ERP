from django.core.exceptions import ValidationError
from ..models import Transfer, TransferItems
import logging

logger = logging.getLogger(__name__)

class TransferBusinessValidator:
    """Validator class for Transfer business rules"""
    
    @staticmethod
    def validate_company_access(data, user):
        """Validate company access permissions"""
        user_company = user.employeer.companie
        
        # Validate origin warehouse
        if data.get('origin') and data['origin'].companie != user_company:
            raise ValidationError("Invalid origin warehouse for user's company")
            
        # Validate destiny warehouse
        if data.get('destiny') and data['destiny'].companie != user_company:
            raise ValidationError("Invalid destination warehouse for user's company")
            
        logger.debug("[Transfer Validator] Company access validated")
    
    @staticmethod
    def validate_transfer_status(transfer, expected_status="pending"):
        """Validate transfer status for operations"""
        if transfer.status != expected_status:
            raise ValidationError(f"Only {expected_status} transfers can be processed")
            
        logger.debug(f"[Transfer Validator] Transfer status validated: {transfer.status}")
    
    @staticmethod
    def validate_different_warehouses(data):
        """Validate that origin and destination warehouses are different"""
        if data.get('origin') and data.get('destiny') and data['origin'] == data['destiny']:
            raise ValidationError("Origin and destination warehouses must be different")
            
        logger.debug("[Transfer Validator] Different warehouses validated")
    
    @staticmethod
    def validate_transfer_items(transfer):
        """Validate transfer items"""
        if not transfer.items.exists():
            raise ValidationError("Cannot process transfer without items")
            
        logger.debug("[Transfer Validator] Transfer items validated")
    
    @staticmethod
    def validate_rejection(rejection_reason):
        """Validate rejection reason"""
        if not rejection_reason or not rejection_reason.strip():
            raise ValidationError("A valid rejection reason is required")
            
        if len(rejection_reason) < 10:
            raise ValidationError("Rejection reason must be descriptive (min 10 characters)")
            
        logger.debug("[Transfer Validator] Rejection reason validated")

    