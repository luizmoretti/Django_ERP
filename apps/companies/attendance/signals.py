from .models import TimeTracking, Payroll
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=TimeTracking)
def update_or_create_payroll(sender, instance, created, **kwargs):
    """
    Signal to automatically create or update a Payroll when a TimeTracking is saved.
    
    This signal handles both creation of new Payroll for new TimeTrackings
    and updates to existing Payroll when TimeTracking details change.
    
    Args:
        sender: The model class (TimeTracking)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    try:
        payroll = Payroll.objects.filter(employee=instance.employee).first()
        # Create new Payroll
        if not payroll:
            if instance.employee.payment_type == 'Hour':
                payroll = Payroll.objects.create(
                    employee=instance.employee,
                    period_start=instance.clock_in.date(),
                    period_end=instance.clock_in.date(),
                    amount=instance.duration.total_seconds() / 3600 * float(instance.employee.rate),
                    status='Pending',
                ) 
            elif instance.employee.payment_type == 'Day':
                payroll = Payroll.objects.create(
                    employee=instance.employee,
                    period_start=instance.clock_in.date(),
                    period_end=instance.clock_in.date(),
                    amount=instance.employee.rate,
                    status='Pending',
                )
            logger.info(f'Payroll Created for employer: {instance.employee.name}')
        else:
            # Update existing Payroll
            if instance.employee.payment_type == 'Hour':
                payroll.amount += instance.duration.total_seconds() / 3600 * float(instance.employee.rate)
            
            elif instance.employee.payment_type == 'Day':
                payroll.amount += instance.employee.rate
            payroll.save()
            
        logger.info(f"Payroll updated: {payroll.id}")
    
    except Exception as e:
        logger.error(f"Error updating Payroll: {str(e)}", exc_info=True)