from django.core.exceptions import ValidationError
import logging
from ..models import Payroll
import datetime

logger = logging.getLogger(__name__)

class AttendanceBusinessValidator:
    """
    Validator class for attendance and payroll business rules.
    Implements validation methods for all attendance operations.
    """
    
    def validate_company_access(self, employee, user):
        """
        Validate that the user has access to the employee's company.
        
        Args:
            employee: Employee instance to validate access for
            user: User attempting the operation
            
        Raises:
            ValidationError: If user doesn't have access to the employee's company
        """
        if not hasattr(user, 'employeer'):
            logger.error("[ATTENDANCE VALIDATOR] - User has no associated employee")
            raise ValidationError("User has no associated employee")
        
        if employee.companie != user.employeer.companie:
            logger.error("[ATTENDANCE VALIDATOR] - Employee belongs to a different company")
            raise ValidationError("Cannot access employee from a different company")
    
    def validate_work_data_format(self, work_data, payment_type):
        """
        Validate the format of work data based on employee payment type.
        
        Args:
            work_data: List of work data entries to validate
            payment_type: Employee payment type ('Hour' or 'Day')
            
        Raises:
            ValidationError: If work_data format is invalid
        """
        if not work_data or not isinstance(work_data, list):
            logger.error("[ATTENDANCE VALIDATOR] - Work data must be a non-empty list")
            raise ValidationError("Work data must be a non-empty list")
        
        for entry in work_data:
            if payment_type == 'Hour':
                self._validate_hourly_entry(entry)
            elif payment_type == 'Day':
                self._validate_daily_entry(entry)
            else:
                logger.error(f"[ATTENDANCE VALIDATOR] - Invalid payment type: {payment_type}")
                raise ValidationError(f"Invalid payment type: {payment_type}")
    
    def validate_payroll_status_change(self, payroll, new_status):
        """
        Validate that the payroll status change is allowed.
        
        Args:
            payroll: Payroll instance to validate
            new_status: New status to set
            
        Raises:
            ValidationError: If status change is invalid
        """
        valid_statuses = ['Pending', 'Paid']
        
        if new_status not in valid_statuses:
            logger.error(f"[ATTENDANCE VALIDATOR] - Invalid payroll status: {new_status}")
            raise ValidationError(f"Invalid payroll status: {new_status}")
        
        # Validate status transition
        if payroll.status == new_status:
            logger.error(f"[ATTENDANCE VALIDATOR] - Payroll already has status: {new_status}")
            raise ValidationError(f"Payroll already has status: {new_status}")
        
        # Special validation for transitions
        if payroll.status == 'Paid' and new_status == 'Pending':
            logger.error("[ATTENDANCE VALIDATOR] - Cannot change status from Paid to Pending")
            raise ValidationError("Cannot change status from Paid to Pending")
    
    def validate_report_parameters(self, start_date, end_date):
        """
        Validate report generation parameters.
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Convert to date objects if strings
        if isinstance(start_date, str):
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                logger.error("[ATTENDANCE VALIDATOR] - Invalid start date format")
                raise ValidationError("Invalid start date format. Use YYYY-MM-DD")
                
        if isinstance(end_date, str):
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                logger.error("[ATTENDANCE VALIDATOR] - Invalid end date format")
                raise ValidationError("Invalid end date format. Use YYYY-MM-DD")
        
        # Validate date range
        if start_date > end_date:
            logger.error("[ATTENDANCE VALIDATOR] - Start date must be before end date")
            raise ValidationError("Start date must be before end date")
        
        # Validate range is not too broad (e.g., more than 1 year)
        date_range = (end_date - start_date).days
        if date_range > 365:
            logger.error("[ATTENDANCE VALIDATOR] - Date range exceeds 1 year")
            raise ValidationError("Date range cannot exceed 1 year")
    
    def _validate_hourly_entry(self, entry):
        """
        Validate a single hourly work entry format.
        
        Args:
            entry: Work data entry to validate
            
        Raises:
            ValidationError: If entry format is invalid
        """
        required_fields = ['clock_in', 'clock_out']
        
        for field in required_fields:
            if field not in entry:
                logger.error(f"[ATTENDANCE VALIDATOR] - Missing required field: {field}")
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate that clock_out is after clock_in if both are provided
        if entry.get('clock_in') and entry.get('clock_out'):
            try:
                # Convert to datetime objects if they're strings
                clock_in = self._parse_datetime(entry['clock_in'])
                clock_out = self._parse_datetime(entry['clock_out'])
                
                if clock_out <= clock_in:
                    logger.error("[ATTENDANCE VALIDATOR] - Clock out must be after clock in")
                    raise ValidationError("Clock out must be after clock in")
            except ValueError as e:
                logger.error(f"[ATTENDANCE VALIDATOR] - Invalid datetime format: {str(e)}")
                raise ValidationError(f"Invalid datetime format: {str(e)}")
    
    def _validate_daily_entry(self, entry):
        """
        Validate a single daily work entry format.
        
        Args:
            entry: Work data entry to validate
            
        Raises:
            ValidationError: If entry format is invalid
        """
        required_fields = ['date', 'clock_in', 'clock_out']
        
        for field in required_fields:
            if field not in entry:
                logger.error(f"[ATTENDANCE VALIDATOR] - Missing required field: {field}")
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate date format
        try:
            if isinstance(entry['date'], str):
                datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
        except ValueError:
            logger.error("[ATTENDANCE VALIDATOR] - Invalid date format")
            raise ValidationError("Invalid date format. Use YYYY-MM-DD")
        
        # Validate time format and order
        try:
            # Convert to time objects if they're strings
            clock_in = self._parse_time(entry['clock_in'])
            clock_out = self._parse_time(entry['clock_out'])
            
            if clock_out <= clock_in:
                logger.error("[ATTENDANCE VALIDATOR] - Clock out must be after clock in")
                raise ValidationError("Clock out must be after clock in")
        except ValueError as e:
            logger.error(f"[ATTENDANCE VALIDATOR] - Invalid time format: {str(e)}")
            raise ValidationError(f"Invalid time format: {str(e)}")
    
    def _parse_datetime(self, value):
        """
        Parse a datetime string to a datetime object.
        
        Args:
            value: Datetime string or object
            
        Returns:
            datetime: Parsed datetime object
        """
        if isinstance(value, datetime.datetime):
            return value
        
        if isinstance(value, str):
            if 'T' in value:  # ISO format
                return datetime.datetime.fromisoformat(value)
            else:
                # Try multiple formats
                formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S']
                for fmt in formats:
                    try:
                        return datetime.datetime.strptime(value, fmt)
                    except ValueError:
                        continue
        
        raise ValueError(f"Invalid datetime format: {value}")
    
    def _parse_time(self, value):
        """
        Parse a time string to a time object.
        
        Args:
            value: Time string or object
            
        Returns:
            time: Parsed time object
        """
        if isinstance(value, datetime.time):
            return value
        
        if isinstance(value, str):
            # Try multiple formats
            formats = ['%H:%M:%S', '%H:%M']
            for fmt in formats:
                try:
                    return datetime.datetime.strptime(value, fmt).time()
                except ValueError:
                    continue
        
        raise ValueError(f"Invalid time format: {value}")
    
    def validate_payment_data(self, payment_data):
        """Validate payment data structure and values
        
        Args:
            payment_data (dict): Payment data to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not payment_data:
            raise ValidationError("Payment data is required")
        
        # Required fields
        required_fields = ['payment_method']
        for field in required_fields:
            if field not in payment_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate payment method
        valid_methods = ['bank_transfer', 'check', 'cash', 'online']
        if payment_data.get('payment_method') not in valid_methods:
            raise ValidationError(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        
        # Validate payment reference if provided
        if 'payment_reference' in payment_data and not payment_data['payment_reference']:
            raise ValidationError("Payment reference cannot be empty when provided")
        
        # Validate payment date if provided
        if 'payment_date' in payment_data:
            try:
                if isinstance(payment_data['payment_date'], str):
                    datetime.strptime(payment_data['payment_date'], '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Invalid payment date format. Use YYYY-MM-DD")

    def validate_payroll_can_be_paid(self, payroll):
        """Validate if a payroll can be paid
        
        Args:
            payroll: Payroll instance to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if payroll.status == 'Paid':
            raise ValidationError(f"Payroll {payroll.id} has already been paid")
        
        if payroll.status != 'Pending':
            raise ValidationError(f"Only payrolls with 'Pending' status can be paid. Current status: {payroll.status}")
        
        # Validate payroll has amount
        if payroll.amount <= 0:
            raise ValidationError(f"Payroll amount must be greater than zero")