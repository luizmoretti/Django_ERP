from django.db import models
from apps.companies.employeers.models import Employeer
from basemodels.models import BaseModel
from core.constants.choices import PAYROLL_STATUS_CHOICES
from django.utils import timezone
from django.core.exceptions import ValidationError   
import datetime

class AttendanceRegister(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='attendance_employeer')
    acess_code = models.PositiveIntegerField(unique=True, editable=True, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Attendance Register'
        verbose_name_plural = 'Attendance Registers'
        ordering = ['-created_at']
        
    def clean(self):
        if self.acess_code is not None and len(str(self.acess_code)) != 6:
            raise ValidationError('Acess code must be 6 digits long')
        super().clean()

class TimeTracking(BaseModel):
    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE, related_name='attendance_time_tracking', null=True, blank=True)
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, null=True, editable=False, related_name='attendance_time_tracking_employeer')
    clock_in = models.DateTimeField(default=timezone.now)
    clock_out = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Time Tracking'
        verbose_name_plural = 'Time Trackings'
        ordering = ['-created_at']
    
    @property
    def duration(self):
        """Calculate the duration between clock_in and clock_out"""
        if self.clock_in and self.clock_out:
            # Converter strings para datetime se necessário
            clock_in = self.clock_in if isinstance(self.clock_in, datetime.datetime) else datetime.datetime.fromisoformat(self.clock_in)
            clock_out = self.clock_out if isinstance(self.clock_out, datetime.datetime) else datetime.datetime.fromisoformat(self.clock_out)
            return clock_out - clock_in
        return datetime.timedelta(0)
    
    def clean(self):
        if self.register:
            self.employee = self.register.employee
            if not Employeer.objects.filter(id=self.employee.id, payment_type='Hour').exists():
                raise ValidationError('Employee must have payment type "Hour" to create a Time Tracking')
        super().clean()
    
    def save(self, *args, **kwargs):
        if self.register:
            self.employee = self.register.employee
        super().save(*args, **kwargs)
    
class DaysTracking(BaseModel):
    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE, related_name='attendance_days_tracking', null=True, blank=True)
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, null=True, editable=False, related_name='attendance_days_tracking_employeer')
    date = models.DateField(blank=True, null=True)
    clock_in = models.TimeField(blank=True, null=True)
    clock_out = models.TimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Days Tracking'
        verbose_name_plural = 'Days Trackings'
        ordering = ['-created_at']
    
    @property
    def days_worked(self):
        days = 0
        if self.date and self.clock_in and self.clock_out:
            days += 1
        return days
    
    def clean(self):
        if self.register:
            self.employee = self.register.employee
            if not Employeer.objects.filter(id=self.employee.id, payment_type='Day').exists():
                raise ValidationError('Employee must have payment type "Day" to create a Days Tracking')
        super().clean()
    
    def save(self, *args, **kwargs):
        if self.register:
            self.employee = self.register.employee
        super().save(*args, **kwargs)
    
    @property
    def total_days(self):
        return self.days_worked

class Payroll(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='attendance_payroll_employeer')
    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE, related_name='attendance_payroll', null=True)
    period_start = models.DateField()
    period_end = models.DateField()
    days_worked = models.PositiveIntegerField(blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYROLL_STATUS_CHOICES, default='Pending')
    
    class Meta:
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payrolls'
        ordering = ['-created_at']
    
    @property
    def formatted_hours(self):
        if self.hours_worked:
            hours = int(float(self.hours_worked))
            decimal_part = float(self.hours_worked) % 1
            minutes = int(decimal_part * 60)
            seconds = int((decimal_part * 60 % 1) * 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"
    
class PayrollHistory(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='attendance_payroll_history_employeer')
    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE, related_name='attendance_payroll_history', null=True)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payroll_history')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    
    class Meta:
        verbose_name = 'Payroll History'
        verbose_name_plural = 'Payroll Histories'
        ordering = ['-created_at']
    