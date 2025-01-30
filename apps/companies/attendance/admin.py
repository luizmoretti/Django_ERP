from django.contrib import admin
from .models import TimeTracking, Payroll

@admin.register(TimeTracking)
class TimeTrackingAdmin(admin.ModelAdmin):
    list_display = ('employee', 'clock_in', 'clock_out', 'duration')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at', 'companie')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'period_start', 'period_end', 'amount', 'status')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at', 'companie')
