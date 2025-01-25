from django.db import models
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from apps.accounts.models import NormalUser
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date, timedelta
from core.constants.choices import PAYMENT_INTERVAL_CHOICES, BUSINESS_DAY_CHOICES
import logging

logger = logging.getLogger(__name__)

class WorkHour(models.Model):
    """
    Model to store individual worked hours for employees paid by hour.
    """
    hr = models.ForeignKey(
        'HR',
        on_delete=models.CASCADE,
        related_name='worked_hours',
        help_text="HR record this worked hour belongs to"
    )
    date = models.DateField(
        help_text="Date worked"
    )
    
    start_time = models.TimeField(
        help_text="Start time of the worked hour",
        null=True,
        blank=True
    )
    
    end_time = models.TimeField(
        help_text="End time of the worked hour",
        null=True,
        blank=True
    )
    
    hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Hours worked on this day",
        blank=True,
        null=True
    )
    
    class Meta:
        unique_together = ['hr', 'date']
        ordering = ['-date']
        verbose_name = 'Worked Hour'
        verbose_name_plural = 'Worked Hours'
        
    def __str__(self):
        return f"{self.hr.employeer} - {self.date}"
    
    def calculate_hours(self):
        """Calculate hours worked based on start and end time."""
        if not (self.start_time and self.end_time):
            return None
            
        try:
            # Combine date with times for calculation
            start_dt = datetime.combine(date.today(), self.start_time)
            end_dt = datetime.combine(date.today(), self.end_time)
            
            # If end time is before start time, assume it's next day
            if end_dt < start_dt:
                end_dt = datetime.combine(date.today() + timedelta(days=1), self.end_time)
            
            # Calculate hours as decimal
            delta = end_dt - start_dt
            hours = delta.total_seconds() / 3600
            
            logger.info(f"[MODEL] Calculated {hours:.2f} hours for {self}")
            return round(hours, 2)
            
        except Exception as e:
            logger.error(f"[MODEL] Error calculating hours for {self}: {e}")
            return None
    
    def save(self, *args, **kwargs):
        """Override save to update HR hours_worked count."""
        # Calculate hours if start and end times are provided
        if self.start_time and self.end_time:
            self.hours = self.calculate_hours()
        
        # If hours is not set, raise error
        if self.hours is None:
            raise ValueError("Either provide hours directly or both start_time and end_time")
        
        # Salva o WorkHour
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class WorkedDay(models.Model):
    """
    Model to store individual worked days for employees paid by day.
    """
    hr = models.ForeignKey(
        'HR',
        on_delete=models.CASCADE,
        related_name='worked_days',
        help_text="HR record this worked day belongs to"
    )
    date = models.DateField(
        help_text="Date worked"
    )
    
    class Meta:
        unique_together = ['hr', 'date']
        ordering = ['-date']
        verbose_name = 'Worked Day'
        verbose_name_plural = 'Worked Days'
    
    def save(self, *args, **kwargs):
        """Override save to update HR days_worked count."""
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to update HR days_worked count."""
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.hr.employeer} - {self.date}"


class HR(models.Model):
    """
    Human Resources (HR) model for managing employee salary information.
    
    This model stores salary-related information for employees, supporting multiple
    payment types (daily, hourly, monthly) and payment intervals (daily, weekly,
    biweekly, monthly).
    
    Payment Processing:
    - Daily: Paid every business day
    - Weekly: Paid on specified business day of next week
    - Biweekly: Paid on specified business day of next two weeks
    - Monthly: Paid on specified business day of next month
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        help_text="Unique identifier for the HR record"
    )
    employeer = models.ForeignKey(
        Employeer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hr_employeer',
        help_text="Employee associated with this HR record"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        help_text="Timestamp when the record was last updated"
    )
    made_by = models.ForeignKey(
        NormalUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hr_made_by',
        help_text="User who created/modified this HR record"
    )
    
    # Campos de pagamento diário
    payd_by_day = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Indicates if employee is paid on a daily basis"
    )
    daily_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        help_text="Daily salary amount if paid by day"
    )
    days_worked = models.PositiveIntegerField(
        default=0,
        help_text="Number of days worked since last payment"
    )
    last_day_registered = models.DateField(
        null=True,
        blank=True,
        help_text="Last day registered as worked"
    )
    
    # Campos de pagamento por hora
    payd_by_hour = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Indicates if employee is paid on an hourly basis"
    )
    hourly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        help_text="Hourly salary amount if paid by hour"
    )
    hours_worked = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Number of hours worked in the current payment period"
    )
    last_hours_registered = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time hours were registered"
    )
    
    # Campos de pagamento mensal
    payd_by_month = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Indicates if employee is paid on a monthly basis"
    )
    monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        help_text="Monthly salary amount if paid by month"
    )
    
    # Novo campo para intervalo de pagamento
    payment_interval = models.CharField(
        max_length=10,
        choices=PAYMENT_INTERVAL_CHOICES,
        default='weekly',
        help_text="Interval between payments (daily, weekly, biweekly, monthly)"
    )
    
    # Novo campo para dia útil do pagamento
    payment_business_day = models.PositiveSmallIntegerField(
        choices=BUSINESS_DAY_CHOICES,
        default=2,
        help_text="Which business day the payment should be made"
    )
    
    last_payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the last payment made"
    )
    
    next_payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the next payment due"
    )
    
    current_period_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total amount to be paid for the current period"
    )
    
    total_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total amount paid to the employee"
    )
    
    companie = models.ForeignKey(
        Companie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_companie',
        help_text="Company associated with this HR record"
    )
    
    class Meta:
        verbose_name = 'HR'
        verbose_name_plural = 'HRs'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.employeer:
            return f"{self.employeer.user.first_name} {self.employeer.user.last_name}"
        return str(self.id)
    
    def clean(self):
        """
        Validate payment type and settings.
        """
        if not any([self.payd_by_day, self.payd_by_hour, self.payd_by_month]):
            raise ValidationError(_("Select at least one payment type"))
            
        if sum([self.payd_by_day, self.payd_by_hour, self.payd_by_month]) > 1:
            raise ValidationError(_("Select only one payment type"))
            
        if self.payd_by_day and not self.daily_salary:
            raise ValidationError(_("Daily salary is required for daily payment"))
            
        if self.payd_by_hour and not self.hourly_salary:
            raise ValidationError(_("Hourly salary is required for hourly payment"))
            
        if self.payd_by_month and not self.monthly_salary:
            raise ValidationError(_("Monthly salary is required for monthly payment"))
    
    def is_payment_due(self):
        """
        Check if payment is due based on next payment date.
        """
        if not self.next_payment_date:
            return False
        return timezone.now().date() >= self.next_payment_date
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure data consistency.
        """
        try:
            # Validate payment type and settings
            self.clean()
            
            # Save the instance
            super().save(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"[MODEL] - Error saving HR {self.id}: {str(e)}")
            raise

class PaymentHistory(models.Model):
    """
    Model to store payment history.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    hr = models.ForeignKey(HR, on_delete=models.CASCADE, related_name='payment_history')
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20)  # Daily, Hourly, Monthly
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment History'
        verbose_name_plural = 'Payment History'
        
class WorkHistory(models.Model):
    """
    Model to store work history.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    payment = models.ForeignKey(PaymentHistory, on_delete=models.CASCADE, related_name='work_history')
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Work History'
        verbose_name_plural = 'Work History'