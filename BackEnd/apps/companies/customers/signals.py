from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Customer, CustomerProjectAddress, CustomerBillingAddress, CustomerLeads
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Customer)
def create_customer_addresses(sender, instance, created, **kwargs):
    """
    Signal to automatically create CustomerProjectAddress and CustomerBillingAddress
    when a new Customer is created and their respective flags are False.
    
    Args:
        sender: The model class (Customer)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:  # Only run on new customer creation
        try:
            with transaction.atomic():
                # Create project address if another_shipping_address is False
                if not instance.another_shipping_address:
                    project_address = CustomerProjectAddress.objects.create(
                        customer=instance,
                        companie=instance.companie,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by
                    )
                    logger.info(f"[CUSTOMER SIGNAL] - Created project address for customer {instance.full_name()}")
                
                # Create billing address if another_billing_address is False
                if not instance.another_billing_address:
                    billing_address = CustomerBillingAddress.objects.create(
                        customer=instance,
                        companie=instance.companie,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by
                    )
                    logger.info(f"[CUSTOMER SIGNAL] - Created billing address for customer {instance.full_name()}")
                    
        except Exception as e:
            logger.error(f"[CUSTOMER SIGNAL] - Error creating addresses for customer {instance.full_name()}: {str(e)}")
            raise  # Re-raise the exception to ensure the transaction is rolled back