from .models import TimeTracking, Payroll, PayrollHistory, DaysTracking
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from decimal import Decimal
import datetime

logger = logging.getLogger(__name__)

@receiver(post_save, sender=TimeTracking)
def update_or_create_payroll_hourly(sender, instance, created, **kwargs):
    """
    Signal to automatically create or update a Payroll when a TimeTracking is saved.
    Updates both amount and hours worked based on actual clock in/out times.
    """
    try:
        if not instance.clock_out:
            return  # Skip if clock_out is not set
            
        # Find existing pending payroll for this employee
        payroll = Payroll.objects.filter(
            employee=instance.employee,
            status='Pending'
        ).first()
        
        if not payroll:
            # Calculate initial values for the first entry
            duration_hours = Decimal(str(instance.duration.total_seconds() / 3600))
            amount = duration_hours * Decimal(str(instance.employee.rate))
            
            payroll = Payroll.objects.create(
                employee=instance.employee,
                period_start=instance.clock_in.date(),
                period_end=instance.clock_out.date(),
                amount=amount,
                days_worked=1 if instance.clock_in.date() == instance.clock_out.date() else 2,
                hours_worked=duration_hours,
                status='Pending',
            )
            logger.info(f'Hourly Payroll created successfully for {instance.clock_in.date()}')
        else:
            # Update period range if needed
            if instance.clock_out.date() > payroll.period_end:
                payroll.period_end = instance.clock_out.date()
            if instance.clock_in.date() < payroll.period_start:
                payroll.period_start = instance.clock_in.date()
        
            # Get all time entries in the period
            time_entries = TimeTracking.objects.filter(
                employee=instance.employee,
                clock_in__date__gte=payroll.period_start,
                clock_in__date__lte=payroll.period_end,
                clock_out__isnull=False
            )
            
            # Calculate totals
            total_hours = Decimal('0')
            worked_days = set()
            
            for entry in time_entries:
                # Add all dates between clock_in and clock_out
                current_date = entry.clock_in.date()
                while current_date <= entry.clock_out.date():
                    worked_days.add(current_date)
                    current_date += datetime.timedelta(days=1)
                
                # Calculate hours
                duration_hours = Decimal(str(entry.duration.total_seconds() / 3600))
                total_hours += duration_hours
            
            # Calculate amount based on total hours
            amount = total_hours * Decimal(str(instance.employee.rate))
            
            payroll.amount = amount
            payroll.days_worked = len(worked_days)
            payroll.hours_worked = total_hours
            payroll.save()
            
            logger.info(f'Hourly Payroll updated successfully for period {payroll.period_start} to {payroll.period_end}')
            
    except Exception as e:
        logger.error(f"Error updating Payroll: {str(e)}", exc_info=True)
        

@receiver(post_save, sender=DaysTracking)
def update_or_create_payroll_daily(sender, instance, created, **kwargs):
    """
    Signal to automatically create or update a Payroll when a DaysTracking is saved.
    For daily workers, calculates total days worked and hours based on actual clock in/out times.
    """
    try:
        if not instance.clock_out:
            return  # Skip if clock_out is not set
            
        # Find existing pending payroll for this employee
        payroll = Payroll.objects.filter(
            employee=instance.employee,
            status='Pending'
        ).first()
        
        if not payroll:
            # Calculate initial values for the first entry
            # Convert time to datetime for duration calculation
            clock_in_dt = datetime.datetime.combine(instance.date, instance.clock_in)
            clock_out_dt = datetime.datetime.combine(instance.date, instance.clock_out)
            duration = clock_out_dt - clock_in_dt
            duration_hours = Decimal(str(duration.total_seconds() / 3600))
            amount = Decimal(str(instance.employee.rate))
            
            payroll = Payroll.objects.create(
                employee=instance.employee,
                period_start=instance.date,
                period_end=instance.date,
                amount=amount,
                days_worked=1,
                hours_worked=duration_hours.quantize(Decimal()),
                status='Pending',
            )
            logger.info(f'Daily Payroll created successfully for {instance.date}')
        else:
            # Update period range if needed
            if instance.date > payroll.period_end:
                payroll.period_end = instance.date
            if instance.date < payroll.period_start:
                payroll.period_start = instance.date
            
            # Get all days entries in the period
            days_entries = DaysTracking.objects.filter(
                employee=instance.employee,
                date__gte=payroll.period_start,
                date__lte=payroll.period_end,
                clock_out__isnull=False
            )
            
            # Calculate totals
            total_hours = Decimal()
            worked_days = set()
            
            for entry in days_entries:
                worked_days.add(entry.date)
                
                # Calculate actual hours worked
                clock_in_dt = datetime.datetime.combine(entry.date, entry.clock_in)
                clock_out_dt = datetime.datetime.combine(entry.date, entry.clock_out)
                duration = clock_out_dt - clock_in_dt
                duration_hours = Decimal(str(duration.total_seconds() / 3600))
                total_hours += duration_hours
            
            total_days = len(worked_days)
            amount = Decimal(str(instance.employee.rate)) * total_days
            
            payroll.amount = amount
            payroll.days_worked = total_days
            payroll.hours_worked = total_hours.quantize(Decimal('0.01'))
            payroll.save()
            
            logger.info(f'Daily Payroll updated successfully for period {payroll.period_start} to {payroll.period_end}')
            
    except Exception as e:
        logger.error(f"Error updating Daily Payroll: {str(e)}", exc_info=True)
        

@receiver(post_save, sender=Payroll)
def update_or_create_payroll_history(sender, instance, created, **kwargs):
    """
    Signal to automatically create or update a PayrollHistory when a Payroll change status to 'Paid'
    
    Args:
        sender: The model class (Payroll)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    try:
        payroll_history = PayrollHistory.objects.filter(payroll=instance).first()
        
        if instance.status == 'Paid':
            if not payroll_history:
                # Create and assign the new instance to payroll_history
                payroll_history = PayrollHistory.objects.create(
                    employee=instance.employee,
                    payroll=instance,
                    amount_paid=instance.amount,
                    payment_date=instance.period_end
                )
                logger.info(f"PayrollHistory created: {payroll_history.id}")
            else:
                # Update existing instance
                payroll_history.amount_paid += instance.amount
                payroll_history.payment_date = instance.period_end
                payroll_history.save()
                logger.info(f"PayrollHistory updated: {payroll_history.id}")
                
    except Exception as e:
        logger.error(f"Error updating or creating PayrollHistory: {str(e)}", exc_info=True)
    