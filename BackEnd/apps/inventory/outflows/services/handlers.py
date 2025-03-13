from ..models import Outflow, OutflowItems
from django.db import transaction
from .validators import OutflowBusinessValidator
import logging

logger = logging.getLogger(__name__)

class OutflowService:
    """Service class for Outflow operations"""
    
    def __init__(self):
        self.validator = OutflowBusinessValidator()
    
    def create_outflow(self, data, user):
        """Create a new outflow"""
        # Validate company access
        self.validator.validate_company_access(data, user)
        
        # Create outflow with transaction
        with transaction.atomic():
            outflow = Outflow.objects.create(
                origin=data['origin'],
                destiny=data['destiny'],
                status='pending',
                companie=user.employeer.companie,
                created_by=user.employeer,
                updated_by=user.employeer
            )
            
            # Create outflow items
            for item_data in data['items_data']:
                OutflowItems.objects.create(
                    outflow=outflow,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    companie=user.employeer.companie,
                    created_by=user.employeer,
                    updated_by=user.employeer
                )
            
            logger.info(f"Outflow created successfully", extra={'outflow_id': outflow.id})
            return outflow
    
    def update_outflow(self, outflow, data, user):
        """Update an existing outflow"""
        # Validate company access
        self.validator.validate_company_access(data, user)
        
        # Validate outflow status
        self.validator.validate_outflow_status(outflow)
        
        # Update outflow with transaction
        with transaction.atomic():
            outflow.origin = data['origin']
            outflow.destiny = data['destiny']
            outflow.updated_by = user.employeer
            outflow.save()
            
            # Delete existing items
            outflow.items.all().delete()
            
            # Create new items
            for item_data in data['items_data']:
                OutflowItems.objects.create(
                    outflow=outflow,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    companie=user.employeer.companie,
                    created_by=user.employeer,
                    updated_by=user.employeer
                )
            
            logger.info(f"Outflow updated successfully", extra={'outflow_id': outflow.id})
            return outflow
    
    def approve_outflow(self, outflow, user):
        """Approve an outflow"""
        # Validate outflow status
        self.validator.validate_outflow_status(outflow)
        
        # Validate outflow items
        self.validator.validate_outflow_items(outflow)
        
        # Approve outflow
        with transaction.atomic():
            outflow.status = 'approved'
            outflow.updated_by = user.employeer
            outflow.save()
            
            logger.info(f"Outflow approved successfully", extra={'outflow_id': outflow.id})
            return outflow
    
    def reject_outflow(self, outflow, user, rejection_reason):
        """Reject an outflow"""
        # Validate outflow status
        self.validator.validate_outflow_status(outflow)
        
        # Validate rejection reason
        self.validator.validate_rejection(rejection_reason)
        
        # Reject outflow
        outflow.status = 'rejected'
        outflow.rejection_reason = rejection_reason
        outflow.updated_by = user.employeer
        outflow.save()
        
        logger.info(f"Outflow rejected successfully", extra={'outflow_id': outflow.id})
        return outflow
