from .models import TimeTracking, Payroll, PayrollHistory, DaysTracking
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from decimal import Decimal
import datetime

logger = logging.getLogger(__name__)

def convert_to_date(date_value):
    """Helper function to convert string to date if needed"""
    if isinstance(date_value, str):
        return datetime.datetime.strptime(date_value, '%Y-%m-%d').date()
    return date_value

def convert_to_time(time_value):
    """Helper function to convert string to time if needed"""
    if isinstance(time_value, str):
        if 'T' in time_value:  # ISO format
            return datetime.datetime.fromisoformat(time_value).time()
        return datetime.datetime.strptime(time_value, '%H:%M:%S').time()
    return time_value

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
        
        # Ensure we have datetime objects
        clock_in = instance.clock_in if isinstance(instance.clock_in, datetime.datetime) else datetime.datetime.fromisoformat(instance.clock_in)
        clock_out = instance.clock_out if isinstance(instance.clock_out, datetime.datetime) else datetime.datetime.fromisoformat(instance.clock_out)
        
        # Calculate duration directly
        duration = clock_out - clock_in
        duration_hours = Decimal(str(duration.total_seconds() / 3600))
        
        if not payroll:
            # Calculate initial values for the first entry
            amount = duration_hours * Decimal(str(instance.employee.rate))
            
            payroll = Payroll.objects.create(
                employee=instance.employee,
                register=instance.register,
                period_start=clock_in.date(),
                period_end=clock_out.date(),
                amount=amount,
                days_worked=1 if clock_in.date() == clock_out.date() else 2,
                hours_worked=duration_hours.quantize(Decimal('0.01')),
                status='Pending',
            )
            logger.info(f'Hourly Payroll created successfully for {clock_in.date()}')
        else:
            # Update period range if needed
            if clock_out.date() > payroll.period_end:
                payroll.period_end = clock_out.date()
            if clock_in.date() < payroll.period_start:
                payroll.period_start = clock_in.date()
        
            # Get all time entries in the period
            time_entries = TimeTracking.objects.filter(
                employee=instance.employee,
                clock_in__date__gte=payroll.period_start,
                clock_in__date__lte=payroll.period_end,
                clock_out__isnull=False
            )
            
            # Calculate totals
            total_hours = Decimal('0.00')
            worked_days = set()
            
            for entry in time_entries:
                # Ensure we have datetime objects for each entry
                entry_clock_in = entry.clock_in if isinstance(entry.clock_in, datetime.datetime) else datetime.datetime.fromisoformat(entry.clock_in)
                entry_clock_out = entry.clock_out if isinstance(entry.clock_out, datetime.datetime) else datetime.datetime.fromisoformat(entry.clock_out)
                
                # Add all dates between clock_in and clock_out
                current_date = entry_clock_in.date()
                while current_date <= entry_clock_out.date():
                    worked_days.add(current_date)
                    current_date += datetime.timedelta(days=1)
                
                # Calculate hours directly
                entry_duration = entry_clock_out - entry_clock_in
                entry_hours = Decimal(str(entry_duration.total_seconds() / 3600))
                total_hours += entry_hours
            
            # Calculate amount based on total hours
            amount = total_hours * Decimal(str(instance.employee.rate))
            
            payroll.amount = amount
            payroll.days_worked = len(worked_days)
            payroll.hours_worked = total_hours.quantize(Decimal('0.01'))
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
        
        # Convert date and times if they're strings
        work_date = convert_to_date(instance.date)
        clock_in_time = convert_to_time(instance.clock_in)
        clock_out_time = convert_to_time(instance.clock_out)
        
        if not payroll:
            # Calculate initial values for the first entry
            clock_in_dt = datetime.datetime.combine(work_date, clock_in_time)
            clock_out_dt = datetime.datetime.combine(work_date, clock_out_time)
            duration = clock_out_dt - clock_in_dt
            duration_hours = Decimal(str(duration.total_seconds() / 3600))
            amount = Decimal(str(instance.employee.rate))
            
            payroll = Payroll.objects.create(
                employee=instance.employee,
                register=instance.register,
                period_start=work_date,
                period_end=work_date,
                amount=amount,
                days_worked=1,
                hours_worked=duration_hours.quantize(Decimal('0.01')),
                status='Pending',
            )
            logger.info(f'Daily Payroll created successfully for {work_date}')
        else:
            # Update period range if needed
            if work_date > payroll.period_end:
                payroll.period_end = work_date
            if work_date < payroll.period_start:
                payroll.period_start = work_date
            
            # Get all days entries in the period
            days_entries = DaysTracking.objects.filter(
                employee=instance.employee,
                date__gte=payroll.period_start,
                date__lte=payroll.period_end,
                clock_out__isnull=False
            )
            
            # Calculate totals
            total_hours = Decimal('0.00')
            worked_days = set()
            
            for entry in days_entries:
                entry_date = convert_to_date(entry.date)
                entry_clock_in = convert_to_time(entry.clock_in)
                entry_clock_out = convert_to_time(entry.clock_out)
                
                worked_days.add(entry_date)
                
                # Calculate actual hours worked
                clock_in_dt = datetime.datetime.combine(entry_date, entry_clock_in)
                clock_out_dt = datetime.datetime.combine(entry_date, entry_clock_out)
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
                    register=instance.register,
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
    