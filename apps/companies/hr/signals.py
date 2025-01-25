from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import WorkedDay, WorkHour, HR
from .services import HRService, WorkDayService, WorkHourService

logger = logging.getLogger(__name__)

@receiver(post_save, sender=HR)
def update_hr_payment_fields(sender, instance, created, **kwargs):
    """
    Signal to update HR payment fields when HR is saved.
    """
    # Evita chamadas recursivas
    if getattr(instance, '_skip_signal', False):
        return
        
    try:
        logger.info(f"[SIGNAL] - Updating payment fields for HR {instance.id}")
        
        # Marca o objeto para evitar chamadas recursivas
        instance._skip_signal = True
        
        if instance.payd_by_day:
            HR.objects.filter(id=instance.id).update(
                hourly_salary=0,
                monthly_salary=0,
                hours_worked=0
            )
            HRService.update_worked_days(instance)
            
        elif instance.payd_by_hour:
            HR.objects.filter(id=instance.id).update(
                daily_salary=0,
                monthly_salary=0,
                days_worked=0
            )
            HRService.update_worked_hours(instance)
            
        elif instance.payd_by_month:
            HR.objects.filter(id=instance.id).update(
                daily_salary=0,
                hourly_salary=0,
                days_worked=0,
                hours_worked=0
            )
            instance.current_period_amount = instance.monthly_salary
            instance.save(update_fields=['current_period_amount'])
            
        # Remove a marca
        delattr(instance, '_skip_signal')
            
    except Exception as e:
        logger.error(f"[SIGNAL] - Error updating payment fields for HR {instance.id}: {str(e)}")
        raise

@receiver([post_save, post_delete], sender=WorkHour)
def handle_work_hour_changes(sender, instance, **kwargs):
    """
    Signal to update HR when WorkHour is saved or deleted.
    """
    try:
        hr = instance.hr
        if hr.payd_by_hour and not getattr(hr, '_skip_signal', False):
            hr._skip_signal = True
            HRService.update_worked_hours(hr)
            delattr(hr, '_skip_signal')
    except Exception as e:
        logger.error(f"[SIGNAL] - Error handling WorkHour changes: {str(e)}")
        raise

@receiver([post_save, post_delete], sender=WorkedDay)
def handle_worked_day_changes(sender, instance, **kwargs):
    """
    Signal to update HR when WorkedDay is saved or deleted.
    """
    try:
        hr = instance.hr
        if hr.payd_by_day and not getattr(hr, '_skip_signal', False):
            hr._skip_signal = True
            HRService.update_worked_days(hr)
            delattr(hr, '_skip_signal')
    except Exception as e:
        logger.error(f"[SIGNAL] - Error handling WorkedDay changes: {str(e)}")
        raise