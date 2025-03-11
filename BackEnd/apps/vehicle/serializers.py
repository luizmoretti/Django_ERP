from rest_framework import serializers
from django.utils.translation import gettext as _
from django.db import transaction
from decimal import Decimal

from .models import Vehicle, VehicleMaintenanceRecord, VehicleFuelRecord
from apps.companies.employeers.models import Employeer
from apps.companies.employeers.serializers import EmployeerSerializer


class VehicleFuelRecordSerializer(serializers.ModelSerializer):
    """Serializer for VehicleFuelRecord model
    
    Fields:
        id (UUIDField): Read-only unique identifier
        vehicle (PrimaryKeyRelatedField): Vehicle UUID, write-only
        date (DateField): Date of the fuel purchase
        odometer_reading (IntegerField): Odometer reading at the time of fueling
        fuel_amount (DecimalField): Amount of fuel added in gallons
        fuel_cost (DecimalField): Total cost of the fuel purchase
        fuel_type (CharField): Type of fuel purchased
        station_name (CharField): Name of the fuel station, optional
        location (CharField): Location where fuel was purchased, optional
        full_tank (BooleanField): Whether the tank was filled completely
        notes (TextField): Additional notes about the fuel purchase, optional
        price_per_gallon (DecimalField): Calculated price per gallon, read-only
    """
    id = serializers.ReadOnlyField()
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        required=True
    )
    price_per_gallon = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = VehicleFuelRecord
        fields = [
            'id',
            'vehicle',
            'date',
            'odometer_reading',
            'fuel_amount',
            'fuel_cost',
            'fuel_type',
            'station_name',
            'location',
            'full_tank',
            'notes',
            'price_per_gallon',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'price_per_gallon',
            'created_at',
            'updated_at',
        ]
    
    def get_price_per_gallon(self, obj) -> float:
        """Calculate the price per gallon for this fuel purchase"""
        return obj.price_per_gallon
    
    def validate(self, attrs):
        """Validate the fuel record data
        
        Checks:
            - Odometer reading is greater than or equal to the vehicle's current odometer
            - Fuel amount is positive
            - Fuel cost is positive
        """
        vehicle = attrs.get('vehicle')
        odometer_reading = attrs.get('odometer_reading')
        fuel_amount = attrs.get('fuel_amount')
        fuel_cost = attrs.get('fuel_cost')
        
        # Validate odometer reading
        if odometer_reading < vehicle.odometer:
            raise serializers.ValidationError({
                'odometer_reading': _('Odometer reading cannot be less than the current vehicle odometer reading')
            })
        
        # Validate fuel amount
        if fuel_amount <= 0:
            raise serializers.ValidationError({
                'fuel_amount': _('Fuel amount must be positive')
            })
        
        # Validate fuel cost
        if fuel_cost <= 0:
            raise serializers.ValidationError({
                'fuel_cost': _('Fuel cost must be positive')
            })
        
        return attrs


class VehicleMaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for VehicleMaintenanceRecord model
    
    Fields:
        id (UUIDField): Read-only unique identifier
        vehicle (PrimaryKeyRelatedField): Vehicle UUID, write-only
        maintenance_type (CharField): Type of maintenance performed
        description (TextField): Detailed description of the maintenance
        cost (DecimalField): Cost of the maintenance
        service_date (DateField): Date when the maintenance was performed
        odometer_reading (IntegerField): Odometer reading at the time of maintenance
        performed_by (CharField): Person or company that performed the maintenance
        invoice_number (CharField): Invoice number, optional
        notes (TextField): Additional notes, optional
        next_maintenance_date (DateField): Recommended date for next maintenance, optional
        next_maintenance_odometer (IntegerField): Recommended odometer for next maintenance, optional
    """
    id = serializers.ReadOnlyField()
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        required=True
    )
    
    class Meta:
        model = VehicleMaintenanceRecord
        fields = [
            'id',
            'vehicle',
            'maintenance_type',
            'description',
            'cost',
            'service_date',
            'odometer_reading',
            'performed_by',
            'invoice_number',
            'notes',
            'next_maintenance_date',
            'next_maintenance_odometer',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]
    
    def validate(self, attrs):
        """Validate the maintenance record data
        
        Checks:
            - Odometer reading is greater than or equal to the vehicle's current odometer
            - Cost is positive
            - Service date is valid
            - Next maintenance date is after service date if provided
        """
        vehicle = attrs.get('vehicle')
        odometer_reading = attrs.get('odometer_reading')
        cost = attrs.get('cost')
        service_date = attrs.get('service_date')
        next_maintenance_date = attrs.get('next_maintenance_date')
        
        # Validate odometer reading
        if odometer_reading < vehicle.odometer:
            raise serializers.ValidationError({
                'odometer_reading': _('Odometer reading cannot be less than the current vehicle odometer reading')
            })
        
        # Validate cost
        if cost <= 0:
            raise serializers.ValidationError({
                'cost': _('Maintenance cost must be positive')
            })
        
        # Validate next maintenance date
        if next_maintenance_date and next_maintenance_date <= service_date:
            raise serializers.ValidationError({
                'next_maintenance_date': _('Next maintenance date must be after the service date')
            })
        
        return attrs


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model
    
    Fields:
        id (UUIDField): Read-only unique identifier
        plate_number (CharField): License plate number
        nickname (CharField): Nickname or common name, optional
        vehicle_type (CharField): Type of vehicle
        maker (CharField): Manufacturer of the vehicle
        model (CharField): Model of the vehicle
        year (IntegerField): Year of manufacture
        color (CharField): Color of the vehicle
        vin (CharField): Vehicle Identification Number
        capacity_weight (DecimalField): Maximum weight capacity
        capacity_volume (DecimalField): Maximum volume capacity
        insurance_number (CharField): Insurance policy number, optional
        insurance_expiry (DateField): Insurance expiry date, optional
        registration_expiry (DateField): Registration expiry date, optional
        last_maintenance_date (DateField): Date of last maintenance, read-only
        next_maintenance_date (DateField): Scheduled date for next maintenance, optional
        odometer (IntegerField): Current odometer reading
        fuel_level (DecimalField): Current fuel level percentage
        is_active (BooleanField): Whether the vehicle is active
        assigned_driver (PrimaryKeyRelatedField): Driver UUID, optional
        maintenance_due (BooleanField): Whether maintenance is due, read-only
        documentation_valid (BooleanField): Whether documentation is valid, read-only
        full_name (CharField): Full vehicle description, read-only
    """
    id = serializers.ReadOnlyField()
    assigned_driver = serializers.PrimaryKeyRelatedField(
        queryset=Employeer.objects.all(),
        required=False,
        allow_null=True
    )
    assigned_driver_name = serializers.SerializerMethodField(read_only=True)
    maintenance_due = serializers.BooleanField(read_only=True) #source='maintenance_due'
    documentation_valid = serializers.BooleanField(read_only=True) #source='documentation_valid'
    full_name = serializers.CharField(read_only=True) #source='full_name'
    maintenance_records = VehicleMaintenanceRecordSerializer(many=True, read_only=True)
    fuel_records = VehicleFuelRecordSerializer(many=True, read_only=True)
    
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
            'capacity_weight',
            'capacity_volume',
            'insurance_number',
            'insurance_expiry',
            'registration_expiry',
            'last_maintenance_date',
            'next_maintenance_date',
            'odometer',
            'fuel_level',
            'is_active',
            'assigned_driver',
            'assigned_driver_name',
            'maintenance_due',
            'documentation_valid',
            'full_name',
            'maintenance_records',
            'fuel_records',
            'created_at',
            'updated_at',
            'companie',
        ]
        read_only_fields = [
            'id',
            'last_maintenance_date',
            'maintenance_due',
            'documentation_valid',
            'full_name',
            'maintenance_records',
            'fuel_records',
            'created_at',
            'updated_at',
            'companie',
        ]
    
    def get_assigned_driver_name(self, obj) -> str:
        """Get the name of the assigned driver"""
        if obj.assigned_driver:
            return f"{obj.assigned_driver.first_name} {obj.assigned_driver.last_name}"
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
    
    def validate(self, attrs):
        """Validate the vehicle data
        
        Checks:
            - Year is valid
            - Capacity values are positive
            - Insurance and registration dates are valid
        """
        year = attrs.get('year')
        capacity_weight = attrs.get('capacity_weight')
        capacity_volume = attrs.get('capacity_volume')
        insurance_expiry = attrs.get('insurance_expiry')
        registration_expiry = attrs.get('registration_expiry')
        
        # Validate year
        from datetime import date
        current_year = date.today().year
        if year < 1900 or year > current_year + 1:
            raise serializers.ValidationError({
                'year': _('Year must be between 1900 and next year')
            })
        
        # Validate capacity values
        if capacity_weight <= 0:
            raise serializers.ValidationError({
                'capacity_weight': _('Weight capacity must be positive')
            })
        
        if capacity_volume <= 0:
            raise serializers.ValidationError({
                'capacity_volume': _('Volume capacity must be positive')
            })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create a vehicle with validated data"""
        return super().create(validated_data)
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a vehicle with validated data"""
        return super().update(instance, validated_data)