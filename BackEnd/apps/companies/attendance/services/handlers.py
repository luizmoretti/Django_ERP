from django.db import transaction
import logging
from ..models import AttendanceRegister, TimeTracking, DaysTracking, Payroll, PayrollHistory
from apps.companies.employeers.models import Employeer
from django.utils import timezone
import datetime
from decimal import Decimal
from .validators import AttendanceBusinessValidator

logger = logging.getLogger(__name__)

class AttendanceService:
    """
    Service class for managing attendance records and payroll operations.
    Handles CRUD operations and business logic for attendance tracking.
    """
    
    def __init__(self):
        self.validator = AttendanceBusinessValidator()
    
    def create_attendance(self, data, user):
        """Create a new attendance register with time or day tracking
        
        Args:
            data (dict): Data containing employee and work_data
            user: User creating the attendance register
            
        Returns:
            AttendanceRegister: Created attendance register instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Validate employee access
            employee_id = data.get('employee')
            employee = Employeer.objects.get(id=employee_id)
            self.validator.validate_company_access(employee, user)
            
            # Validate work data format
            work_data = data.get('work_data', [])
            self.validator.validate_work_data_format(work_data, employee.payment_type)
            
            with transaction.atomic():
                # Create attendance register
                attendance_register = AttendanceRegister.objects.create(
                    employee=employee
                )
                
                # Process work data based on payment type
                if employee.payment_type == 'Hour':
                    self._create_time_tracking_entries(attendance_register, employee, work_data)
                elif employee.payment_type == 'Day':
                    self._create_days_tracking_entries(attendance_register, employee, work_data)
                
                logger.info(f"[ATTENDANCE SERVICE] - Attendance register created successfully", 
                            extra={'attendance_id': attendance_register.id})
                
                return attendance_register
                
        except Exception as e:
            logger.error(f"[ATTENDANCE SERVICE] - Error creating attendance register: {str(e)}", 
                        exc_info=True)
            raise
    
    def update_attendance(self, instance, data, user):
        """Update an existing attendance register
        
        Args:
            instance: Existing AttendanceRegister instance
            data (dict): Updated data
            user: User updating the attendance register
            
        Returns:
            AttendanceRegister: Updated attendance register
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Validate employee access
            employee_id = data.get('employee')
            employee = Employeer.objects.get(id=employee_id)
            self.validator.validate_company_access(employee, user)
            
            # Validate work data format
            work_data = data.get('work_data', [])
            self.validator.validate_work_data_format(work_data, employee.payment_type)
            
            with transaction.atomic():
                # Process work data based on payment type
                if employee.payment_type == 'Hour':
                    self._update_time_tracking_entries(instance, employee, work_data)
                elif employee.payment_type == 'Day':
                    self._update_days_tracking_entries(instance, employee, work_data)
                
                logger.info(f"[ATTENDANCE SERVICE] - Attendance register updated successfully", 
                            extra={'attendance_id': instance.id})
                
                return instance
                
        except Exception as e:
            logger.error(f"[ATTENDANCE SERVICE] - Error updating attendance register: {str(e)}", 
                        exc_info=True)
            raise
    
    def update_payroll_status(self, payroll_id, status, user):
        """Update the status of a payroll record
        
        Args:
            payroll_id: ID of the payroll to update
            status: New status ('Pending' or 'Paid')
            user: User updating the status
            
        Returns:
            Payroll: Updated payroll record
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            payroll = Payroll.objects.get(id=payroll_id)
            
            # Validate company access
            self.validator.validate_company_access(payroll.employee, user)
            
            # Validate status change
            self.validator.validate_payroll_status_change(payroll, status)
            
            with transaction.atomic():
                payroll.status = status
                payroll.save()
                
                logger.info(f"[ATTENDANCE SERVICE] - Payroll status updated to {status}", 
                            extra={'payroll_id': payroll.id})
                
                return payroll
                
        except Exception as e:
            logger.error(f"[ATTENDANCE SERVICE] - Error updating payroll status: {str(e)}", 
                        exc_info=True)
            raise
    
    def generate_attendance_report(self, start_date, end_date, employee_id=None, company_id=None, user=None):
        """Generate a report of attendance and payroll for a given period
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            employee_id: Optional ID to filter by specific employee
            company_id: Optional ID to filter by specific company
            user: User requesting the report
            
        Returns:
            dict: Report data
        """
        try:
            # Convert to date objects if strings
            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Base query
            payroll_query = Payroll.objects.filter(
                period_start__gte=start_date,
                period_end__lte=end_date
            )
            
            # Apply filters
            if employee_id:
                payroll_query = payroll_query.filter(employee_id=employee_id)
            
            if company_id:
                payroll_query = payroll_query.filter(employee__companie_id=company_id)
            
            # If user provided, validate access
            if user and hasattr(user, 'employeer'):
                payroll_query = payroll_query.filter(
                    employee__companie=user.employeer.companie
                )
            
            # Calculate totals
            total_amount = sum(p.amount for p in payroll_query)
            total_hours = sum(p.hours_worked or 0 for p in payroll_query)
            total_days = sum(p.days_worked or 0 for p in payroll_query)
            
            # Prepare result
            report = {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'totals': {
                    'amount': total_amount,
                    'hours': total_hours,
                    'days': total_days,
                    'records': payroll_query.count()
                },
                'status': {
                    'pending': payroll_query.filter(status='Pending').count(),
                    'paid': payroll_query.filter(status='Paid').count()
                }
            }
            
            logger.info(f"[ATTENDANCE SERVICE] - Attendance report generated successfully")
            
            return report
            
        except Exception as e:
            logger.error(f"[ATTENDANCE SERVICE] - Error generating attendance report: {str(e)}", 
                        exc_info=True)
            raise
    
    def _create_time_tracking_entries(self, attendance_register, employee, work_data):
        """Helper method to create time tracking entries
        
        Args:
            attendance_register: AttendanceRegister instance
            employee: Employee instance
            work_data: List of work data dictionaries
        """
        for entry in work_data:
            TimeTracking.objects.create(
                register=attendance_register,
                employee=employee,
                clock_in=entry.get('clock_in'),
                clock_out=entry.get('clock_out')
            )
    
    def _create_days_tracking_entries(self, attendance_register, employee, work_data):
        """Helper method to create days tracking entries
        
        Args:
            attendance_register: AttendanceRegister instance
            employee: Employee instance  
            work_data: List of work data dictionaries
        """
        for entry in work_data:
            DaysTracking.objects.create(
                register=attendance_register,
                employee=employee,
                date=entry.get('date'),
                clock_in=entry.get('clock_in'),
                clock_out=entry.get('clock_out')
            )
    
    def _update_time_tracking_entries(self, attendance_register, employee, work_data):
        """Helper method to update time tracking entries
        
        Args:
            attendance_register: AttendanceRegister instance
            employee: Employee instance
            work_data: List of work data dictionaries
        """
        for entry in work_data:
            TimeTracking.objects.update_or_create(
                register=attendance_register,
                employee=employee,
                clock_in=entry.get('clock_in'),
                defaults={
                    'clock_out': entry.get('clock_out')
                }
            )
    
    def _update_days_tracking_entries(self, attendance_register, employee, work_data):
        """Helper method to update days tracking entries
        
        Args:
            attendance_register: AttendanceRegister instance
            employee: Employee instance
            work_data: List of work data dictionaries
        """
        for entry in work_data:
            DaysTracking.objects.update_or_create(
                register=attendance_register,
                employee=employee,
                date=entry.get('date'),
                defaults={
                    'clock_in': entry.get('clock_in'),
                    'clock_out': entry.get('clock_out')
                }
            )