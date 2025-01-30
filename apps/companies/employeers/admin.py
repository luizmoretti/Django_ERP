from django.contrib import admin
from .models import Employeer

@admin.register(Employeer)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'hire_date', 'payroll_schedule', 'payment_type', 'rate', 'created_by', 'created_at')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')
