from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import HR, WorkHour, WorkedDay
from django.db import transaction
from .services import PaymentService, WorkHourService, WorkDayService, HRService
from datetime import datetime
from apps.companies.models import Companie
import logging
logger = logging.getLogger(__name__)

class HRSerializer(serializers.ModelSerializer):
    """
    Serializer for HR model.
    
    This serializer handles the validation and representation of HR records,
    including payment settings and work status.
    
    Required fields for creation:
    - employeer: UUID of the employee
    - employeer_name: Name of the employee
    - One payment type must be selected (payd_by_day, payd_by_hour, or payd_by_month)
    - Corresponding salary field based on payment type:
      * daily_salary for payd_by_day
      * hourly_salary for payd_by_hour
      * monthly_salary for payd_by_month
    - payment_interval: 'daily', 'weekly', 'biweekly', or 'monthly'
    - payment_business_day: 1-5 (business day of payment)
    
    Read-only fields:
    - created_at, updated_at
    - days_worked, hours_worked
    - current_period_amount
    - last_payment_date
    - last_day_registered, last_hours_registered
    - payment_type, payment_status, work_status
    - worked_hours, worked_days
    """
    id = serializers.UUIDField(required=False)

    employeer_name = serializers.CharField(source='employeer.get_full_name', required=False)
    made_by_name = serializers.CharField(source='made_by.get_full_name', required=False)
    
    worked_hours = serializers.SerializerMethodField(read_only=True)
    worked_days = serializers.SerializerMethodField(read_only=True)
    
    payment_type = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    
    work_status = serializers.SerializerMethodField()
    
    last_payment_date = serializers.DateField(read_only=True, format="%Y-%m-%d")
    next_payment_date = serializers.DateField(required=False, allow_null=True)
    
    last_day_registered = serializers.DateField(required=False, allow_null=True)
    last_hours_registered = serializers.DateTimeField(required=False, allow_null=True)
    
    companie = serializers.PrimaryKeyRelatedField(required=False, queryset=Companie.objects.all())

    class Meta:
        model = HR
        fields = [
            'id', 
            'employeer', 
            'employeer_name', 
            'made_by', 
            'made_by_name',
            'payd_by_day', 
            'daily_salary', 
            'days_worked', 
            'last_day_registered',
            'payd_by_hour', 
            'hourly_salary', 
            'hours_worked', 
            'last_hours_registered',
            'companie',
            'payd_by_month', 
            'monthly_salary', 
            'payment_interval', 
            'payment_business_day',
            'last_payment_date', 
            'next_payment_date', 
            'current_period_amount',
            'payment_type', 
            'payment_status', 
            'work_status',
            'worked_hours', 
            'worked_days',
            'total_paid',
            'created_at', 
            'updated_at' 
        ]
        
        read_only_fields = [
            'created_at', 'updated_at', 'days_worked', 'hours_worked',
            'current_period_amount', 'total_paid', 'last_payment_date',
            'last_day_registered', 'last_hours_registered', 'made_by_name', 'id',
        ]

    def get_employeer_name(self, obj) -> str:
        """Get employee name."""
        if obj.employeer:
            return f"{obj.employeer.user.first_name} {obj.employeer.user.last_name}"
        return "Unassigned Employee"
    
    def get_made_by_name(self, obj) -> str:
        """Get made by name."""
        if obj.made_by:
            return f"{obj.made_by.first_name} {obj.made_by.last_name}" if not None else f"{obj.made_by.username}" 
        return "Unassigned Employee"
    
    def get_payment_type(self, obj) -> str:
        """Get formatted payment type with amount."""
        if obj.payd_by_day:
            return f'Daily'
        if obj.payd_by_hour:
            return f'Hourly'
        if obj.payd_by_month:
            return f'Monthly'
        return None

    def get_payment_status(self, obj) -> str:
        """
        Get payment status using PaymentService.
        
        Returns:
            str: One of:
                - 'Payment schedule not configured'
                - 'Payment Due'
                - 'Up to date'
        """
        try:
            # Se não tiver next_payment_date, calcular
            if not obj.next_payment_date:
                obj.next_payment_date = PaymentService.calculate_next_payment_date(obj)
                if obj.next_payment_date:
                    HR.objects.filter(id=obj.id).update(next_payment_date=obj.next_payment_date)
                    logger.info(f"[SERIALIZER] Updated next payment date for HR {obj.id}: {obj.next_payment_date}")
                else:
                    logger.warning(f"[SERIALIZER] Could not calculate next payment date for HR {obj.id}")
                    return 'Payment schedule not configured'
            
            today = timezone.now().date()
            if obj.next_payment_date <= today:
                logger.info(f"[SERIALIZER] Payment due for HR {obj.id}. Next payment: {obj.next_payment_date}, Today: {today}")
                return 'Payment Due'
            
            logger.info(f"[SERIALIZER] Payment up to date for HR {obj.id}. Next payment: {obj.next_payment_date}")
            return 'Up to date'
            
        except Exception as e:
            logger.error(f"[SERIALIZER] Error getting payment status for HR {obj.id}: {str(e)}")
            return 'Error calculating payment status'

    def get_work_status(self, obj) -> str:
        """Get work status based on payment type using services."""
        if obj.payd_by_day:
            total_days = WorkDayService.calculate_total_days(obj)
            if total_days == 1:
                return f'{total_days} day worked'
            return f'{total_days} days worked'
        if obj.payd_by_hour:
            total_hours = WorkHourService.calculate_total_hours(obj)
            if total_hours == 1:
                return f'{total_hours} hour worked'
            return f'{total_hours} hours worked'
        return None
    
    def get_worked_days(self, obj) -> dict:
        """Return a list of the dates worked"""
        if obj.payd_by_day:
            return WorkDayService.days_worked_list(obj)
        return 'Payment type is different'
    
    def get_worked_hours(self, obj) -> dict:
        """Return a list of the dates and hours worked"""
        if obj.payd_by_hour:
            return WorkHourService.hours_worked_list(obj)
        return 'Payment type is different'
    
    def validate(self, data):
        """
        Validate that:
        1. Only one payment type is selected
        2. The corresponding salary field is set
        3. Payment schedule is valid
        """
        payment_types = [
            data.get('payd_by_day', False),
            data.get('payd_by_hour', False),
            data.get('payd_by_month', False)
        ]
        
        # if not any(payment_types):
        #     raise serializers.ValidationError(_("Select at least one payment type"))

        if sum(payment_types) > 1:
            raise serializers.ValidationError(_("Select only one payment type"))

        # Validate salary based on payment type
        if data.get('payd_by_day') and not data.get('daily_salary'):
            raise serializers.ValidationError(_("Daily salary is required for daily payment"))
        
        if data.get('payd_by_hour') and not data.get('hourly_salary'):
            raise serializers.ValidationError(_("Hourly salary is required for hourly payment"))

        if data.get('payd_by_month') and not data.get('monthly_salary'):
            raise serializers.ValidationError(_("Monthly salary is required for monthly payment"))

        return data
    
    def create(self, validated_data):
        """
        Create HR instance with related work records.
        
        Args:
            validated_data (dict): Validated data for HR creation
            
        Returns:
            HR: Created HR instance
        """
        try:
            # Extrair dados de trabalho
            worked_days_data = self.context.get('request').data.get('worked_days', [])
            worked_hours_data = self.context.get('request').data.get('worked_hours', [])
            
            # Obter usuário logado e sua companie
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    employeer = request.user.employeer_user
                    validated_data['companie'] = employeer.companie
                    logger.info(f"[SERIALIZER] Setting company {employeer.companie} for HR record")
                except Exception as e:
                    logger.error(f"[SERIALIZER] Error getting user's company: {str(e)}")
                    raise serializers.ValidationError(_("User must be associated with a company"))
            
            with transaction.atomic():
                # Criar instância do HR
                hr_instance = HR.objects.create(**validated_data)
                logger.info(f"[SERIALIZER] Created HR instance for {hr_instance.employeer}")
                
                # Criar registros de dias trabalhados
                if hr_instance.payd_by_day and worked_days_data:
                    WorkedDay.objects.bulk_create(
                        [
                            WorkedDay(
                                hr=hr_instance,
                                date=day_data
                            )
                            for day_data in worked_days_data
                        ]
                    )
                    logger.info(f"[SERIALIZER] Created {len(worked_days_data)} worked days for HR {hr_instance.id}")
                    
                    # Atualizar campos calculados para dias
                    WorkDayService.update_last_worked_dates(hr_instance)
                    hr_instance.refresh_from_db()
                    
                    # Atualizar total de dias e valor
                    total_days = WorkDayService.calculate_total_days(hr_instance)
                    HR.objects.filter(id=hr_instance.id).update(
                        days_worked=total_days,
                        current_period_amount=total_days * hr_instance.daily_salary
                    )
                    hr_instance.refresh_from_db()
                    
                    # Atualizar data do próximo pagamento
                    next_payment = PaymentService.calculate_next_payment_date(hr_instance)
                    if next_payment:
                        HR.objects.filter(id=hr_instance.id).update(next_payment_date=next_payment)
                        hr_instance.refresh_from_db()
                
                # Criar registros de horas trabalhadas
                if hr_instance.payd_by_hour and worked_hours_data:
                    # Calcular horas trabalhadas
                    work_hours = []
                    for hour_data in worked_hours_data:
                        start = datetime.strptime(hour_data.get('start_time'), '%H:%M:%S').time()
                        end = datetime.strptime(hour_data.get('end_time'), '%H:%M:%S').time()
                        
                        # Converter para datetime para calcular diferença
                        date_obj = datetime.strptime(hour_data.get('date'), '%Y-%m-%d').date()
                        start_dt = datetime.combine(date_obj, start)
                        end_dt = datetime.combine(date_obj, end)
                        
                        # Calcular diferença em horas
                        hours = (end_dt - start_dt).total_seconds() / 3600
                        
                        work_hours.append(
                            WorkHour(
                                hr=hr_instance,
                                date=hour_data.get('date'),
                                start_time=start,
                                end_time=end,
                                hours=hours
                            )
                        )
                    
                    # Criar registros
                    WorkHour.objects.bulk_create(work_hours)
                    logger.info(f"[SERIALIZER] Created {len(worked_hours_data)} work hours for HR {hr_instance.id}")
                    
                    # Atualizar campos calculados para horas
                    HRService.update_worked_hours(hr_instance)
                    hr_instance.refresh_from_db()
                    
                    # Atualizar última hora registrada
                    last_hour = WorkHourService.get_last_worked_hour(hr_instance)
                    if last_hour:
                        HR.objects.filter(id=hr_instance.id).update(last_hours_registered=last_hour)
                        hr_instance.refresh_from_db()
                    
                    # Atualizar data do próximo pagamento
                    next_payment = PaymentService.calculate_next_payment_date(hr_instance)
                    if next_payment:
                        HR.objects.filter(id=hr_instance.id).update(next_payment_date=next_payment)
                        hr_instance.refresh_from_db()
                
                return hr_instance
                
        except Exception as e:
            logger.error(f"[SERIALIZER] Error creating HR: {str(e)}")
            raise serializers.ValidationError(f"Error creating HR: {str(e)}")
    
    def update(self, instance, validated_data):
        """
        Update HR instance and related work records.
        
        Args:
            instance (HR): Existing HR instance
            validated_data (dict): Validated data for update
            
        Returns:
            HR: Updated HR instance
        """
        try:
            # Extrair dados de trabalho
            worked_days_data = self.context.get('request').data.get('worked_days', [])
            worked_hours_data = self.context.get('request').data.get('worked_hours', [])
            
            # Verificar se o employeer pertence à mesma empresa do usuário logado
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    user_employeer = request.user.employeer_user
                    # Se estiver atualizando o employeer, validar a empresa
                    if 'employeer' in validated_data:
                        new_employeer = validated_data['employeer']
                        if new_employeer.companie != user_employeer.companie:
                            raise serializers.ValidationError(_("Cannot assign employee from different company"))
                except Exception as e:
                    logger.error(f"[SERIALIZER] Error validating user's company: {str(e)}")
                    raise serializers.ValidationError(_("User must be associated with a company"))
            
            with transaction.atomic():
                # Atualizar instância do HR
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                instance.refresh_from_db()
                
                # Se mudou o tipo de pagamento, limpar registros antigos
                if 'payd_by_day' in validated_data or 'payd_by_hour' in validated_data:
                    WorkedDay.objects.filter(hr=instance).delete()
                    WorkHour.objects.filter(hr=instance).delete()
                    instance.days_worked = 0
                    instance.hours_worked = 0
                    instance.current_period_amount = 0
                    instance.save()
                    instance.refresh_from_db()
                
                # Atualizar registros de dias trabalhados
                if instance.payd_by_day and worked_days_data:
                    WorkedDay.objects.filter(hr=instance).delete()
                    WorkedDay.objects.bulk_create(
                        [
                            WorkedDay(
                                hr=instance,
                                date=day_data
                            )
                            for day_data in worked_days_data
                        ]
                    )
                    logger.info(f"[SERIALIZER] Updated {len(worked_days_data)} worked days for HR {instance.id}")
                    
                    # Atualizar campos calculados para dias
                    WorkDayService.update_last_worked_dates(instance)
                    instance.refresh_from_db()
                    
                    # Atualizar total de dias e valor (adicionado)
                    total_days = WorkDayService.calculate_total_days(instance)
                    HR.objects.filter(id=instance.id).update(
                        days_worked=total_days,
                        current_period_amount=total_days * instance.daily_salary
                    )
                    instance.refresh_from_db()
                
                # Atualizar registros de horas trabalhadas
                if instance.payd_by_hour and worked_hours_data:
                    WorkHour.objects.filter(hr=instance).delete()
                    # Calcular horas trabalhadas (adicionado)
                    work_hours = []
                    for hour_data in worked_hours_data:
                        start = datetime.strptime(hour_data.get('start_time'), '%H:%M:%S').time()
                        end = datetime.strptime(hour_data.get('end_time'), '%H:%M:%S').time()
                        
                        # Converter para datetime para calcular diferença
                        date_obj = datetime.strptime(hour_data.get('date'), '%Y-%m-%d').date()
                        start_dt = datetime.combine(date_obj, start)
                        end_dt = datetime.combine(date_obj, end)
                        
                        # Calcular diferença em horas
                        hours = (end_dt - start_dt).total_seconds() / 3600
                        
                        work_hours.append(
                            WorkHour(
                                hr=instance,
                                date=hour_data.get('date'),
                                start_time=start,
                                end_time=end,
                                hours=hours
                            )
                        )
                    
                    # Criar registros
                    WorkHour.objects.bulk_create(work_hours)
                    logger.info(f"[SERIALIZER] Updated {len(worked_hours_data)} work hours for HR {instance.id}")
                    
                    # Atualizar campos calculados para horas
                    HRService.update_worked_hours(instance)
                    instance.refresh_from_db()
                    
                    # Atualizar última hora registrada (adicionado)
                    last_hour = WorkHourService.get_last_worked_hour(instance)
                    if last_hour:
                        HR.objects.filter(id=instance.id).update(last_hours_registered=last_hour)
                        instance.refresh_from_db()
                
                # Calcular próxima data de pagamento
                next_payment = PaymentService.calculate_next_payment_date(instance)
                if next_payment:
                    HR.objects.filter(id=instance.id).update(next_payment_date=next_payment)
                    instance.refresh_from_db()
                
                return instance
                
        except Exception as e:
            logger.error(f"[SERIALIZER] Error updating HR {instance.id}: {str(e)}")
            raise serializers.ValidationError(f"Error updating HR: {str(e)}")
