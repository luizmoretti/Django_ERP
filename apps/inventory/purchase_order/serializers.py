from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import PurchaseOrder, PurchaseOrderItem
from ..product.models import Product
from ..supplier.models import Supplier
from decimal import Decimal


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderItem model
    
    Fields:
        product (PrimaryKeyRelatedField): Product UUID, write-only
        _product (CharField): Product name, read-only
        quantity (IntegerField): Quantity to order, must be positive
        unit_price (DecimalField): Price per unit
    """
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        required=True
    )
    _product = serializers.CharField(source='product.name', read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.00')
    )
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'product',
            '_product',
            'quantity',
            'unit_price'
        ]
        read_only_fields = ['_product']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model
    
    This serializer handles the creation and retrieval of PurchaseOrder instances with their
    associated PurchaseOrderItems. It uses separate fields for write operations (UUIDs) and
    read operations (names) for supplier references.
    
    Fields:
        id (UUIDField): Read-only unique identifier
        companie (UUIDField): Read-only company identifier
        supplier (PrimaryKeyRelatedField): Write-only field for supplier UUID
        _supplier (CharField): Read-only field for supplier name
        order_date (DateField): Date when order was placed
        expected_delivery (DateField): Expected delivery date
        status (CharField): Order status
        notes (TextField): Additional notes
        items (PurchaseOrderItemSerializer): Read-only nested serializer for order items
        items_data (ListField): Write-only field for creating order items
        created_at (DateTimeField): Read-only timestamp
        updated_at (DateTimeField): Read-only timestamp
        created_by (SerializerMethodField): Read-only creator name
        updated_by (SerializerMethodField): Read-only updater name
        
    Validation:
        - Supplier must exist
        - At least one item must be provided
        - All items must have valid products and quantities
    """
    id = serializers.ReadOnlyField()
    order_number = serializers.CharField(read_only=True, required=False)
    order_date = serializers.DateField(read_only=True, required=False)
    expected_delivery = serializers.DateField(required=True)
    
    status = serializers.CharField(max_length=20)
    notes = serializers.CharField(max_length=255, required=False)
    
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        write_only=True,
        required=True
    )
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    items = PurchaseOrderItemSerializer(
        many=True,
        read_only=True,
    )
    items_data = PurchaseOrderItemSerializer(
        many=True,
        write_only=True,
        required=True
    )
    
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    companie = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'order_number',
            'supplier',
            'supplier_name',
            'order_date',
            'expected_delivery',
            'status',
            'notes',
            'items',
            'items_data',
            'total',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'companie',
        ]
        read_only_fields = [
            'id',
            'order_number',
            'order_date',
            'supplier_name',
            'items',
            'total',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'companie',
        ]
    
    def get_created_by(self, obj) -> str | None:
        """Get the name of the user who created the order"""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str | None:
        """Get the name of the user who last updated the order"""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def get_companie(self, obj) -> str | None:
        """Get the name of the companie"""
        if obj.companie:
            return f'[{obj.companie.type}] {obj.companie.name}'
        return None
    
    def validate(self, attrs):
        """Validate the purchase order data
        
        Checks:
            - At least one item is provided
            - All items have valid products and quantities
            - Supplier exists
            - Order date and expected delivery are valid
        """
        # Validate items
        items_data = attrs.get('items_data')
        if not items_data:
            raise ValidationError({
                'items_data': 'At least one item is required'
            })
        
        # Validate supplier
        supplier = attrs.get('supplier')
        if not supplier:
            raise ValidationError({
                'supplier': 'Supplier is required'
            })
        
        # Validate dates
        order_date = attrs.get('order_date')
        expected_delivery = attrs.get('expected_delivery')
        if expected_delivery and order_date and expected_delivery < order_date:
            raise ValidationError({
                'expected_delivery': 'Expected delivery date cannot be before order date'
            })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create a purchase order with its items
        
        Creates the purchase order and its associated items in a single transaction.
        """
        items_data = validated_data.pop('items_data')
        order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=order,
                **item_data
            )
        
        return order
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a purchase order and its items
        
        Updates the purchase order and recreates all its items.
        Previous prices are preserved through signals before the update.
        """
        items_data = validated_data.pop('items_data', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in items_data:
                PurchaseOrderItem.objects.create(
                    purchase_order=instance,
                    **item_data
                )
        
        return instance
