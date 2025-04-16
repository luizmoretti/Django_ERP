from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from ..models import Inflow, InflowItems
from ..notifications.handlers import InflowNotificationHandler
from .validators import InflowBusinessValidator
from ...warehouse.models import WarehouseProduct
import logging

logger = logging.getLogger(__name__)

class InflowService:
    """
    Service class for handling Inflow business logic and persistence
    """
    
    def __init__(self):
        self.validator = InflowBusinessValidator()
    
    def create_inflow(self, data, user):
        """
        Create a new inflow with validation
        
        Args:
            data (dict): Data for creating inflow
            user: User creating the inflow
            
        Returns:
            Inflow: Created inflow instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate company access
        self.validator.validate_company_access(data, user)
        
        # Create inflow with transaction
        with transaction.atomic():
            # Create inflow
            inflow = Inflow.objects.create(
                origin=data['origin'],
                destiny=data['destiny'],
                status='pending',
                companie=user.employeer.companie,
                created_by=user.employeer,
                updated_by=user.employeer
            )
            
            # Create inflow items
            for item_data in data['items_data']:
                InflowItems.objects.create(
                    inflow=inflow,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    companie=user.employeer.companie,
                    created_by=user.employeer,
                    updated_by=user.employeer
                )
            
            logger.info(
                f"Inflow created successfully",
                extra={
                    'inflow_id': inflow.id,
                    'user_id': user.id
                }
            )
            
            return inflow
    
    def update_inflow(self, inflow, data, user):
        """
        Update an existing inflow with validation
        
        Args:
            inflow (Inflow): Inflow to update
            data (dict): Updated data
            user: User performing the update
            
        Returns:
            Inflow: Updated inflow instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate company access
        self.validator.validate_company_access(data, user)
        
        # Validate inflow status
        self.validator.validate_inflow_status(inflow)
        
        # Update inflow with transaction
        with transaction.atomic():
            # Update inflow fields
            inflow.origin = data['origin']
            inflow.destiny = data['destiny']
            inflow.updated_by = user.employeer
            inflow.save()
            
            # Delete existing items
            inflow.items.all().delete()
            
            # Create new items
            for item_data in data['items_data']:
                InflowItems.objects.create(
                    inflow=inflow,
                    product=item_data['product'],
                    quantity=item_data['quantity']
                )
            
            logger.info(
                f"[INFLOW SERVICE] Inflow updated successfully",
                extra={
                    'inflow_id': inflow.id,
                    'user_id': user.id
                }
            )
            
            return inflow
    
    def approve_inflow(self, inflow):
        """
        Approve an inflow with validation
        
        Args:
            inflow (Inflow): Inflow to approve
            user: User approving the inflow
            
        Returns:
            Inflow: Approved inflow instance
            
        Validations:
            - Validate inflow status
            - Validate inflow items
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inflow status
        self.validator.validate_inflow_status(inflow)
        
        # Validate inflow items
        self.validator.validate_inflow_items(inflow)
        
        # Approve inflow with transaction
        with transaction.atomic():
            # Update status
            inflow.status = 'approved'
            inflow.save()
            
            logger.info(
                f"[INFLOW SERVICE] Inflow approved successfully",
                extra={
                    'inflow_id': inflow.id
                }
            )
            
            return inflow
    
    def reject_inflow(self, inflow, rejection_reason):
        """
        Reject an inflow with validation
        
        Args:
            inflow (Inflow): Inflow to reject
            user: User rejecting the inflow
            rejection_reason (str): Reason for rejection
            
        Returns:
            Inflow: Rejected inflow instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inflow status
        self.validator.validate_inflow_status(inflow)
        
        # Validate rejection reason
        self.validator.validate_rejection(rejection_reason)
        
        # Reject inflow
        inflow.status = 'rejected'
        inflow.rejection_reason = rejection_reason
        inflow.save()
        
        logger.info(
            f"[INFLOW SERVICE] Inflow rejected successfully",
            extra={
                'inflow_id': inflow.id,
                'reason': rejection_reason
            }
        )
        
        return inflow
