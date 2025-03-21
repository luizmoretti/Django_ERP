from rest_framework import serializers
from django.utils.translation import gettext as _
from django.db import transaction
from .models import Vehicle
from apps.companies.employeers.models import Employeer
from core.constants.choices import (
    VEHICLE_TYPE_CHOICES, 
    VEHICLE_MAKER_CHOICES, 
    VEHICLE_COLOR_CHOICES
)


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model
    
    Fields:
        id (UUIDField): Read-only unique identifier
        plate_number (CharField): License plate number
        nickname (CharField): Nickname or common name, optional
        vehicle_type (CharField): Type of vehicle
        maker (CharField): Manufacturer of the vehicle
        color (CharField): Color of the vehicle
        vin (CharField): Vehicle Identification Number
        is_active (BooleanField): Whether the vehicle is active
        assigned_driver (PrimaryKeyRelatedField): Driver UUID, optional
        full_name (CharField): Full vehicle description, read-only
    """
    id = serializers.ReadOnlyField()
    nickname = serializers.CharField(required=False)
    plate_number = serializers.CharField()
    vehicle_type = serializers.ChoiceField(choices=VEHICLE_TYPE_CHOICES, required=False)
    maker = serializers.ChoiceField(choices=VEHICLE_MAKER_CHOICES, required=False)
    color = serializers.ChoiceField(choices=VEHICLE_COLOR_CHOICES, required=False)
    vin = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False, default=True)
    assigned_driver = serializers.PrimaryKeyRelatedField(
        queryset=Employeer.objects.all(),
        required=False,
        allow_null=True
    )
    _assigned_driver = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(read_only=True) #source='full_name'
    
    # Audit fields
    created_by = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    updated_by = serializers.SerializerMethodField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    companie = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id',
            'plate_number',
            'nickname',
            'vehicle_type',
            'maker',
            'color',
            'vin',
            'is_active',
            'assigned_driver',
            '_assigned_driver',
            'full_name',
            'created_by',
            'created_at',
            'updated_by',
            'updated_at',
            'companie',
        ]
        read_only_fields = [
            'id',
            'full_name',
            'created_by',
            'created_at',
            'updated_by',
            'updated_at',
            'companie',
        ]
    
    def get__assigned_driver(self, obj) -> str:
        """Get the name of the assigned driver"""
        if obj.assigned_driver:
            return f"{obj.assigned_driver.first_name} {obj.assigned_driver.last_name}"
        return None
    
    def get_companie(self, obj) -> str:
        """Get the name of the company"""
        return f'[{obj.companie.type}] {obj.companie.name}'
    
    def get_created_by(self, obj) -> str | None:
        """Get the name of the user who created the vehicle"""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str | None:
        """Get the name of the user who last updated the vehicle"""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def validate_plate_number(self, value):
        """Validate that the plate number is unique"""
        instance = getattr(self, 'instance', None)
        if instance and instance.plate_number == value:
            return value
            
        if Vehicle.objects.filter(plate_number=value).exists():
            raise serializers.ValidationError(_('A vehicle with this plate number already exists'))
        return value
    
    def validate_vin(self, value):
        """Validate that the VIN is unique"""
        instance = getattr(self, 'instance', None)
        if instance and instance.vin == value:
            return value
            
        if Vehicle.objects.filter(vin=value).exists():
            raise serializers.ValidationError(_('A vehicle with this VIN already exists'))
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Create a vehicle with validated data"""
        return super().create(validated_data)
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a vehicle with validated data"""
        return super().update(instance, validated_data)