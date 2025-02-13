from django.contrib import admin
from .models import TimeTracking, Payroll, PayrollHistory, DaysTracking, AttendanceRegister


class TimeTrackingAdmin(admin.TabularInline):
    model = TimeTracking
    extra = 0
    exclude = ('created_by', 'updated_by', 'created_at', 'updated_at', 'companie', 'employee')
    
class DaysTrackingAdmin(admin.TabularInline):
    model = DaysTracking
    extra = 0
    exclude = ('created_by', 'updated_by', 'created_at', 'updated_at', 'companie', 'total_days', 'employee')
    
@admin.register(AttendanceRegister)
class AttendanceRegisterAdmin(admin.ModelAdmin):
    list_display = ('employee', 'created_at', 'created_by')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at', 'companie')
    
    def get_inlines(self, request, obj=None):
        if not obj:  # Quando é um novo registro
            return []
        
        if obj.employee.payment_type == 'Hour':
            return [TimeTrackingAdmin]
        elif obj.employee.payment_type == 'Day':
            return [DaysTrackingAdmin]
        return []

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'period_start', 'period_end', 'amount', 'status', 'days_worked', 'formatted_hours')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at', 'companie')
    
    
@admin.register(PayrollHistory)
class PayrollHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll', 'amount_paid', 'payment_date')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at', 'companie')