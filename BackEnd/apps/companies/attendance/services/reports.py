import logging
import datetime
from django.db.models import Sum, Count, F, Q
from ..models import AttendanceRegister, TimeTracking, DaysTracking, Payroll, PayrollHistory
from .validators import AttendanceBusinessValidator

logger = logging.getLogger(__name__)

class AttendanceReportService:
    """
    Service for generating attendance and payroll reports.
    """
    
    def __init__(self):
        self.validator = AttendanceBusinessValidator()
    
    def generate_attendance_summary(self, company, start_date, end_date, user):
        """
        Generate a summary report of attendance for a company within a date range.
        
        Args:
            company: Company instance to generate report for
            start_date: Start date for the report period
            end_date: End date for the report period
            user: User requesting the report
            
        Returns:
            dict: Dictionary containing attendance summary data
        """
        # Validate parameters
        self.validator.validate_report_parameters(start_date, end_date)
        
        # Query attendance records
        attendance_records = AttendanceRegister.objects.filter(
            companie=company,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Calculate summary statistics
        total_records = attendance_records.count()
        total_employees = attendance_records.values('employee').distinct().count()
        
        # Calculate metrics for hourly employees
        hourly_stats = self._calculate_hourly_stats(company, start_date, end_date)
        
        # Calculate metrics for daily employees
        daily_stats = self._calculate_daily_stats(company, start_date, end_date)
        
        # Create summary report
        report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'overview': {
                'total_records': total_records,
                'total_employees': total_employees,
            },
            'hourly_employees': hourly_stats,
            'daily_employees': daily_stats
        }
        
        logger.info(f"[ATTENDANCE REPORTS] - Generated attendance summary for period {start_date} to {end_date}")
        return report
    
    def generate_payroll_report(self, company, start_date, end_date, status=None, user=None):
        """
        Generate a payroll report for a company within a date range.
        
        Args:
            company: Company instance to generate report for
            start_date: Start date for the report period
            end_date: End date for the report period
            status: Optional filter for payroll status
            user: User requesting the report
            
        Returns:
            dict: Dictionary containing payroll report data
        """
        # Validate parameters
        self.validator.validate_report_parameters(start_date, end_date)
        
        # Build query filters
        filters = {
            'companie': company,
            'created_at__date__gte': start_date,
            'created_at__date__lte': end_date
        }
        
        if status:
            filters['status'] = status
        
        # Query payroll records
        payroll_records = Payroll.objects.filter(**filters)
        
        # Calculate summary statistics
        total_payroll = payroll_records.aggregate(
            total_amount=Sum('total_amount'),
            count=Count('id')
        )
        
        # Group by status
        status_summary = payroll_records.values('status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        )
        
        # Group by payment type
        payment_type_summary = payroll_records.values('payment_type').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        )
        
        # Create report
        report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'overview': {
                'total_records': total_payroll['count'] or 0,
                'total_amount': total_payroll['total_amount'] or 0,
            },
            'by_status': [item for item in status_summary],
            'by_payment_type': [item for item in payment_type_summary]
        }
        
        logger.info(f"[ATTENDANCE REPORTS] - Generated payroll report for period {start_date} to {end_date}")
        return report
    
    def generate_employee_attendance_report(self, employee, start_date, end_date, user):
        """
        Generate detailed attendance report for a specific employee.
        
        Args:
            employee: Employee instance to generate report for
            start_date: Start date for the report period
            end_date: End date for the report period
            user: User requesting the report
            
        Returns:
            dict: Dictionary containing employee attendance data
        """
        # Validate access and parameters
        self.validator.validate_company_access(employee, user)
        self.validator.validate_report_parameters(start_date, end_date)
        
        # Get attendance records for employee
        attendance_records = AttendanceRegister.objects.filter(
            employee=employee,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).order_by('created_at')
        
        # Initialize report data
        attendance_data = []
        
        # Process each attendance record
        for record in attendance_records:
            entry = {
                'date': record.created_at.date(),
                'id': record.id,
            }
            
            # Add time tracking data if available
            time_entries = TimeTracking.objects.filter(attendance=record)
            if time_entries.exists():
                entry['type'] = 'Hourly'
                entry['entries'] = [
                    {
                        'clock_in': te.clock_in,
                        'clock_out': te.clock_out,
                        'total_hours': te.total_hours
                    } for te in time_entries
                ]
                entry['total_hours'] = sum(te.total_hours for te in time_entries if te.total_hours)
            
            # Add days tracking data if available
            days_entries = DaysTracking.objects.filter(attendance=record)
            if days_entries.exists():
                entry['type'] = 'Daily'
                entry['entries'] = [
                    {
                        'date': de.date,
                        'clock_in': de.clock_in,
                        'clock_out': de.clock_out
                    } for de in days_entries
                ]
                entry['total_days'] = days_entries.count()
            
            attendance_data.append(entry)
        
        # Get payroll data for the employee in this period
        payroll_records = Payroll.objects.filter(
            employee=employee,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).order_by('created_at')
        
        payroll_data = [
            {
                'id': pr.id,
                'date': pr.created_at.date(),
                'payment_type': pr.payment_type,
                'total_amount': pr.total_amount,
                'status': pr.status
            } for pr in payroll_records
        ]
        
        # Calculate totals
        total_paid = sum(pr.total_amount for pr in payroll_records if pr.status == 'Paid')
        total_pending = sum(pr.total_amount for pr in payroll_records if pr.status == 'Pending')
        
        # Create report
        report = {
            'employee': {
                'id': employee.id,
                'name': employee.user.get_full_name() if hasattr(employee, 'user') else '',
                'payment_type': employee.payment_type,
                'rate': employee.payment_rate,
            },
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'attendance': attendance_data,
            'payroll': {
                'records': payroll_data,
                'total_paid': total_paid,
                'total_pending': total_pending,
                'total_amount': total_paid + total_pending
            }
        }
        
        logger.info(f"[ATTENDANCE REPORTS] - Generated employee attendance report for {employee.id}")
        return report
    
    def _calculate_hourly_stats(self, company, start_date, end_date):
        """
        Calculate statistics for hourly employees.
        
        Args:
            company: Company instance
            start_date: Start date for the report period
            end_date: End date for the report period
            
        Returns:
            dict: Dictionary with hourly employee statistics
        """
        # Get time tracking entries in the period
        time_entries = TimeTracking.objects.filter(
            attendance__companie=company,
            attendance__created_at__date__gte=start_date,
            attendance__created_at__date__lte=end_date
        )
        
        # Calculate totals
        total_hours = time_entries.aggregate(total=Sum('total_hours'))['total'] or 0
        total_employees = time_entries.values('attendance__employee').distinct().count()
        total_entries = time_entries.count()
        
        return {
            'total_employees': total_employees,
            'total_entries': total_entries,
            'total_hours': total_hours
        }
    
    def _calculate_daily_stats(self, company, start_date, end_date):
        """
        Calculate statistics for daily employees.
        
        Args:
            company: Company instance
            start_date: Start date for the report period
            end_date: End date for the report period
            
        Returns:
            dict: Dictionary with daily employee statistics
        """
        # Get days tracking entries in the period
        days_entries = DaysTracking.objects.filter(
            attendance__companie=company,
            attendance__created_at__date__gte=start_date,
            attendance__created_at__date__lte=end_date
        )
        
        # Calculate totals
        total_days = days_entries.count()
        total_employees = days_entries.values('attendance__employee').distinct().count()
        
        return {
            'total_employees': total_employees,
            'total_entries': total_days,
            'total_days': total_days
        }