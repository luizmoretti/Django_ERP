from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
from .services import WorkDayService, WorkHourService, PaymentService, HRService
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

from .models import HR, WorkedDay, WorkHour, PaymentHistory, WorkHistory
from .forms import WorkedDayInlineForm, WorkHourInlineForm, HRAdminForm


class WorkedDayInline(admin.TabularInline):
    model = WorkedDay
    form = WorkedDayInlineForm
    extra = 1
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-date')


class WorkHourInline(admin.TabularInline):
    model = WorkHour
    form = WorkHourInlineForm
    extra = 1
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-date')


@admin.register(HR)
class HRAdmin(admin.ModelAdmin):
    """Admin interface for HR model."""
    
    form = HRAdminForm
    actions = ['process_payment', 'mark_as_paid']
    list_select_related = ['employeer__user']
    list_display_links = ['employee_name', 'payment_type']
    
    list_display = [
        'employee_name',
        'payment_type',
        'current_amount',
        'payment_schedule',
        'work_status',
        'payment_status',
        'created_at',
        'made_by'
    ]
    
    list_filter = [
        'payd_by_day',
        'payd_by_hour',
        'payd_by_month',
        'payment_interval',
        'payment_business_day'
    ]
    
    search_fields = [
        'employeer__user__first_name',
        'employeer__user__last_name',
        'employeer__user__email'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'days_worked',
        'hours_worked',
        'current_period_amount',
        'last_payment_date',
        'next_payment_date',
        'last_day_registered',
        'last_hours_registered'
    ]
    
    fieldsets = [
        ('Employee Information', {
            'fields': [
                'employeer',
                'made_by'
            ]
        }),
        ('Payment Settings', {
            'fields': [
                'payd_by_day', 'daily_salary',
                'payd_by_hour', 'hourly_salary',
                'payd_by_month', 'monthly_salary',
                'payment_interval',
                'payment_business_day'
            ]
        }),
        ('Work Status', {
            'fields': [
                'days_worked',
                'last_day_registered',
                'hours_worked',
                'last_hours_registered'
            ]
        }),
        ('Payment Status', {
            'fields': [
                'current_period_amount',
                'last_payment_date',
                'next_payment_date'
            ]
        }),
        ('System Information', {
            'fields': [
                'id',
                'created_at',
                'updated_at'
            ]
        })
    ]
    
    def get_inline_instances(self, request, obj=None):
        """Return appropriate inline based on payment type."""
        if not obj:  # When creating a new object
            return []
            
        if obj.payd_by_day:
            return [WorkedDayInline(self.model, self.admin_site)]
        elif obj.payd_by_hour:
            return [WorkHourInline(self.model, self.admin_site)]
        return []
    
    def get_form(self, request, obj=None, **kwargs):
        """Override to add request to form."""
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form
    
    def response_change(self, request, obj):
        """Override to handle custom actions."""
        response = super().response_change(request, obj)
        obj.refresh_from_db()
        return response
    
    def save_model(self, request, obj, form, change):
        """Override to ensure HR is updated before saving."""
        try:
            # Save the model
            super().save_model(request, obj, form, change)
            
            # Updates the object in memory
            obj.refresh_from_db()
            
            with transaction.atomic():
                # Updates the last record dates
                if obj.payd_by_day:
                    WorkDayService.update_last_worked_dates(obj)
                    logger.info(f"[ADMIN] Updated last day registered for HR {obj.id}")
                elif obj.payd_by_hour:
                    WorkHourService.update_last_worked_dates(obj)
                    logger.info(f"[ADMIN] Updated last hours registered for HR {obj.id}")
                
                # Recalculate next payment date
                next_payment = PaymentService.calculate_next_payment_date(obj)
                if next_payment:
                    HR.objects.filter(id=obj.id).update(next_payment_date=next_payment)
                    logger.info(f"[ADMIN] Updated next payment date for HR {obj.id} to {next_payment}")
                
                obj.refresh_from_db()
            
            # Shows success message
            messages.success(request, f"HR updated successfully. Current value: ${obj.current_period_amount}")
            
        except Exception as e:
            logger.error(f"[ADMIN] - Error saving HR {obj.id}: {str(e)}")
            messages.error(request, f"Error updating HR: {str(e)}")
            raise
    
    def save_formset(self, request, form, formset, change):
        """Override to ensure HR is updated after inline saves."""
        try:
            # Save the formset
            super().save_formset(request, form, formset, change)
            
            # Updates the object in memory
            hr = form.instance
            hr.refresh_from_db()
            
            with transaction.atomic():
                # Updates the last record dates
                if hr.payd_by_day:
                    WorkDayService.update_last_worked_dates(hr)
                    logger.info(f"[ADMIN] Updated last day registered for HR {hr.id}")
                elif hr.payd_by_hour:
                    WorkHourService.update_last_worked_dates(hr)
                    logger.info(f"[ADMIN] Updated last hours registered for HR {hr.id}")
                
                # Recalculate next payment date
                next_payment = PaymentService.calculate_next_payment_date(hr)
                if next_payment:
                    HR.objects.filter(id=hr.id).update(next_payment_date=next_payment)
                    logger.info(f"[ADMIN] Updated next payment date for HR {hr.id} to {next_payment}")
                
                hr.refresh_from_db()
            
            # Shows success message
            messages.success(request, f"Records successfully updated. Current value: ${hr.current_period_amount}")
            
        except Exception as e:
            logger.error(f"[ADMIN] - Error saving formset to HR {form.instance.id}: {str(e)}")
            messages.error(request, f"Error updating records: {str(e)}")
            raise
    
    def employee_name(self, obj):
        """Display employee name with link to employee admin."""
        if obj.employeer:
            url = reverse('admin:employeers_employeer_change', args=[obj.employeer.id])
            return format_html('<a href="{}">{} {}</a>',
                             url,
                             obj.employeer.user.first_name,
                             obj.employeer.user.last_name)
        return "-"
    employee_name.short_description = _("Employee")
    
    def payment_type(self, obj):
        """Display payment type with amount."""
        if obj.payd_by_day:
            return f'Daily (${obj.daily_salary}/day)'
        if obj.payd_by_hour:
            return f'Hourly (${obj.hourly_salary}/hour)'
        if obj.payd_by_month:
            return f'Monthly (${obj.monthly_salary}/month)'
        return "-"
    payment_type.short_description = _("Payment Type")
    
    def current_amount(self, obj):
        """Display current period amount."""
        return format_html('${}', obj.current_period_amount)
    current_amount.short_description = _("Current Amount")
    
    def payment_schedule(self, obj):
        """Display payment interval and business day."""
        intervals = dict(obj.__class__.PAYMENT_INTERVAL_CHOICES)
        return format_html('{} - business day {}',
                         intervals[obj.payment_interval],
                         obj.payment_business_day)
    payment_schedule.short_description = _("Payment Schedule")
    
    def work_status(self, obj):
        """Display work status based on payment type."""
        if obj.payd_by_day:
            return format_html('{} days worked', obj.days_worked)
        if obj.payd_by_hour:
            return format_html('{} hours worked', obj.hours_worked)
        return "-"
    work_status.short_description = _("Work Status")
    
    def payment_status(self, obj):
        """Display payment status."""
        if obj.is_payment_due():
            return format_html('<span style="color: red;">Payment Due</span>')
        return format_html('<span style="color: green;">Up to date</span>')
    payment_status.short_description = _("Payment Status")
    
    def process_payment(self, request, queryset):
        """Process payment for selected records using PaymentService."""
        updated = 0
        for hr in queryset:
            try:
                if hr.is_payment_due():
                    PaymentService.process_payment(hr)
                    updated += 1
                    logger.info(f"[ADMIN] Successfully processed payment for HR {hr.id}")
            except Exception as e:
                logger.error(f"[ADMIN] Error processing payment for HR {hr.id}: {str(e)}")
                messages.error(request, f'Error processing payment for record {hr.id}: {str(e)}')
        
        if updated:
            messages.success(request, f'Successfully processed payment for {updated} records.')
        else:
            messages.warning(request, 'No payments were due for processing.')
    process_payment.short_description = _("Process payment for selected records")
    
    def mark_as_paid(self, request, queryset):
        """Mark selected records as paid today."""
        updated = queryset.update(
            last_payment_date=timezone.now().date(),
            current_period_amount=0,
            days_worked=0,
            hours_worked=0
        )
        
        if updated:
            messages.success(request, f'Successfully marked {updated} records as paid.')
        else:
            messages.warning(request, 'No records were updated.')
    mark_as_paid.short_description = _("Mark selected records as paid")
    
    class Media:
        css = {
            'all': ['admin/css/forms.css']
        }
        js = ['admin/js/core.js']
        
        
        
class WorkHistoryInline(admin.TabularInline):
    """Inline admin for WorkHistory."""
    model = WorkHistory
    extra = 0
    readonly_fields = ['date', 'start_time', 'end_time', 'hours']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    """Admin interface for PaymentHistory model."""
    list_display = ['payment_date', 'hr_name', 'payment_type', 'amount_paid']
    list_filter = ['payment_date', 'payment_type']
    search_fields = ['hr__employeer__first_name', 'hr__employeer__last_name']
    readonly_fields = ['hr', 'payment_date', 'amount_paid', 'payment_type']
    inlines = [WorkHistoryInline]
    
    def hr_name(self, obj):
        """Get HR employee name."""
        return obj.hr.employeer.get_full_name()
    hr_name.short_description = 'Employee'
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    
@admin.register(WorkHistory)
class WorkHistoryAdmin(admin.ModelAdmin):
    """Admin interface for WorkHistory model."""
    list_display = ['date', 'payment_employee', 'start_time', 'end_time', 'hours']
    list_filter = ['date', 'payment__payment_type']
    search_fields = ['payment__hr__employeer__first_name', 'payment__hr__employeer__last_name']
    readonly_fields = ['payment', 'date', 'start_time', 'end_time', 'hours']
    
    def payment_employee(self, obj):
        """Get payment employee name."""
        return obj.payment.hr.employeer.get_full_name()
    payment_employee.short_description = 'Employee'
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False