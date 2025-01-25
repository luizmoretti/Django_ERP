from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from .models import HR, WorkedDay, WorkHour, PaymentHistory, WorkHistory


class WorkedDayInlineForm(forms.ModelForm):
    """Form for WorkedDay inline in admin."""
    
    class Meta:
        model = WorkedDay
        fields = ['date']
        widgets = {
            'date': AdminDateWidget()
        }


class WorkHourInlineForm(forms.ModelForm):
    """Form for WorkHour inline in admin."""
    
    class Meta:
        model = WorkHour
        fields = ['date', 'hours', 'start_time', 'end_time']
        widgets = {
            'date': AdminDateWidget(),
            'start_time': AdminTimeWidget(),
            'end_time': AdminTimeWidget()
        }

class HRAdminForm(forms.ModelForm):
    """Form for HR in admin."""
    
    class Meta:
        model = HR
        fields = '__all__'
        
    def clean(self):
        """Validate that only one payment type is selected."""
        cleaned_data = super().clean()
        payment_types = [
            cleaned_data.get('payd_by_day'),
            cleaned_data.get('payd_by_hour'),
            cleaned_data.get('payd_by_month')
        ]
        
        if sum(bool(pt) for pt in payment_types) != 1:
            raise forms.ValidationError(
                "Exactly one payment type must be selected."
            )
