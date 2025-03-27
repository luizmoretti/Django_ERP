from rest_framework import serializers
from .models import AttendanceRegister, TimeTracking, DaysTracking, Payroll, PayrollHistory
from apps.companies.employeers.models import Employeer
import logging
from django.db import transaction
import datetime

logger = logging.getLogger(__name__)

class TimeTrackingSerializer(serializers.ModelSerializer):
    duration = serializers.CharField(read_only=True)
    
    class Meta:
        model = TimeTracking
        fields = ['clock_in', 'clock_out', 'duration']

class DaysTrackingSerializer(serializers.ModelSerializer):
    clock_in = serializers.TimeField(format='%H:%M:%S')
    clock_out = serializers.TimeField(format='%H:%M:%S')
    
    class Meta:
        model = DaysTracking
        fields = ['date', 'clock_in', 'clock_out']

class PayrollSerializer(serializers.ModelSerializer):
    hours_worked = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    formatted_hours = serializers.CharField(read_only=True)
    
    class Meta:
        model = Payroll
        fields = [
            'period_start', 'period_end', 
            'days_worked', 'hours_worked', 'formatted_hours',
            'amount', 'status'
        ]

class PayrollHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PayrollHistory
        fields = ['amount_paid', 'payment_date']

class AttendanceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employeer.objects.all(), required=True, write_only=False)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    hours = TimeTrackingSerializer(source='attendance_time_tracking', many=True, read_only=True)
    days = DaysTrackingSerializer(source='attendance_days_tracking', many=True, read_only=True)
    payroll = PayrollSerializer(source='attendance_payroll', many=True, read_only=True)
    payroll_history = PayrollHistorySerializer(source='attendance_payroll_history', many=True, read_only=True)
    work_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    companie_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AttendanceRegister
        fields = [
            'id', 'employee', 'employee_name', 'hours', 'days',
            'payroll', 'payroll_history', 'work_data', 'created_at', 'updated_at', 'companie_name'
        ]
        read_only_fields = ['id', 'employee_name', 'hours', 'days', 'created_at', 'updated_at', 'companie_name']
    
    def get_companie_name(self, obj) -> str | None:
        if obj.companie:
            return f"[{obj.companie.type}] {obj.companie.name}"
        return None
    
    def validate_work_data(self, value) -> list:
        """
        Validate and convert work data into the correct formats.
        """
        for entry in value:
            try:
                if 'date' in entry:
                    # Validate date format
                    datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
                
                if 'clock_in' in entry:
                    # Validate clock_in format
                    if 'T' in entry['clock_in']:  # ISO format
                        datetime.datetime.fromisoformat(entry['clock_in'])
                    else:  # HH:MM:SS format
                        datetime.datetime.strptime(entry['clock_in'], '%H:%M:%S')
                
                if 'clock_out' in entry:
                    # Validate clock_out format
                    if 'T' in entry['clock_out']:  # ISO format
                        datetime.datetime.fromisoformat(entry['clock_out'])
                    else:  # HH:MM:SS format
                        datetime.datetime.strptime(entry['clock_out'], '%H:%M:%S')
                
            except ValueError as e:
                raise serializers.ValidationError(f"Invalid date/time format: {str(e)}")
        
        return value
    
    def create(self, validated_data):
        work_data = validated_data.pop('work_data', [])
        employee = validated_data.pop('employee')
        
        try:
            with transaction.atomic():
                # Create the attendance record with the employee
                attendance_register = AttendanceRegister.objects.create(
                    employee=employee  # Pass the employee directly
                )
                
                # Check the employee's payment type
                payment_type = employee.payment_type
                
                # Process each work entry
                for entry in work_data:
                    if payment_type == 'Hour':
                        TimeTracking.objects.create(
                            register=attendance_register,
                            employee=employee,
                            clock_in=entry.get('clock_in'),
                            clock_out=entry.get('clock_out')
                        )
                    elif payment_type == 'Day':
                        DaysTracking.objects.create(
                            register=attendance_register,
                            employee=employee,
                            date=entry.get('date'),
                            clock_in=entry.get('clock_in'),
                            clock_out=entry.get('clock_out')
                        )
                
                return attendance_register
                
        except Exception as e:
            logger.error(f"[ATTENDANCE SERIALIZER] - Error creating attendance register: {str(e)}")
            raise serializers.ValidationError({"detail": "Error creating attendance register"})
    
    def update(self, instance, validated_data):
        work_data = validated_data.pop('work_data', [])
        employee = validated_data.pop('employee')
        
        try:
            with transaction.atomic():
                # Update the attendance record
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                
                # Check the employee's payment type
                payment_type = employee.payment_type
                
                # Process each work entry
                for entry in work_data:
                    if payment_type == 'Hour':
                        # Update or create new hour record
                        time_tracking, created = TimeTracking.objects.update_or_create(
                            register=instance,
                            employee=employee,
                            clock_in=entry.get('clock_in'),
                            defaults={
                                'clock_out': entry.get('clock_out')
                            }
                        )
                    elif payment_type == 'Day':
                        # Update or create new day record
                        days_tracking, created = DaysTracking.objects.update_or_create(
                            register=instance,
                            employee=employee,
                            date=entry.get('date'),
                            defaults={
                                'clock_in': entry.get('clock_in'),
                                'clock_out': entry.get('clock_out')
                            }
                        )
                
                return instance
                
        except Exception as e:
            logger.error(f"[ATTENDANCE SERIALIZER] - Error updating attendance register: {str(e)}")
            raise serializers.ValidationError({"detail": "Error updating attendance register"})

class AttendanceClockInRequestSerializer(serializers.Serializer):
    """Serializer para validar requisições de registro de ponto (entrada/saída)"""
    access_code = serializers.IntegerField(
        required=True,
        min_value=100000,  # Código de 6 dígitos (mínimo 100000)
        max_value=999999,  # Código de 6 dígitos (máximo 999999)
        error_messages={
            'required': 'O código de acesso é obrigatório',
            'min_value': 'O código de acesso deve ter 6 dígitos',
            'max_value': 'O código de acesso deve ter 6 dígitos',
            'invalid': 'O código de acesso deve ser um número inteiro'
        }
    )
    
    def validate_access_code(self, value):
        """Validação adicional para o código de acesso"""
        # Converte para string para verificar o comprimento
        if len(str(value)) != 6:
            raise serializers.ValidationError("O código de acesso deve ter exatamente 6 dígitos")
        return value


class AttendanceClockInOutResponseSerializer(serializers.Serializer):
    """Serializer para padronizar a resposta da operação de registro de ponto"""
    operation = serializers.CharField(
        help_text="Operação realizada: clock_in ou clock_out"
    )
    employee_id = serializers.UUIDField(
        help_text="UUID do funcionário"
    )
    employee_name = serializers.CharField(
        help_text="Nome do funcionário"
    )
    success = serializers.BooleanField(
        help_text="Indica se a operação foi bem-sucedida"
    )
    # Campos adicionais que podem ser incluídos na resposta
    timestamp = serializers.DateTimeField(
        help_text="Data e hora do registro",
        required=False
    )
    message = serializers.CharField(
        help_text="Mensagem adicional para o usuário",
        required=False
    )

class PayrollPaymentInputSerializer(serializers.Serializer):
    """Serializer para validar dados de entrada para processamento de pagamento de folha"""
    payment_method = serializers.ChoiceField(
        choices=['bank_transfer', 'check', 'cash', 'online'],
        required=True,
        error_messages={
            'required': 'The payment method is mandatory',
            'invalid_choice': 'Invalid payment method. Choose between: bank_transfer, check, cash, online'
        },
        help_text="Payment method used"
    )
    payment_reference = serializers.CharField(
        required=False,
        allow_blank=False,
        help_text="Payment reference (check number, transaction ID, etc.)"
    )
    payment_date = serializers.DateField(
        required=False,
        help_text="Payment date (format YYYY-MM-DD)"
    )
    
    def validate_payment_date(self, value):
        """Validate payment date"""
        if value and value > datetime.date.today():
            raise serializers.ValidationError("Payment date cannot be in the future")
        return value
    
    def validate(self, data):
        """Custom validation for specific method and reference combinations"""
        payment_method = data.get('payment_method')
        payment_reference = data.get('payment_reference')
        
        # Verify if reference is required for certain payment methods
        if payment_method in ['bank_transfer', 'check'] and not payment_reference:
            raise serializers.ValidationError({
                'payment_reference': f'Payment reference is required for {payment_method}'
            })
            
        return data

class PayrollPaymentResponseSerializer(serializers.Serializer):
    """Serializer to standardize the response of the payroll payment operation"""
    success = serializers.BooleanField(
        help_text="Indicates if the operation was successful"
    )
    payment_details = serializers.DictField(
        help_text="Details of the processed payment",
        child=serializers.JSONField()
    )