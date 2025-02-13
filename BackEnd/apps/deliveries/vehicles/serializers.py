from rest_framework import serializers
from .models import Vehicle
from apps.companies.employeers.models import Employeer
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class VehicleSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100, required=False)
    plate = serializers.CharField(max_length=100, required=False)
    driver = serializers.PrimaryKeyRelatedField(queryset=Employeer.objects.all(), required=True, write_only=True)
    driver_name = serializers.SerializerMethodField(read_only=True)
    drivers_license = serializers.CharField(max_length=100, required=False)
    vehicle_maker = serializers.CharField(max_length=100, required=False)
    vehicle_model = serializers.CharField(max_length=100, required=False)
    vehicle_color = serializers.CharField(max_length=100, required=False)
    type = serializers.CharField(max_length=100, required=False)
    vehicle_is_active = serializers.BooleanField(default=True, required=False)
    
    
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    companie_name = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    updated_by_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Vehicle
        fields = [
            'id',
            'name',
            'plate',
            'driver',
            'driver_name',
            'drivers_license',
            'vehicle_maker',
            'vehicle_model',
            'vehicle_color',
            'type',
            'vehicle_is_active',
            'created_at',
            'created_by_name',
            'updated_at',
            'updated_by_name',
            'companie_name'
        ]
        read_only_fields = [
            'id', 
            'driver_name',
            'created_at', 
            'updated_at', 
            'companie', 
            'created_by', 
            'updated_by',
            'companie_name',
            'created_by_name',
            'updated_by_name'
        ]
    
    
    def get_created_by_name(self, obj) -> str:
        if obj.created_by:
            return obj.created_by.name
        return None
    
    def get_updated_by_name(self, obj) -> str:
        if obj.updated_by:
            return obj.updated_by.name
        return None
    
    def get_driver_name(self, obj) -> str:
        if obj.driver:
            return obj.driver.name
        return None
    
    def get_companie_name(self, obj) -> str | None:
        if obj.companie:
            logger.debug(f'[VEHICLE SERIALIZER] Companie: {obj.companie.name} [{obj.companie.type}]')
            return f"[{obj.companie.type}] {obj.companie.name}"
        return None
    
    @transaction.atomic
    def create(self, validated_data):
        name = validated_data.pop('name')
        plate = validated_data.pop('plate')
        driver = validated_data.pop('driver')
        drivers_license = validated_data.pop('drivers_license')
        vehicle_maker = validated_data.pop('vehicle_maker', None)
        vehicle_model = validated_data.pop('vehicle_model', None)
        vehicle_color = validated_data.pop('vehicle_color', None)
        type = validated_data.pop('type', None)
        vehicle_is_active = validated_data.pop('vehicle_is_active', True)
        
        vehicle = Vehicle.objects.create(
            name=name,
            plate=plate,
            driver=driver,
            drivers_license=drivers_license,
            vehicle_maker=vehicle_maker,
            vehicle_model=vehicle_model,
            vehicle_color=vehicle_color,
            type=type,
            vehicle_is_active=vehicle_is_active
        )
        return vehicle
        
    
    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.plate = validated_data.get('plate', instance.plate)
        instance.driver = validated_data.get('driver', instance.driver)
        instance.drivers_license = validated_data.get('drivers_license', instance.drivers_license)
        instance.vehicle_maker = validated_data.get('vehicle_maker', instance.vehicle_maker)
        instance.vehicle_model = validated_data.get('vehicle_model', instance.vehicle_model)
        instance.vehicle_color = validated_data.get('vehicle_color', instance.vehicle_color)
        instance.type = validated_data.get('type', instance.type)
        instance.vehicle_is_active = validated_data.get('vehicle_is_active', instance.vehicle_is_active)
        instance.save()
        return instance
    