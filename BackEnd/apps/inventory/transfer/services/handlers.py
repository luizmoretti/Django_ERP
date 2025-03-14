from django.db import transaction
import logging
from .validators import TransferBusinessValidator
from ..models import Transfer, TransferItems

logger = logging.getLogger(__name__)

class TransferService:
    """Service class for Transfer operations"""
    
    def __init__(self):
        self.validator = TransferBusinessValidator()
    
    def create_transfer(self, data, user):
        """Create a new transfer"""
        # Validate company access
        self.validator.validate_company_access(data, user)
        
        # Validate different warehouses
        self.validator.validate_different_warehouses(data)
        
        # Create transfer with transaction
        with transaction.atomic():
            transfer = Transfer.objects.create(
                origin=data['origin'],
                destiny=data['destiny'],
                status='pending',
                companie=user.employeer.companie,
                created_by=user.employeer,
                updated_by=user.employeer
            )
            
            # Create transfer items
            for item_data in data['items_data']:
                TransferItems.objects.create(
                    transfer=transfer,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    companie=user.employeer.companie,
                    created_by=user.employeer,
                    updated_by=user.employeer
                )
            
            logger.info(f"[Transfer Service] Transfer created successfully", extra={'transfer_id': transfer.id})
            return transfer
    
    def update_transfer(self, transfer, data, user):
        """Update an existing transfer"""
        # Validate company access
        self.validator.validate_company_access(data, user)
        
        # Validate transfer status
        self.validator.validate_transfer_status(transfer)
        
        # Validate different warehouses
        self.validator.validate_different_warehouses(data)
        
        # Update transfer with transaction
        with transaction.atomic():
            transfer.origin = data['origin']
            transfer.destiny = data['destiny']
            transfer.updated_by = user.employeer
            transfer.save()
            
            # Delete existing items
            transfer.items.all().delete()
            
            # Create new items
            for item_data in data['items_data']:
                TransferItems.objects.create(
                    transfer=transfer,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    companie=user.employeer.companie,
                    created_by=user.employeer,
                    updated_by=user.employeer
                )
            
            logger.info(f"[Transfer Service] Transfer updated successfully", extra={'transfer_id': transfer.id})
            return transfer
    
    def approve_transfer(self, transfer, user):
        """Approve a transfer"""
        # Validate transfer status
        self.validator.validate_transfer_status(transfer)
        
        # Validate transfer items
        self.validator.validate_transfer_items(transfer)
        
        # Approve transfer
        with transaction.atomic():
            transfer.status = 'approved'
            transfer.updated_by = user.employeer
            transfer.save()
            
            logger.info(f"[Transfer Service] Transfer approved successfully", extra={'transfer_id': transfer.id})
            return transfer
    
    def reject_transfer(self, transfer, user, rejection_reason):
        """Reject a transfer"""
        # Validate transfer status
        self.validator.validate_transfer_status(transfer)
        
        # Validate rejection reason
        self.validator.validate_rejection(rejection_reason)
        
        # Reject transfer
        transfer.status = 'rejected'
        transfer.rejection_reason = rejection_reason
        transfer.updated_by = user.employeer
        transfer.save()
        
        logger.info(f"[Transfer Service] Transfer rejected successfully", extra={'transfer_id': transfer.id})
        return transfer