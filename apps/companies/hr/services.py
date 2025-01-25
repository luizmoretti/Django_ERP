from datetime import datetime, date, timedelta, time
from typing import Optional, List, Tuple, Union
from django.db.models import Sum, F, Q
from django.utils import timezone
import logging
from decimal import Decimal
from .models import WorkedDay, WorkHour, HR, PaymentHistory, WorkHistory

logger = logging.getLogger(__name__)

class DateUtils:
    """Utility class for handling date-related operations."""
    
    @staticmethod
    def is_business_day(day: date) -> bool:
        """Check if a given date is a business day (Monday-Friday)."""
        return day.weekday() < 5
    
    @staticmethod
    def get_next_business_day(from_date: date) -> date:
        """Get the next business day after the given date."""
        next_day = from_date + timedelta(days=1)
        while not DateUtils.is_business_day(next_day):
            next_day += timedelta(days=1)
        return next_day
    
    @staticmethod
    def get_business_days_between(start_date: date, end_date: date) -> int:
        """Count business days between two dates."""
        current_date = start_date
        business_days = 0
        while current_date <= end_date:
            if DateUtils.is_business_day(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        return business_days

class WorkRecordService:
    """Base service class for work record operations."""
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> None:
        """Validate a date range."""
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        if end_date > timezone.now().date():
            raise ValueError("End date cannot be in the future")

class WorkDayService(WorkRecordService):
    """Service for handling worked days records."""
    
    @staticmethod
    def calculate_total_days(hr_instance) -> int:
        """Calculate total worked days for an HR instance."""
        try:
            total_days = hr_instance.worked_days.count()
            logger.info(f"[SERVICE] Calculated {total_days} total days for HR {hr_instance.id}")
            return total_days
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating total days: {str(e)}")
            return 0
    
    @staticmethod
    def update_last_worked_dates(hr_instance) -> None:
        """Update last worked day date for an HR instance."""
        try:
            last_day = hr_instance.worked_days.order_by('-date').first()
            if last_day:
                hr_instance.last_day_registered = last_day.date
                hr_instance.save(update_fields=['last_day_registered'])
                logger.info(f"[SERVICE] Updated last worked day to {last_day.date} for HR {hr_instance.id}")
        except Exception as e:
            logger.error(f"[SERVICE] Error updating last worked dates: {str(e)}")

    @staticmethod
    def get_worked_days_in_period(hr_instance, start_date: date, end_date: date) -> List[date]:
        """Get list of worked days in a specific period."""
        try:
            WorkRecordService.validate_date_range(start_date, end_date)
            days = hr_instance.worked_days.filter(
                date__gte=start_date,
                date__lte=end_date
            ).values_list('date', flat=True)
            return list(days)
        except Exception as e:
            logger.error(f"[SERVICE] Error getting worked days in period: {str(e)}")
            return []
        
    @staticmethod
    def days_worked_list(hr_instance) -> List[date]:
        """
        Return a list with the dates worked.
        """
        try:
            return WorkedDay.objects.filter(hr=hr_instance).values_list('date', flat=True)
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating days worked: {str(e)}")
            raise

class WorkHourService(WorkRecordService):
    """Service for handling worked hours records."""
    
    @staticmethod
    def calculate_total_hours(hr_instance) -> Decimal:
        """Calculate total worked hours for an HR instance."""
        try:
            total_hours = hr_instance.worked_hours.aggregate(
                total=Sum('hours')
            )['total'] or Decimal('0')
            logger.info(f"[SERVICE] Calculated {total_hours} total hours for HR {hr_instance.id}")
            return Decimal(str(total_hours))
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating total hours: {str(e)}")
            return Decimal('0')
        
    @staticmethod
    def hours_worked_list(hr_instance) -> List[Tuple[date, time, time, Decimal]]:
        """
        Return a list with the hours worked.
        """
        try:
            return WorkHour.objects.filter(hr=hr_instance).values_list('date', 'start_time', 'end_time')
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating hours worked: {str(e)}")
            raise
    
    @staticmethod
    def get_last_worked_hour(hr_instance) -> Optional[datetime]:
        """Get the last worked hour record datetime."""
        try:
            last_hour = hr_instance.worked_hours.order_by('-date', '-end_time').first()
            if last_hour:
                return datetime.combine(last_hour.date, last_hour.end_time)
            return None
        except Exception as e:
            logger.error(f"[SERVICE] Error getting last worked hour: {str(e)}")
            return None
    
    @staticmethod
    def update_last_worked_dates(hr_instance) -> None:
        """Update last worked hour datetime for an HR instance."""
        try:
            last_hour = WorkHourService.get_last_worked_hour(hr_instance)
            if last_hour:
                hr_instance.last_hours_registered = last_hour
                hr_instance.save(update_fields=['last_hours_registered'])
                logger.info(f"[SERVICE] Updated last hours registered to {last_hour} for HR {hr_instance.id}")
        except Exception as e:
            logger.error(f"[SERVICE] Error updating last worked dates: {str(e)}")
    
    @staticmethod
    def get_worked_hours_in_period(hr_instance, start_date: date, end_date: date) -> List[Tuple[date, time, time, Decimal]]:
        """Get list of worked hours in a specific period."""
        try:
            WorkRecordService.validate_date_range(start_date, end_date)
            hours = hr_instance.worked_hours.filter(
                date__gte=start_date,
                date__lte=end_date
            ).values_list('date', 'start_time', 'end_time', 'hours')
            return list(hours)
        except Exception as e:
            logger.error(f"[SERVICE] Error getting worked hours in period: {str(e)}")
            return []

class PaymentService:
    """Service for handling payment-related operations."""
    
    @staticmethod
    def calculate_next_payment_date(hr_instance, force_today: bool = False) -> Optional[date]:
        """Calculate next payment date based on payment settings."""
        try:
            if not hr_instance.payment_interval or not hr_instance.payment_business_day:
                logger.warning(f"[SERVICE] No payment business day configured for HR {hr_instance.id}")
                return None
                
            # Determine the base date for the calculation
            reference_date = None
            
            # If force_today=True, use the current date
            if force_today:
                reference_date = timezone.now().date()
            else:
                # Try using the last registered date
                if hr_instance.payd_by_hour and hr_instance.last_hours_registered:
                    reference_date = hr_instance.last_hours_registered.date()
                elif hr_instance.payd_by_day and hr_instance.last_day_registered:
                    reference_date = hr_instance.last_day_registered
                
                # If no registered date, use the current date
                if not reference_date:
                    reference_date = timezone.now().date()
            
            logger.info(f"[SERVICE] Calculating next payment date for HR {hr_instance.id}. "
                       f"Payment interval: {hr_instance.payment_interval}, "
                       f"Business day: {hr_instance.payment_business_day}, "
                       f"Reference date: {reference_date}")
            
            next_date = None
            
            # Calculate next payment date based on interval
            if hr_instance.payment_interval == 'daily':
                # For daily payment, next date is the next business day
                next_date = reference_date + timedelta(days=1)
                # If it's the end of the week, move to the next Monday
                while next_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                    next_date += timedelta(days=1)
                    
            elif hr_instance.payment_interval == 'weekly':
                # payment_business_day is 1-based (1 = Monday, 2 = Tuesday, etc)
                # weekday() is 0-based (0 = Monday, 1 = Tuesday, etc)
                target_weekday = hr_instance.payment_business_day - 1
                
                # Calculate how many days until the target day
                days_ahead = target_weekday - reference_date.weekday()
                if days_ahead <= 0:  # If already passed the target day this week, move to next
                    days_ahead += 7
                next_date = reference_date + timedelta(days=days_ahead)
                
                # If the calculated date is before the reference date, add a week
                if next_date <= reference_date:
                    next_date += timedelta(days=7)
                
                # If it's the end of the week, move to the next Monday
                while next_date.weekday() >= 5:
                    next_date += timedelta(days=1)
                    
            elif hr_instance.payment_interval == 'biweekly':
                # payment_business_day is 1-based (1 = Monday, 2 = Tuesday, etc)
                # weekday() is 0-based (0 = Monday, 1 = Tuesday, etc)
                target_weekday = hr_instance.payment_business_day - 1
                
                # Calculate how many days until the target day
                days_ahead = target_weekday - reference_date.weekday()
                if days_ahead <= 0:  # If already passed the target day this week, move to next week
                    days_ahead += 14
                next_date = reference_date + timedelta(days=days_ahead)
                
                # If the calculated date is before the reference date, add a week
                if next_date <= reference_date:
                    next_date += timedelta(days=14)
                
                # Check if we're in the correct week (even or odd)
                if (next_date.isocalendar()[1] % 2) == (reference_date.isocalendar()[1] % 2):
                    next_date += timedelta(days=0)
                
                # If it's the end of the week, move to the next Monday
                while next_date.weekday() >= 5:
                    next_date += timedelta(days=1)
                    
            else:  # monthly
                # Find the next occurrence of payment_business_day in the month
                if reference_date.day >= hr_instance.payment_business_day:  # If already passed the payment day
                    if reference_date.month == 12:
                        next_date = reference_date.replace(year=reference_date.year + 1, month=1, day=1)
                    else:
                        next_date = reference_date.replace(month=reference_date.month + 1, day=1)
                else:
                    next_date = reference_date.replace(day=1)
                
                # Adjust for payday
                try:
                    next_date = next_date.replace(day=hr_instance.payment_business_day)
                except ValueError:  # If the day doesn't exist in this month
                    if next_date.month == 12:
                        next_date = next_date.replace(year=next_date.year + 1, month=1, day=1)
                    else:
                        next_date = next_date.replace(month=next_date.month + 1, day=1)
                    next_date -= timedelta(days=1)
                
                # If it's the end of the week, move to the next Monday
                while next_date.weekday() >= 5:
                    next_date += timedelta(days=1)
            
            # If the calculated date is before the current date and we're not forcing today,
            # recalculate from today
            today = timezone.now().date()
            if next_date <= today:
                if not force_today:
                    # Recalculate using the current date as a reference
                    next_date = PaymentService.calculate_next_payment_date(hr_instance, force_today=True)
                else:
                    # If we're already using the current date and the calculated date is still in the past,
                    # add an interval
                    if hr_instance.payment_interval == 'daily':
                        next_date += timedelta(days=1)
                    elif hr_instance.payment_interval == 'weekly':
                        next_date += timedelta(days=7)
                    elif hr_instance.payment_interval == 'biweekly':
                        next_date += timedelta(days=14)
                    else:  # monthly
                        if next_date.month == 12:
                            next_date = next_date.replace(year=next_date.year + 1, month=1)
                        else:
                            next_date = next_date.replace(month=next_date.month + 1)
            
            logger.info(f"[SERVICE] Next payment date for HR {hr_instance.id}: {next_date}")
            return next_date
            
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating next payment date: {str(e)}")
            return None
    
    @staticmethod
    def calculate_current_period_amount(hr_instance) -> Decimal:
        """Calculate amount to be paid for current period."""
        try:
            if hr_instance.payd_by_day:
                total_days = WorkDayService.calculate_total_days(hr_instance)
                return Decimal(str(total_days)) * Decimal(str(hr_instance.daily_salary))
            elif hr_instance.payd_by_hour:
                total_hours = WorkHourService.calculate_total_hours(hr_instance)
                return total_hours * Decimal(str(hr_instance.hourly_salary))
            elif hr_instance.payd_by_month:
                return Decimal(str(hr_instance.monthly_salary))
            return Decimal('0')
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating current period amount: {str(e)}")
            return Decimal('0')
    
    @staticmethod
    def process_payment(hr_instance) -> bool:
        """Process payment for an HR instance.
        
        1. Validate payment conditions
        2. Create payment history record
        3. Store work history
        4. Update HR total_paid and clear current records
        5. Update payment dates
        """
        from .models import PaymentHistory, WorkHistory
        from django.db import transaction
        
        try:
            # Validate if there's amount to pay
            if hr_instance.current_period_amount <= 0:
                logger.warning(f"[SERVICE] No amount to pay for HR {hr_instance.id}")
                return False
            
            with transaction.atomic():
                # Determine payment type
                payment_type = None
                if hr_instance.payd_by_day:
                    payment_type = 'Daily'
                elif hr_instance.payd_by_hour:
                    payment_type = 'Hourly'
                elif hr_instance.payd_by_month:
                    payment_type = 'Monthly'
                else:
                    logger.error(f"[SERVICE] Invalid payment type for HR {hr_instance.id}")
                    return False
                
                # 1. Create payment history record
                payment_history = PaymentHistory.objects.create(
                    hr=hr_instance,
                    amount_paid=hr_instance.current_period_amount,
                    payment_type=payment_type
                )
                logger.info(f"[SERVICE] Created payment history for HR {hr_instance.id}")
                
                # 2. Store work history
                if hr_instance.payd_by_day:
                    # Get all worked days
                    worked_days = hr_instance.worked_days.all()
                    for day in worked_days:
                        WorkHistory.objects.create(
                            payment=payment_history,
                            date=day.date
                        )
                    logger.info(f"[SERVICE] Stored {worked_days.count()} days in work history")
                    
                elif hr_instance.payd_by_hour:
                    # Get all worked hours
                    worked_hours = hr_instance.worked_hours.all()
                    for hour in worked_hours:
                        WorkHistory.objects.create(
                            payment=payment_history,
                            date=hour.date,
                            start_time=hour.start_time,
                            end_time=hour.end_time,
                            hours=hour.hours
                        )
                    logger.info(f"[SERVICE] Stored {worked_hours.count()} hours in work history")
                
                # 3. Update HR and clear records
                # Update total paid
                hr_instance.total_paid = F('total_paid') + hr_instance.current_period_amount
                
                # Clear current records
                if hr_instance.payd_by_day:
                    hr_instance.worked_days.all().delete()
                    hr_instance.days_worked = 0
                elif hr_instance.payd_by_hour:
                    hr_instance.worked_hours.all().delete()
                    hr_instance.hours_worked = 0
                
                # 4. Update payment dates
                hr_instance.last_payment_date = timezone.now().date()
                hr_instance.next_payment_date = PaymentService.calculate_next_payment_date(hr_instance)
                hr_instance.current_period_amount = 0
                
                hr_instance.save()
                logger.info(f"[SERVICE] Successfully processed payment for HR {hr_instance.id}")
                
                return True
                
        except Exception as e:
            logger.error(f"[SERVICE] Error processing payment for HR {hr_instance.id}: {str(e)}")
            return False

class HRService:
    """Service for handling HR record operations."""
    
    @staticmethod
    def update_worked_hours(hr_instance) -> None:
        """Update total worked hours and current period amount."""
        try:
            total_hours = WorkHourService.calculate_total_hours(hr_instance)
            current_amount = total_hours * Decimal(str(hr_instance.hourly_salary))
            next_payment = PaymentService.calculate_next_payment_date(hr_instance)
            
            hr_instance.hours_worked = total_hours
            hr_instance.current_period_amount = current_amount
            hr_instance.next_payment_date = next_payment
            hr_instance.save(update_fields=['hours_worked', 'current_period_amount', 'next_payment_date'])
            
            # Update last_hours_registered
            WorkHourService.update_last_worked_dates(hr_instance)
            
            logger.info(f"[SERVICE] Updated worked hours to {total_hours} and amount to {current_amount} for HR {hr_instance.id}")
        except Exception as e:
            logger.error(f"[SERVICE] Error updating worked hours: {str(e)}")
            
    @staticmethod
    def update_worked_days(hr_instance) -> None:
        """Update total worked days and current period amount."""
        try:
            total_days = WorkDayService.calculate_total_days(hr_instance)
            current_amount = Decimal(str(total_days)) * Decimal(str(hr_instance.daily_salary))
            next_payment = PaymentService.calculate_next_payment_date(hr_instance)
            
            hr_instance.days_worked = total_days
            hr_instance.current_period_amount = current_amount
            hr_instance.next_payment_date = next_payment
            hr_instance.save(update_fields=['days_worked', 'current_period_amount', 'next_payment_date'])
            
            logger.info(f"[SERVICE] Updated worked days to {total_days} and amount to {current_amount} for HR {hr_instance.id}")
        except Exception as e:
            logger.error(f"[SERVICE] Error updating worked days: {str(e)}")
    
    @staticmethod
    def get_payment_status(hr_instance) -> str:
        """Get current payment status."""
        try:
            if not hr_instance.payment_interval or not hr_instance.payment_business_day:
                return "Payment schedule not configured"
                
            if not hr_instance.next_payment_date:
                next_date = PaymentService.calculate_next_payment_date(hr_instance)
                if next_date:
                    hr_instance.next_payment_date = next_date
                    hr_instance.save(update_fields=['next_payment_date'])
            
            if hr_instance.next_payment_date and hr_instance.next_payment_date <= timezone.now().date():
                return "Payment Due"
            
            return "Up to date"
        except Exception as e:
            logger.error(f"[SERVICE] Error getting payment status: {str(e)}")
            return "Error checking payment status"
    
    @staticmethod
    def get_work_status(hr_instance) -> str:
        """Get current work status based on payment type."""
        try:
            if hr_instance.payd_by_day:
                total_days = WorkDayService.calculate_total_days(hr_instance)
                return f"{total_days} days worked"
            elif hr_instance.payd_by_hour:
                total_hours = WorkHourService.calculate_total_hours(hr_instance)
                return f"{total_hours} hours worked"
            elif hr_instance.payd_by_month:
                if hr_instance.last_payment_date:
                    business_days = DateUtils.get_business_days_between(
                        hr_instance.last_payment_date,
                        timezone.now().date()
                    )
                    return f"{business_days} business days since last payment"
                return "No payments recorded"
            return "Payment type not configured"
        except Exception as e:
            logger.error(f"[SERVICE] Error getting work status: {str(e)}")
            return "Error checking work status"