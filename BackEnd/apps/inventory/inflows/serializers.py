from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Inflow, InflowItems
from django.db import transaction
from ..warehouse.models import Warehouse
from ..product.models import Product
from ..supplier.models import Supplier
import logging

logger = logging.getLogger(__name__)

class InflowItemSerializer(serializers.ModelSerializer):
    """Serializer for InflowItems model
    
    Fields:
        product (SlugRelatedField): Product name, maps to Product model
        quantity (IntegerField): Quantity to receive, must be positive
        
    Meta:
        model: InflowItems
        fields: ['product', 'quantity']
    """
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, required=True)
    _product = serializers.CharField(source='product.name', read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = InflowItems
        fields = ['product', '_product', 'quantity']
        

class InflowSerializer(serializers.ModelSerializer):
    """Serializer for Inflow model
    
    This serializer handles the creation and retrieval of Inflow instances with their
    associated InflowItems. It uses separate fields for write operations (UUIDs) and
    read operations (names) for warehouse and supplier references.
    
    Fields:
        id (UUIDField): Read-only unique identifier
        companie (UUIDField): Read-only company identifier
        origin (PrimaryKeyRelatedField): Write-only field for origin supplier UUID
        destiny (PrimaryKeyRelatedField): Write-only field for destiny warehouse UUID
        origin_name (CharField): Read-only field for origin supplier name
        destiny_name (CharField): Read-only field for destiny warehouse name
        items (InflowItemSerializer): Read-only nested serializer for inflow items
        items_data (ListField): Write-only field for creating inflow items
        created_at (DateTimeField): Read-only timestamp
        updated_at (DateTimeField): Read-only timestamp
        created_by (SerializerMethodField): Read-only creator name
        updated_by (SerializerMethodField): Read-only updater name
        
    Validation:
        - Origin supplier must exist
        - Destiny warehouse must exist
        - At least one item must be provided
        - Each item must have valid product and positive quantity
    """
    id = serializers.UUIDField(read_only=True)
    
    # Write-only fields for UUIDs
    origin = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        required=True,
        write_only=True
    )
    # Read-only field for Origin name
    _origin = serializers.CharField(source='origin.name', read_only=True)
    destiny = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        required=True,
        write_only=True
    )
    # Read-only field for Destiny name
    _destiny = serializers.CharField(source='destiny.name', read_only=True)
    
    items = InflowItemSerializer(many=True, read_only=True)
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    
    status = serializers.CharField(max_length=20, required=False)
    rejection_reason = serializers.CharField(max_length=255, required=False)
    
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    companie = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Inflow
        fields = [
            'id',
            'origin',
            '_origin',
            'destiny',
            '_destiny',
            'type',
            'items',
            'items_data',
            'status',
            'rejection_reason',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'companie',
        ]
        read_only_fields = [
            'id', 
            'companie',
            '_destiny',
            '_origin',
            'items', 
            'created_at', 
            'updated_at', 
            'created_by', 
            'updated_by', 
        ]
    
    # def get_origin_name(self, obj) -> str | None:
    #     """Get the name of the origin supplier"""
    #     return obj.origin.name
    
    # def get_destiny_name(self, obj) -> str | None:
    #     """Get the name of the destiny customer"""
    #     return obj.destiny.full_name
    
    def get_created_by(self, obj) -> str | None:
        """Get the name of the user who created the inflow"""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str | None:
        """Get the name of the user who last updated the inflow"""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
        
    def validate(self, attrs):
        """Validate the inflow data
        
        Validates basic data requirements and formats:
            - Required fields are present
            - Data types are correct
            - Basic value validations
        """
        # Validate items_data structure
        if not attrs.get('items_data'):
            raise ValidationError({'items_data': 'At least one item is required'})
            
        items = attrs.get('items_data')
        for item in items:
            if not isinstance(item, dict):
                raise ValidationError({'items_data': 'Each item must be a dictionary'})
                
            if not all(k in item for k in ('product', 'quantity')):
                raise ValidationError({
                    'items_data': 'Each item must have product and quantity fields'
                })
                
            if not isinstance(item.get('quantity'), (int, float)):
                raise ValidationError({
                    'items_data': 'Quantity must be a number'
                })
                
            if item['quantity'] < 1:
                raise ValidationError({
                    'items_data': 'Quantity must be positive'
                })
                
        return attrs
        
    @transaction.atomic
    def create(self, validated_data):
        """Create an inflow with its items
        
        Creates the inflow and its associated items in a single transaction.
        Updates the warehouse and product quantities through signals.
        """
        items_data = validated_data.pop('items_data')
        inflow = Inflow.objects.create(**validated_data)
        
        for item_data in items_data:
            # Get the Product instance from the validated InflowItemSerializer
            item_serializer = InflowItemSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            validated_item = item_serializer.validated_data
            
            InflowItems.objects.create(
                inflow=inflow,
                product=validated_item['product'],
                quantity=validated_item['quantity'],
            )
            
        return inflow
        
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update an inflow and its items
        
        Updates the inflow and recreates all its items.
        Previous quantities are restored through signals before the update.
        """
        if 'items_data' in validated_data:
            items_data = validated_data.pop('items_data')
            instance.inflow_items.all().delete()
            
            for item_data in items_data:
                # Get the Product instance from the validated InflowItemSerializer
                item_serializer = InflowItemSerializer(data=item_data)
                item_serializer.is_valid(raise_exception=True)
                validated_item = item_serializer.validated_data
                
                InflowItems.objects.create(
                    inflow=instance,
                    product=validated_item['product'],
                    quantity=validated_item['quantity'],
                    companie=instance.companie,
                    created_by=instance.created_by,
                    updated_by=instance.updated_by,
                )
                
        return super().update(instance, validated_data)