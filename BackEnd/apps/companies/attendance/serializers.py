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
                # Criar o registro de atendimento com o employee
                attendance_register = AttendanceRegister.objects.create(
                    employee=employee  # Passamos o employee diretamente
                )
                
                # Verificar o tipo de pagamento do funcionário
                payment_type = employee.payment_type
                
                # Processar cada entrada de trabalho
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
                # Atualizar o registro de atendimento
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                
                # Verificar o tipo de pagamento do funcionário
                payment_type = employee.payment_type
                
                # Processar cada entrada de trabalho
                for entry in work_data:
                    if payment_type == 'Hour':
                        # Atualizar ou criar novo registro de horas
                        time_tracking, created = TimeTracking.objects.update_or_create(
                            register=instance,
                            employee=employee,
                            clock_in=entry.get('clock_in'),
                            defaults={
                                'clock_out': entry.get('clock_out')
                            }
                        )
                    elif payment_type == 'Day':
                        # Atualizar ou criar novo registro diário
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