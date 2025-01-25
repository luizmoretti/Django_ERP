from django.db import transaction
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import HR, WorkHour, WorkedDay, PaymentHistory, WorkHistory
from django.db.models import Sum, F
import logging

logger = logging.getLogger(__name__)

class HRService:
    @staticmethod
    def create_hr(data, user):
        """
        Create a new HR record with validation and logging.
        """
        try:
            data['made_by'] = user
            
            with transaction.atomic():
                # Create HR instance
                hr = HR.objects.create(**data)
                
                # Calculate and update next payment date
                next_payment_date = PaymentService.calculate_next_payment_date(hr)
                if next_payment_date:
                    hr.next_payment_date = next_payment_date
                    hr.save()
                
                logger.info(f"[SERVICE] Created HR record {hr.id}")
                return hr
                
        except Exception as e:
            logger.error(f"[SERVICE] Error creating HR record: {str(e)}")
            raise

    @staticmethod
    def update_hr(hr_instance, data):
        """
        Update HR record with validation.
        """
        try:
            with transaction.atomic():
                # Update HR instance
                for key, value in data.items():
                    setattr(hr_instance, key, value)
                hr_instance.save()
                
                # Calculate and update next payment date
                next_payment_date = PaymentService.calculate_next_payment_date(hr_instance)
                if next_payment_date:
                    hr_instance.next_payment_date = next_payment_date
                    hr_instance.save()
                
                logger.info(f"[SERVICE] Updated HR record {hr_instance.id}")
                return hr_instance
                
        except Exception as e:
            logger.error(f"[SERVICE] Error updating HR record: {str(e)}")
            raise

    @staticmethod
    def calculate_payment(hr_instance):
        """
        Calculate payment based on payment type and worked time.
        """
        try:
            if hr_instance.payd_by_hour:
                return hr_instance.hours_worked * hr_instance.hourly_salary
            elif hr_instance.payd_by_day:
                return hr_instance.days_worked * hr_instance.daily_salary
            elif hr_instance.payd_by_month:
                return hr_instance.monthly_salary
            return 0
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating payment: {str(e)}")
            raise
    
    @staticmethod
    def update_worked_hours(hr_instance):
        """
        Update HR hours_worked and current_period_amount.
        """
        try:
            logger.info(f"[SERVICE] Updating hours worked for HR {hr_instance.id}")
            
            with transaction.atomic():
                total_hours = WorkHour.objects.filter(hr=hr_instance).aggregate(
                    total=Sum('hours')
                )['total'] or 0
                
                HR.objects.filter(id=hr_instance.id).update(
                    hours_worked=total_hours,
                    current_period_amount=total_hours * F('hourly_salary'),
                    last_hours_registered=timezone.now()
                )
                hr_instance.refresh_from_db()
                
            logger.info(f"[SERVICE] Successfully updated HR {hr_instance.id} hours to {total_hours}")
            return hr_instance
            
        except Exception as e:
            logger.error(f"[SERVICE] Error updating hours worked for HR {hr_instance.id}: {str(e)}")
            raise

    @staticmethod
    def update_worked_days(hr_instance):
        """
        Update HR days_worked and current_period_amount.
        """
        try:
            logger.info(f"[SERVICE] Updating days worked for HR {hr_instance.id}")
            
            with transaction.atomic():
                total_days = WorkedDay.objects.filter(hr=hr_instance).count()
                
                HR.objects.filter(id=hr_instance.id).update(
                    days_worked=total_days,
                    current_period_amount=total_days * F('daily_salary'),
                    last_day_registered=timezone.now()
                )
                hr_instance.refresh_from_db()
                
            logger.info(f"[SERVICE] Successfully updated HR {hr_instance.id} days to {total_days}")
            return hr_instance
            
        except Exception as e:
            logger.error(f"[SERVICE] Error updating days worked for HR {hr_instance.id}: {str(e)}")
            raise

    @staticmethod
    def update_monthly_amount(hr_instance):
        """
        Update HR current_period_amount for monthly payment.
        """
        try:
            logger.info(f"[SERVICE] Updating monthly amount for HR {hr_instance.id}")
            
            with transaction.atomic():
                HR.objects.filter(id=hr_instance.id).update(
                    current_period_amount=F('monthly_salary')
                )
                hr_instance.refresh_from_db()
                
            logger.info(f"[SERVICE] Successfully updated HR {hr_instance.id} monthly amount")
            return hr_instance
            
        except Exception as e:
            logger.error(f"[SERVICE] Error updating monthly amount for HR {hr_instance.id}: {str(e)}")
            raise
class WorkHourService:
    """Service class for handling worked hours operations."""

    @staticmethod
    def register_worked_hours(hr_instance, date, start_time=None, end_time=None, hours=None):
        """
        Register worked hours and update HR instance.
        
        Args:
            hr_instance (HR): The HR instance to register hours for.
            date (date): The date worked.
            start_time (time, optional): Start time of work.
            end_time (time, optional): End time of work.
            hours (Decimal, optional): Hours worked if not using start/end time.
            
        Returns:
            tuple: (WorkHour, HR) The created WorkHour and updated HR instance.
        """
        try:
            with transaction.atomic():
                # Create worked hour
                worked_hour = WorkHour.objects.create(
                    hr=hr_instance,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    hours=hours
                )
                logger.info(f"[SERVICE] Created worked hour for HR {hr_instance.id}: {date}")
                
                # Update HR instance
                hr_instance.hours_worked += worked_hour.hours
                if hr_instance.payd_by_hour:
                    hr_instance.current_period_amount += (hr_instance.hourly_salary * worked_hour.hours)
                
                # Update last worked dates
                WorkHourService.update_last_worked_dates(hr_instance)
                hr_instance.save()
                
                logger.info(f"[SERVICE] Successfully registered worked hours for HR {hr_instance.id}")
                return worked_hour, hr_instance
                
        except Exception as e:
            logger.error(f"[SERVICE] Error registering worked hours for HR {hr_instance.id}: {str(e)}")
            raise

    @staticmethod
    def calculate_total_hours(hr_instance, start_date=None, end_date=None):
        """
        Calculate total hours worked in a period.
        """
        try:
            query = WorkHour.objects.filter(hr=hr_instance)
            if start_date:
                query = query.filter(date__gte=start_date)
            if end_date:
                query = query.filter(date__lte=end_date)
            
            total_hours = sum(wh.hours or 0 for wh in query)
            logger.info(f"[SERVICE] Calculated total hours: {total_hours}")
            return total_hours
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating total hours: {str(e)}")
            raise
        
    @staticmethod
    def hours_worked_list(hr_instance):
        """ 
        Return a list with the dates, start_time and end_time worked.
        """
        try:
            return WorkHour.objects.filter(hr=hr_instance).values_list('date', 'start_time', 'end_time')
        except Exception as e:
            logger.error(f"[SERVICE] Error getting hours worked list: {str(e)}")
            raise

    @staticmethod
    def get_last_worked_hour(hr_instance):
        """
        Get the last worked hour from WorkHour model.
        
        Args:
            hr_instance (HR): The HR instance to get last worked hour for.
            
        Returns:
            datetime: The last worked hour or None if no hours worked.
        """
        try:
            last_hour = WorkHour.objects.filter(hr=hr_instance).order_by('-date', '-end_time').first()
            if last_hour:
                # Combine date with end_time for full datetime
                if last_hour.end_time:
                    last_datetime = datetime.combine(last_hour.date, last_hour.end_time)
                    logger.info(f"[SERVICE] Found last worked hour for HR {hr_instance.id}: {last_datetime}")
                    return last_datetime
                
                logger.info(f"[SERVICE] Found last worked day for HR {hr_instance.id}: {last_hour.date}")
                return datetime.combine(last_hour.date, time.max)
            
            logger.info(f"[SERVICE] No worked hours found for HR {hr_instance.id}")
            return None
            
        except Exception as e:
            logger.error(f"[SERVICE] Error getting last worked hour for HR {hr_instance.id}: {str(e)}")
            return None

    @staticmethod
    def update_last_worked_dates(hr_instance):
        """
        Update last_hours_registered based on WorkHour model.
        
        Args:
            hr_instance (HR): The HR instance to update dates for.
            
        Returns:
            HR: The updated HR instance.
        """
        try:
            with transaction.atomic():
                last_hour = WorkHourService.get_last_worked_hour(hr_instance)
                if last_hour:
                    HR.objects.filter(id=hr_instance.id).update(last_hours_registered=last_hour)
                    hr_instance.refresh_from_db()
                    logger.info(f"[SERVICE] Successfully updated last hours registered for HR {hr_instance.id}")
                else:
                    logger.warning(f"[SERVICE] No worked hours to update for HR {hr_instance.id}")
                
                return hr_instance
                
        except Exception as e:
            logger.error(f"[SERVICE] Error updating last worked hours for HR {hr_instance.id}: {str(e)}")
            raise

class WorkDayService:
    """Service class for handling worked days operations."""
    
    @staticmethod
    def create_worked_day(hr_instance, data):
        """Criar registro de dia trabalhado e atualizar HR"""
        try:
            with transaction.atomic():
                # Criar registro
                worked_day = WorkedDay.objects.create(
                    hr=hr_instance,
                    date=data.get('date')
                )
                logger.info(f"[SERVICE] Created worked day for HR {hr_instance.id}: {data.get('date')}")
                
                # Atualizar HR
                total_days = WorkedDay.objects.filter(hr=hr_instance).count()
                hr_instance.days_worked = total_days
                hr_instance.current_period_amount = total_days * hr_instance.daily_salary
                
                # Atualizar última data registrada
                last_day = WorkDayService.get_last_worked_day(hr_instance)
                if last_day:
                    hr_instance.last_day_registered = last_day
                    logger.info(f"[SERVICE] Updated last day registered for HR {hr_instance.id} to {last_day}")
                else:
                    logger.warning(f"[SERVICE] No last day found for HR {hr_instance.id}")
                
                hr_instance.save()
                logger.info(f"[SERVICE] Successfully updated HR {hr_instance.id}")
                
                return worked_day
                
        except Exception as e:
            logger.error(f"[SERVICE] Error creating worked day for HR {hr_instance.id}: {str(e)}")
            raise
    
    @staticmethod
    def register_worked_day(hr_instance, date):
        """
        Register a worked day for an employee.
        """
        try:
            worked_day = WorkedDay.objects.create(
                hr=hr_instance,
                date=date
            )
            logger.info(f"[SERVICE] Registered worked day for {hr_instance.employeer} on {date}")
            return worked_day
        except Exception as e:
            logger.error(f"[SERVICE] Error registering worked day: {str(e)}")
            raise

    @staticmethod
    def calculate_total_days(hr_instance, start_date=None, end_date=None):
        """
        Calculate total days worked in a period.
        """
        try:
            query = WorkedDay.objects.filter(hr=hr_instance)
            if start_date:
                query = query.filter(date__gte=start_date)
            if end_date:
                query = query.filter(date__lte=end_date)
            
            total_days = query.count()
            logger.info(f"[SERVICE] Calculated total days: {total_days}")
            return total_days
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating total days: {str(e)}")
            raise
        
    @staticmethod
    def days_worked_list(hr_instance):
        """
        Return a list with the dates worked.
        """
        try:
            return WorkedDay.objects.filter(hr=hr_instance).values_list('date', flat=True)
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating days worked: {str(e)}")
            raise

    @staticmethod
    def get_last_worked_day(hr_instance):
        """
        Get the last worked day from WorkedDay model.
        
        Args:
            hr_instance (HR): The HR instance to get last worked day for.
            
        Returns:
            date: The last worked day or None if no days worked.
        """
        try:
            last_day = WorkedDay.objects.filter(hr=hr_instance).order_by('-date').first()
            if last_day:
                logger.info(f"[SERVICE] Found last worked day for HR {hr_instance.id}: {last_day.date}")
                return last_day.date
            
            logger.info(f"[SERVICE] No worked days found for HR {hr_instance.id}")
            return None
            
        except Exception as e:
            logger.error(f"[SERVICE] Error getting last worked day for HR {hr_instance.id}: {str(e)}")
            return None

    @staticmethod
    def update_last_worked_dates(hr_instance):
        """
        Update last_day_registered based on WorkedDay model.
        
        Args:
            hr_instance (HR): The HR instance to update dates for.
            
        Returns:
            HR: The updated HR instance.
        """
        try:
            with transaction.atomic():
                last_day = WorkDayService.get_last_worked_day(hr_instance)
                if last_day:
                    HR.objects.filter(id=hr_instance.id).update(last_day_registered=last_day)
                    hr_instance.refresh_from_db()
                    logger.info(f"[SERVICE] Successfully updated last day registered for HR {hr_instance.id}")
                else:
                    logger.warning(f"[SERVICE] No worked days to update for HR {hr_instance.id}")
                
                return hr_instance
                
        except Exception as e:
            logger.error(f"[SERVICE] Error updating last worked day for HR {hr_instance.id}: {str(e)}")
            raise

    @staticmethod
    def register_worked_day(hr_instance, date):
        """
        Register a worked day and update HR instance.
        
        Args:
            hr_instance (HR): The HR instance to register day for.
            date (date): The date to register.
            
        Returns:
            tuple: (WorkedDay, HR) The created WorkedDay and updated HR instance.
        """
        try:
            with transaction.atomic():
                # Create worked day
                worked_day = WorkedDay.objects.create(hr=hr_instance, date=date)
                logger.info(f"[SERVICE] Created worked day for HR {hr_instance.id}: {date}")
                
                # Update HR instance
                hr_instance.days_worked += 1
                if hr_instance.payd_by_day:
                    hr_instance.current_period_amount += hr_instance.daily_salary
                
                # Update last worked dates
                WorkDayService.update_last_worked_dates(hr_instance)
                hr_instance.save()
                
                logger.info(f"[SERVICE] Successfully registered worked day for HR {hr_instance.id}")
                return worked_day, hr_instance
                
        except Exception as e:
            logger.error(f"[SERVICE] Error registering worked day for HR {hr_instance.id}: {str(e)}")
            raise

class PaymentService:
    """
    Service class for handling payment-related operations in the HR system.
    
    This service manages payment calculations, processing, and scheduling for HR records.
    It handles different payment intervals (daily, weekly, biweekly, monthly) and ensures
    payments are scheduled only on business days.
    """
    
    @staticmethod
    def calculate_next_payment_date(hr_instance):
        """
        Calculate the next payment date based on payment interval and business day.
        
        Args:
            hr_instance (HR): The HR instance to calculate next payment date for.
            
        Returns:
            date: Next payment date or None if payment_business_day is not configured.
        
        Payment Intervals:
            - daily: Next business day after last worked day
            - weekly: Next business day after the week of last worked day
            - biweekly: Next business day after two weeks of last worked day
            - monthly: Next business day of next month after last worked day
        """
        try:
            if not hr_instance.payment_business_day:
                logger.warning(f"[SERVICE] No payment business day configured for HR {hr_instance.id}")
                return None
            
            # Get the reference date (last worked day or current date)
            reference_date = None
            if hr_instance.payd_by_day and hr_instance.last_day_registered:
                reference_date = hr_instance.last_day_registered
            elif hr_instance.payd_by_hour and hr_instance.last_hours_registered:
                reference_date = hr_instance.last_hours_registered.date()
            else:
                reference_date = timezone.now().date()
            
            logger.info(f"[SERVICE] Calculating next payment date for HR {hr_instance.id}. "
                       f"Payment interval: {hr_instance.payment_interval}, "
                       f"Business day: {hr_instance.payment_business_day}, "
                       f"Reference date: {reference_date}")
            
            next_date = None
            
            if hr_instance.payment_interval == 'daily':
                # For daily payment, next business day after the last day worked
                next_date = reference_date + timedelta(days=1)
                # If it falls on the weekend, skip to Monday
                while next_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                    next_date += timedelta(days=1)
            
            elif hr_instance.payment_interval == 'weekly':
                # Adjust payment_business_day to base weekday() (0-6)
                target_weekday = hr_instance.payment_business_day - 1  # Convert from 1-5 to 0-4
                
                # Get next occurrence of target weekday
                days_ahead = target_weekday - reference_date.weekday()
                if days_ahead <= 0:  # Se já passou do dia alvo nesta semana
                    days_ahead += 7
                next_date = reference_date + timedelta(days=days_ahead)
                
                # Se a data de referência não é da semana atual, ajusta para a próxima semana
                if next_date <= reference_date:
                    next_date += timedelta(days=7)
                
                # Se cair no fim de semana, move para segunda
                while next_date.weekday() >= 5:
                    next_date += timedelta(days=1)
            
            elif hr_instance.payment_interval == 'biweekly':
                # Adjust payment_business_day to base weekday() (0-6)
                target_weekday = hr_instance.payment_business_day - 1  # Convert from 1-5 to 0-4
                
                # Get next occurrence of target weekday
                days_ahead = target_weekday - reference_date.weekday()
                if days_ahead <= 0:  # Se já passou do dia alvo nesta semana
                    days_ahead += 14
                next_date = reference_date + timedelta(days=days_ahead)
                
                # Se a data de referência não é da semana atual, ajusta para a próxima semana
                if next_date <= reference_date:
                    next_date += timedelta(days=14)
                
                # Check if we're in the right week (even or odd)
                if (next_date.isocalendar()[1] % 2) == (reference_date.isocalendar()[1] % 2):
                    next_date += timedelta(days=0)
                
                # Se cair no fim de semana, move para segunda
                while next_date.weekday() >= 5:
                    next_date += timedelta(days=1)
            
            elif hr_instance.payment_interval == 'monthly':
                # Find the next occurrence of payment_business_day in the month
                if reference_date.day >= hr_instance.payment_business_day:  # Se já passou do dia de pagamento
                    if reference_date.month == 12:
                        next_date = reference_date.replace(year=reference_date.year + 1, month=1, day=1)
                    else:
                        next_date = reference_date.replace(month=reference_date.month + 1, day=1)
                else:
                    next_date = reference_date.replace(day=1)
                
                # Adjust to the payment business day
                try:
                    next_date = next_date.replace(day=hr_instance.payment_business_day)
                except ValueError:  # Se o dia não existe neste mês
                    if next_date.month == 12:
                        next_date = next_date.replace(year=next_date.year + 1, month=1, day=1)
                    else:
                        next_date = next_date.replace(month=next_date.month + 1, day=1)
                    next_date -= timedelta(days=1)
                
                # Se cair no fim de semana, move para segunda
                while next_date.weekday() >= 5:
                    next_date += timedelta(days=1)
            
            logger.info(f"[SERVICE] Next payment date for HR {hr_instance.id}: {next_date}")
            return next_date
            
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating next payment date for HR {hr_instance.id}: {str(e)}")
            return None
    
    @staticmethod
    def process_payment(hr_instance):
        """
        Process payment for an HR instance.
        
        1. Validate payment conditions
        2. Create payment history record
        3. Store work history
        4. Update HR total_paid and clear current records
        5. Update payment dates
        """
        try:
            # Validar se tem valor para pagar
            if hr_instance.current_period_amount <= 0:
                logger.warning(f"[SERVICE] No amount to pay for HR {hr_instance.id}")
                return False
            
            with transaction.atomic():
                # Determinar o tipo de pagamento
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
                
                # 1. Criar registro de pagamento
                payment_history = PaymentHistory.objects.create(
                    hr=hr_instance,
                    amount_paid=hr_instance.current_period_amount,
                    payment_type=payment_type
                )
                logger.info(f"[SERVICE] Created payment history for HR {hr_instance.id}")
                
                # 2. Armazenar histórico de trabalho
                if hr_instance.payd_by_day:
                    # Obter todos os dias trabalhados
                    worked_days = WorkedDay.objects.filter(hr=hr_instance)
                    for day in worked_days:
                        WorkHistory.objects.create(
                            payment=payment_history,
                            date=day.date
                        )
                    logger.info(f"[SERVICE] Stored {worked_days.count()} days in work history")
                    
                elif hr_instance.payd_by_hour:
                    # Obter todas as horas trabalhadas
                    worked_hours = WorkHour.objects.filter(hr=hr_instance)
                    for hour in worked_hours:
                        WorkHistory.objects.create(
                            payment=payment_history,
                            date=hour.date,
                            start_time=hour.start_time,
                            end_time=hour.end_time,
                            hours=hour.hours
                        )
                    logger.info(f"[SERVICE] Stored {worked_hours.count()} hours in work history")
                
                # 3. Atualizar HR e limpar registros
                # Atualizar total pago
                hr_instance.total_paid = F('total_paid') + hr_instance.current_period_amount
                
                # Limpar registros atuais
                if hr_instance.payd_by_day:
                    WorkedDay.objects.filter(hr=hr_instance).delete()
                    hr_instance.days_worked = 0
                elif hr_instance.payd_by_hour:
                    WorkHour.objects.filter(hr=hr_instance).delete()
                    hr_instance.hours_worked = 0
                
                # 4. Atualizar datas de pagamento
                hr_instance.last_payment_date = timezone.now().date()
                hr_instance.next_payment_date = PaymentService.calculate_next_payment_date(hr_instance)
                hr_instance.current_period_amount = 0
                
                hr_instance.save()
                logger.info(f"[SERVICE] Successfully processed payment for HR {hr_instance.id}")
                
                return True
                
        except Exception as e:
            logger.error(f"[SERVICE] Error processing payment for HR {hr_instance.id}: {str(e)}")
            return False

    @staticmethod
    def get_next_payment_date(hr_instance):
        """
        Calculate and retrieve the next payment date for an HR record.
        
        This is a convenience method that wraps calculate_next_payment_date
        with additional logging.
        
        Args:
            hr_instance (HR): The HR instance to calculate next payment date for.
        
        Returns:
            date: The calculated next payment date.
        
        Raises:
            Exception: If any error occurs during calculation.
        """
        try:
            logger.info(f"[SERVICE] Retrieving next payment date for HR {hr_instance.id}")
            next_date = PaymentService.calculate_next_payment_date(hr_instance)
            
            if next_date:
                logger.info(f"[SERVICE] Next payment date for HR {hr_instance.id} ({hr_instance.employeer}): {next_date}")
            else:
                logger.warning(f"[SERVICE] No next payment date calculated for HR {hr_instance.id} ({hr_instance.employeer})")
                
            return next_date
            
        except Exception as e:
            logger.error(f"[SERVICE] Error calculating next payment date for HR {hr_instance.id}: {str(e)}")
            raise