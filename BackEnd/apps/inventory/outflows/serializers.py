from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Outflow, OutflowItems
from django.db import transaction
from ..warehouse.models import Warehouse
from ..product.models import Product
from apps.companies.customers.models import Customer
import logging

logger = logging.getLogger(__name__)

class OutflowItemSerializer(serializers.ModelSerializer):
    """Serializer for OutflowItems model
    
    Fields:
        product (SlugRelatedField): Product name, maps to Product model
        quantity (IntegerField): Quantity to send out, must be positive
        
    Meta:
        model: OutflowItems
        fields: ['product', 'quantity']
    """
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, required=True)
    _product = serializers.CharField(source='product.name', read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = OutflowItems
        fields = ['product', '_product', 'quantity']

class OutflowSerializer(serializers.ModelSerializer):
    """Serializer for Outflow model
    
    This serializer handles the creation and retrieval of Outflow instances with their
    associated OutflowItems. It uses separate fields for write operations (UUIDs) and
    read operations (names) for warehouse and customer references.
    
    Fields:
        id (UUIDField): Read-only unique identifier
        companie (UUIDField): Read-only company identifier
        origin (PrimaryKeyRelatedField): Write-only field for origin warehouse UUID
        destiny (PrimaryKeyRelatedField): Write-only field for destiny customer UUID
        origin_name (CharField): Read-only field for origin warehouse name
        destiny_name (CharField): Read-only field for destiny customer name
        _items (OutflowItemSerializer): Read-only nested serializer for outflow items
        items (OutflowItemSerializer): Write-only field for creating outflow items
        created_at (DateTimeField): Read-only timestamp
        updated_at (DateTimeField): Read-only timestamp
        created_by (SerializerMethodField): Read-only creator name
        updated_by (SerializerMethodField): Read-only updater name
        
    Validation:
        - Origin warehouse must exist
        - Destiny customer must exist
        - At least one item must be provided
        - Each item must have valid product and positive quantity
        - Product quantity must be available in warehouse
    """
    id = serializers.UUIDField(read_only=True)
    companie = serializers.UUIDField(read_only=True)
    
    # Write-only fields for UUIDs
    origin = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        required=True,
        write_only=True
    ) 
    # Read-only fields for Origin Warehouse 
    _origin = serializers.CharField(source='origin.name', read_only=True)
    origin_address = serializers.CharField(source='display_origin_address', read_only=True)
    
    destiny = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        required=True,
        write_only=True
    )
    # Read-only fields for Destiny Customer
    _destiny = serializers.CharField(source='destiny.full_name', read_only=True)
    destiny_address = serializers.SerializerMethodField(read_only=True)
    
    
    # Write-only field for items
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    # Read-only field for items
    items = OutflowItemSerializer(many=True, read_only=True)
    
    #Status Fields
    status = serializers.CharField(max_length=20, required=False)
    rejection_reason = serializers.CharField(max_length=255, required=False)
    
    
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Outflow
        fields = [
            'id',
            
            'origin',
            '_origin',
            'origin_address',
            
            'destiny',
            '_destiny',
            'destiny_address',
            
            
            'items',
            'items_data',
            
            'status',
            'rejection_reason',
            'companie',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by'
        ]
        read_only_fields = [
            'id',
            
            '_origin',
            'origin_address',
            
            '_destiny',
            'destiny_address',
            
            'items',
            'companie',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by'
        ]
        
    def get_created_by(self, obj) -> str:
        """Get the name of the user who created the outflow"""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_destiny_address(self, obj) -> str:
        if obj.destiny.another_shipping_address:
            destiny_address = obj.destiny.project_address.first()
            return f"{destiny_address.address}, {destiny_address.city}, {destiny_address.state}, {destiny_address.zip_code}"
        else:
            destiny_address = obj.destiny.project_address.first()
            return f"{destiny_address.address}, {destiny_address.city}, {destiny_address.state}, {destiny_address.zip_code}"
    
    def get_updated_by(self, obj) -> str:
        """Get the name of the user who last updated the outflow"""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def get__origin(self, obj) -> str:
        """Get the name of the origin warehouse"""
        return obj.origin.name
    
    def get__destiny(self, obj) -> str:
        """Get the name of the destiny customer"""
        return obj.destiny.full_name
        
    def validate(self, attrs):
        """Validate the outflow data
        
        Checks:
            - At least one item is provided
            - All items have valid products and quantities
            - Origin warehouse exists
            - Destiny customer exists
            - Product quantities are available in warehouse
        """
        if not attrs.get('items_data'):
            raise ValidationError({'items_data': 'At least one item is required'})
            
        items = attrs.get('items_data')
        warehouse = attrs.get('origin')
        
        for item in items:
            if not all(k in item for k in ('product', 'quantity')):
                raise ValidationError({
                    'items_data': 'Each item must have product and quantity'
                })
            
            if item['quantity'] < 1:
                raise ValidationError({
                    'items_data': 'Quantity must be positive'
                })
            
            # Check if product quantity is available in warehouse
            product_id = item['product']
            try:
                product = Product.objects.get(id=product_id)
                try:
                    warehouse_product = warehouse.items.get(product=product)
                    if warehouse_product.current_quantity < item['quantity']:
                        raise ValidationError({
                            'items_data': f'Not enough quantity for product {product.name} in warehouse'
                        })
                except warehouse.items.model.DoesNotExist:
                    raise ValidationError({
                        'items_data': f'Product {product.name} not found in warehouse'
                    })
            except Product.DoesNotExist:
                raise ValidationError({
                    'items_data': f'Product with id {product_id} does not exist'
                })
                
        return attrs
        
    @transaction.atomic
    def create(self, validated_data):
        """Create an outflow with its items
        
        Creates the outflow and its associated items in a single transaction.
        Updates the warehouse and product quantities through signals.
        """
        items_data = validated_data.pop('items_data')
        outflow = Outflow.objects.create(**validated_data)
        
        for item_data in items_data:
            product_id = item_data.pop('product')
            try:
                product = Product.objects.get(id=product_id)
                OutflowItems.objects.create(
                    outflow=outflow,
                    product=product,
                    quantity=item_data['quantity']
                )
            except Product.DoesNotExist:
                raise ValidationError(f'Product with id {product_id} does not exist')
            
        return outflow
        
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update an outflow and its items
        
        Updates the outflow and recreates all its items.
        Previous quantities are restored through signals before the update.
        """
        if 'items_data' in validated_data:
            items_data = validated_data.pop('items_data')
            instance.items.all().delete()
            
            for item_data in items_data:
                product_id = item_data.pop('product')
                try:
                    product = Product.objects.get(id=product_id)
                    OutflowItems.objects.create(
                        outflow=instance,
                        product=product,
                        quantity=item_data['quantity']
                    )
                except Product.DoesNotExist:
                    raise ValidationError(f'Product with id {product_id} does not exist')
                
        return super().update(instance, validated_data)