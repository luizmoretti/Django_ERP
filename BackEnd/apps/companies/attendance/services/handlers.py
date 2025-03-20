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
    
    def clock_inout_with_code(self, acess_code):
        """Register clock in or clock out using an access code
        
        This method automatically determines whether to register a clock in (create new tracking)
        or clock out (update existing tracking) based on the employee's current status.
        
        Args:
            acess_code: 6-digit access code
            
        Returns:
            dict: Result of the operation containing tracking details and status
            
        Raises:
            ValidationError: If access code is invalid or operation fails
        """
        try:
            # Find attendance register by code
            register = AttendanceRegister.objects.get(acess_code=acess_code)
            employee = register.employee
            
            # Determine operation type (clock in or clock out)
            if employee.payment_type == 'Hour':
                # Check for open time tracking (without clock_out)
                open_tracking = TimeTracking.objects.filter(
                    register=register,
                    employee=employee,
                    clock_out__isnull=True
                ).order_by('-created_at').first()
                
                current_time = timezone.now()
                
                if open_tracking:
                    # CLOCK OUT - update existing tracking
                    with transaction.atomic():
                        open_tracking.clock_out = current_time
                        open_tracking.save(update_fields=['clock_out'])
                        
                        logger.info(f"[ATTENDANCE SERVICE] - Clock out registered via access code", 
                                   extra={'employee_id': employee.id, 'tracking_id': open_tracking.id})
                        
                        return {
                            'operation': 'clock_out',
                            'employee_id': str(employee.id),
                            'employee_name': employee.name,
                            'tracking_id': str(open_tracking.id),
                            'clock_in': open_tracking.clock_in,
                            'clock_out': open_tracking.clock_out,
                            'duration': open_tracking.duration,
                            'success': True
                        }
                else:
                    # CLOCK IN - create new tracking
                    with transaction.atomic():
                        tracking = TimeTracking.objects.create(
                            register=register,
                            employee=employee,
                            clock_in=current_time
                        )
                        
                        logger.info(f"[ATTENDANCE SERVICE] - Clock in registered via access code", 
                                   extra={'employee_id': employee.id, 'tracking_id': tracking.id})
                        
                        return {
                            'operation': 'clock_in',
                            'employee_id': str(employee.id),
                            'employee_name': employee.name,
                            'tracking_id': str(tracking.id),
                            'clock_in': tracking.clock_in,
                            'success': True
                        }
                        
            elif employee.payment_type == 'Day':
                # For daily workers, check if there's an entry for today
                current_date = timezone.now().date()
                current_time = timezone.now().time()
                
                today_tracking = DaysTracking.objects.filter(
                    register=register,
                    employee=employee,
                    date=current_date
                ).first()
                
                if today_tracking:
                    # If entry exists for today but no clock_out, update it
                    if today_tracking.clock_out is None:
                        with transaction.atomic():
                            today_tracking.clock_out = current_time
                            today_tracking.save(update_fields=['clock_out'])
                            
                            logger.info(f"[ATTENDANCE SERVICE] - Clock out registered via access code (daily)", 
                                       extra={'employee_id': employee.id, 'tracking_id': today_tracking.id})
                            
                            return {
                                'operation': 'clock_out',
                                'employee_id': str(employee.id),
                                'employee_name': employee.name,
                                'tracking_id': str(today_tracking.id),
                                'date': today_tracking.date,
                                'clock_in': today_tracking.clock_in,
                                'clock_out': today_tracking.clock_out,
                                'success': True
                            }
                    else:
                        # Both clock_in and clock_out exist, can't modify further today
                        logger.warning(f"[ATTENDANCE SERVICE] - Day already fully registered", 
                                      extra={'employee_id': employee.id, 'tracking_id': today_tracking.id})
                        
                        return {
                            'operation': 'none',
                            'employee_id': str(employee.id),
                            'employee_name': employee.name,
                            'message': 'Day already fully registered with both clock in and clock out',
                            'success': False
                        }
                else:
                    # No entry for today, create new
                    with transaction.atomic():
                        tracking = DaysTracking.objects.create(
                            register=register,
                            employee=employee,
                            date=current_date,
                            clock_in=current_time
                        )
                        
                        logger.info(f"[ATTENDANCE SERVICE] - Clock in registered via access code (daily)", 
                                   extra={'employee_id': employee.id, 'tracking_id': tracking.id})
                        
                        return {
                            'operation': 'clock_in',
                            'employee_id': str(employee.id),
                            'employee_name': employee.name,
                            'tracking_id': str(tracking.id),
                            'date': tracking.date,
                            'clock_in': tracking.clock_in,
                            'success': True
                        }
            else:
                logger.error(f"[ATTENDANCE SERVICE] - Unsupported payment type: {employee.payment_type}", 
                            extra={'employee_id': employee.id})
                
                return {
                    'operation': 'none',
                    'employee_id': str(employee.id),
                    'employee_name': employee.name,
                    'message': f'Unsupported payment type: {employee.payment_type}',
                    'success': False
                }
        
        except AttendanceRegister.DoesNotExist:
            logger.error(f"[ATTENDANCE SERVICE] - Invalid access code: {acess_code}")
            raise ValidationError(f"Invalid access code: {acess_code}")
        except Exception as e:
            logger.error(f"[ATTENDANCE SERVICE] - Error processing attendance via access code: {str(e)}", 
                        exc_info=True)
            raise ValidationError(f"Error processing attendance: {str(e)}")