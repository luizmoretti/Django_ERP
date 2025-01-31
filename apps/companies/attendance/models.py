from django.db import models
from apps.companies.employeers.models import Employeer
from basemodels.models import BaseModel
from core.constants.choices import PAYROLL_STATUS_CHOICES
from django.utils import timezone
from django.core.exceptions import ValidationError   

class AttendanceRegister(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='attendance_register')


class TimeTracking(BaseModel):
    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE, related_name='time_tracking', null=True, blank=True)
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, null=True, editable=False, related_name='attendance_employeer')
    clock_in = models.DateTimeField(default=timezone.now)
    clock_out = models.DateTimeField(null=True, blank=True)
    
    @property
    def duration(self):
        if self.clock_out:
            return self.clock_out - self.clock_in
        return None
    
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
    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE, related_name='days_tracking', null=True, blank=True)
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, null=True, editable=False, related_name='days_employeer')
    date = models.DateField(blank=True, null=True)
    clock_in = models.TimeField(blank=True, null=True)
    clock_out = models.TimeField(blank=True, null=True)
    
    @property
    def days_worked(self):
        days = 0
        if self.date and self.clock_in:
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
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='payroll_employeer')
    period_start = models.DateField()
    period_end = models.DateField()
    days_worked = models.PositiveIntegerField(blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYROLL_STATUS_CHOICES, default='Pending')
    
    
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
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='payroll_history')
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payroll_history')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    