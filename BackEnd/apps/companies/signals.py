from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Companie, PickUpCompanieAddress
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Companie)
def update_or_create_pickup_address(sender, instance, created, **kwargs):
    """
    Signal to automatically create or update a PickUpCompanieAddress when a Companie is saved.
    
    This signal handles both creation of new PickUpCompanieAddress for new Companies
    and updates to existing PickUpCompanieAddress when Company details change.
    
    Args:
        sender: The model class (Companie)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    try:
        pickup_address = PickUpCompanieAddress.objects.filter(companie=instance).first()
        
        if pickup_address:
            # Update existing pickup address
            pickup_address.full_address = f'{instance.address}, {instance.city}, {instance.state} {instance.zip_code}'
            pickup_address.save()
            logger.info(f'PickUpCompanieAddress updated successfully for company: {instance.name} [{instance.type}]')
        else:
            # Create new pickup address
            PickUpCompanieAddress.objects.create(
                companie=instance
            )
            action = "created" if created else "updated"
            logger.info(f'PickUpCompanieAddress {action} successfully for company: {instance.name} [{instance.type}]')
            
    except Exception as e:
        action = "creating" if created else "updating"
        logger.error(f'Error {action} PickUpCompanieAddress for company {instance.name}: {str(e)}')