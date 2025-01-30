from django.db import models
from apps.companies.employeers.models import Employeer
from basemodels.models import BaseModel
from core.constants.choices import PAYROLL_STATUS_CHOICES
from django.utils import timezone


class TimeTracking(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='attendance_employeer')
    clock_in = models.DateTimeField(default=timezone.now)
    clock_out = models.DateTimeField(null=True, blank=True)
    
    @property
    def duration(self):
        if self.clock_out:
            return self.clock_out - self.clock_in
        return None


class Payroll(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='payroll_employeer')
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYROLL_STATUS_CHOICES, default='Pending')