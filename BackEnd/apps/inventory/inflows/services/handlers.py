from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from ..models import Inflow, InflowItems
from ..notifications.handlers import InflowNotificationHandler
from .validators import InflowBusinessValidator
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
        Create a new inflow with its items
        
        Args:
            data (dict): Inflow data including items
            user: User creating the inflow
            
        Returns:
            Inflow: Created inflow instance
        """
        with transaction.atomic():
            # Validate business rules
            self.validator.validate_company_access(data, user)
            
            # Create inflow
            inflow = Inflow.objects.create(
                origin=data['origin'],
                destiny=data['destiny']
            )
            
            # Create inflow items
            items_data = data.pop('items_data', [])
            for item in items_data:
                InflowItems.objects.create(
                    inflow=inflow,
                    product=item['product'],
                    quantity=item['quantity']
                )
            
            logger.info(
                f"[INFLOW - CREATE] Inflow created successfully. ID: {inflow.id}",
                extra={
                    'inflow_id': inflow.id,
                    'user_id': user.id,
                    'company_id': user.employeer.companie.id
                }
            )
            
            return inflow
    
    def update_inflow(self, inflow, data, user):
        """
        Update an existing inflow and its items
        
        Args:
            inflow (Inflow): Inflow instance to update
            data (dict): Updated inflow data
            user: User updating the inflow
            
        Returns:
            Inflow: Updated inflow instance
        """
        with transaction.atomic():
            # Validate business rules
            self.validator.validate_company_access(data, user)
            self.validator.validate_inflow_status(inflow)
            
            # Update inflow fields
            inflow.origin = data.get('origin', inflow.origin)
            inflow.destiny = data.get('destiny', inflow.destiny)
            inflow.save()
            
            # Update items if provided
            if 'items_data' in data:
                # Remove existing items
                inflow.items.all().delete()
                
                # Create new items
                for item in data['items_data']:
                    InflowItems.objects.create(
                        inflow=inflow,
                        product=item['product'],
                        quantity=item['quantity']
                    )
            
            logger.info(
                f"[INFLOW SERVICES HANDLERS - UPDATE] Inflow updated successfully. ID: {inflow.id}",
                extra={
                    'inflow_id': inflow.id,
                    'user_id': user.id,
                    'company_id': user.employeer.companie.id
                }
            )
            
            return inflow
    
    def approve_inflow(self, inflow, user):
        """
        Approve an inflow
        
        Args:
            inflow (Inflow): Inflow to approve
            user: User approving the inflow
            
        Returns:
            Inflow: Approved inflow instance
        """
        with transaction.atomic():
            # Validate business rules
            self.validator.validate_company_access({'origin': inflow.origin, 'destiny': inflow.destiny}, user)
            self.validator.validate_inflow_status(inflow)
            self.validator.validate_inflow_items(inflow)
            
            # Update inflow status
            inflow.status = 'approved'
            inflow.save()
            
            # Update warehouse stock
            for item in inflow.items.all():
                item.product.update_stock(
                    warehouse=inflow.destiny,
                    quantity=item.quantity,
                    operation='add'
                )
            
            logger.info(
                f"[INFLOW SERVICES HANDLERS - APPROVE] Inflow approved successfully. ID: {inflow.id}",
                extra={
                    'inflow_id': inflow.id,
                    'user_id': user.id,
                    'company_id': user.employeer.companie.id
                }
            )
            
            return inflow
    
    def reject_inflow(self, inflow, user, rejection_reason):
        """
        Reject an inflow
        
        Args:
            inflow (Inflow): Inflow to reject
            user: User rejecting the inflow
            rejection_reason (str): Reason for rejection
            
        Returns:
            Inflow: Rejected inflow instance
        """
        with transaction.atomic():
            # Validate business rules
            self.validator.validate_company_access({'origin': inflow.origin, 'destiny': inflow.destiny}, user)
            self.validator.validate_inflow_status(inflow)
            self.validator.validate_rejection(rejection_reason)
            
            # Update inflow status
            inflow.status = 'rejected'
            inflow.rejection_reason = rejection_reason
            inflow.save()
            
            logger.info(
                f"[INFLOW SERVICES HANDLERS - REJECT] Inflow rejected successfully. ID: {inflow.id}",
                extra={
                    'inflow_id': inflow.id,
                    'user_id': user.id,
                    'company_id': user.employeer.companie.id,
                    'rejection_reason': rejection_reason
                }
            )
            
            return inflow
