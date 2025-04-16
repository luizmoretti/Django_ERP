from rest_framework import serializers
from .models import Delivery, DeliveryCheckpoint
from apps.companies.customers.models import Customer
from apps.companies.employeers.models import Employeer
from apps.vehicle.models import Vehicle
from apps.inventory.load_order.models import LoadOrder
from rest_framework.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class DeliveryCheckpointSerializer(serializers.ModelSerializer):
    """
    Serializer for the DeliveryCheckpoint model.
    
    Handles serialization of delivery checkpoints which track location,
    status, and other details of a delivery at specific points in time.
    """
    id = serializers.UUIDField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DeliveryCheckpoint
        fields = [
            'id',
            'location',
            'timestamp',
            'status',
            'status_display',
            'notes',
            'photo',
        ]
        read_only_fields = ['id', 'timestamp', 'status_display']
        
    def get_status_display(self, obj):
        """Returns the human-readable status value."""
        return obj.get_status_display()


class DeliverySerializer(serializers.ModelSerializer):
    """
    Serializer for the Delivery model.
    
    Handles serialization of deliveries including:
    - Relationships to customers, drivers, vehicles, and load orders
    - Status management and location tracking
    - Read/write permission control for different fields
    - Derived fields for displaying relationship details
    """
    id = serializers.UUIDField(read_only=True)
    
    # Relationships - IDs for write operations, derived fields for read operations
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=True, write_only=True)
    customer_name = serializers.SerializerMethodField(read_only=True)
    
    driver = serializers.PrimaryKeyRelatedField(queryset=Employeer.objects.all(), required=True, write_only=True)
    driver_name = serializers.SerializerMethodField(read_only=True)
    
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), required=True, write_only=True)
    vehicle_info = serializers.SerializerMethodField(read_only=True)
    
    load = serializers.PrimaryKeyRelatedField(queryset=LoadOrder.objects.all(), many=True, required=True, write_only=True)
    load_info = serializers.SerializerMethodField(read_only=True)
    
    status_display = serializers.SerializerMethodField(read_only=True)
    
    checkpoints = DeliveryCheckpointSerializer(many=True, read_only=True)
    
    # Audit fields
    companie = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = [
            'id',
            'customer',
            'customer_name',
            'driver',
            'driver_name',
            'vehicle',
            'vehicle_info',
            'load',
            'load_info',
            'status',
            'status_display',
            'current_location',
            'estimated_arrival',
            'actual_arrival',
            'checkpoints',
            'companie',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = [
            'id',
            'customer_name',
            'driver_name',
            'vehicle_info',
            'load_info',
            'status_display',
            'checkpoints',
            'companie',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        
    def get_customer_name(self, obj) -> str:
        """Returns the full name of the customer."""
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    
    def get_driver_name(self, obj) -> str:
        """Returns the full name of the driver."""
        return f"{obj.driver.user.get_full_name()}"
    
    def get_vehicle_info(self, obj) -> str:
        """Returns formatted vehicle information (name and plate)."""
        return f"{obj.vehicle.nickname} | {obj.vehicle.plate_number}"
    
    def get_load_info(self, obj) -> list:
        """Returns a list of load order IDs and order numbers."""
        return [{'id': load.id, 'order_number': load.order_number} for load in obj.load.all()]
    
    def get_status_display(self, obj) -> str:
        """Returns the human-readable status value."""
        return obj.get_status_display()
    
    def get_created_by(self, obj) -> str:
        """Returns the full name of the user who created the delivery."""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str:
        """Returns the full name of the user who last updated the delivery."""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def get_companie(self, obj) -> str:
        """Returns the UUID of the companie."""
        return f"[{obj.companie.type}] {obj.companie.name}"
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Creates a new delivery with associated load orders.
        
        Uses atomic transaction to ensure data integrity during
        the creation of the delivery and its relationships.
        
        Args:
            validated_data: Data that has passed validation
            
        Returns:
            Newly created Delivery instance
        """
        loads = validated_data.pop('load', [])
        delivery = Delivery.objects.create(**validated_data)
        
        # Add associated load orders
        if loads:
            delivery.load.set(loads)
            
        return delivery
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Updates an existing delivery and its relationships.
        
        Uses atomic transaction to ensure data integrity during
        the update of the delivery and its relationships.
        
        Args:
            instance: Existing Delivery instance to update
            validated_data: Data that has passed validation
            
        Returns:
            Updated Delivery instance
        """
        if 'load' in validated_data:
            loads = validated_data.pop('load')
            instance.load.set(loads)
            
        return super().update(instance, validated_data)
