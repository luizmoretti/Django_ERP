from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Transfer, TransferItems
from django.db import transaction
from ..warehouse.models import Warehouse
from ..product.models import Product
import logging

logger = logging.getLogger(__name__)

class TransferItemSerializer(serializers.ModelSerializer):
    """Serializer for TransferItems model
    
    Fields:
        product (SlugRelatedField): Product name, maps to Product model
        quantity (IntegerField): Quantity to transfer, must be positive
        
    Meta:
        model: TransferItems
        fields: ['product', 'quantity']
    """
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, required=True)
    _product = serializers.CharField(source='product.name', read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = TransferItems
        fields = ['product', '_product', 'quantity']

class TransferSerializer(serializers.ModelSerializer):
    """Serializer for Transfer model
    
    This serializer handles the creation and retrieval of Transfer instances with their
    associated TransferItems. It uses separate fields for write operations (UUIDs) and
    read operations (names) for warehouse references.
    
    Fields:
        id (UUIDField): Read-only unique identifier
        companie (UUIDField): Read-only company identifier
        origin (PrimaryKeyRelatedField): Write-only field for origin warehouse UUID
        destiny (PrimaryKeyRelatedField): Write-only field for destiny warehouse UUID
        origin_name (CharField): Read-only field for origin warehouse name
        destiny_name (CharField): Read-only field for destiny warehouse name
        items (TransferItemSerializer): Read-only nested serializer for transfer items
        items_data (ListField): Write-only field for creating transfer items
        created_at (DateTimeField): Read-only timestamp
        updated_at (DateTimeField): Read-only timestamp
        created_by (SerializerMethodField): Read-only creator name
        updated_by (SerializerMethodField): Read-only updater name
        
    Validation:
        - Origin and destiny warehouses must be different
        - At least one item must be provided
        - Each item must have valid product and positive quantity
    """
    id = serializers.UUIDField(read_only=True)
    companie = serializers.UUIDField(read_only=True)
    
    # Write-only fields for warehouse UUIDs
    origin = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        required=True,
        write_only=True
    )
    # Read-only field for origin warehouse name
    _origin = serializers.CharField(source='origin.name', read_only=True)
    
    
    destiny = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        required=True,
        write_only=True
    )
    # Read-only field for destiny warehouse name
    _destiny = serializers.CharField(source='destiny.name', read_only=True)
    
    
    items = TransferItemSerializer(many=True, read_only=True)
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Transfer
        fields = [
            'id',
            
            'origin',
            '_origin',
            
            'destiny',
            '_destiny',
            
            'type',
            
            'items',
            'items_data',
            
            'companie',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by'
        ]
        read_only_fields = [
            'id', 
            'companie', 
            'created_at', 
            'updated_at', 
            'created_by', 
            'updated_by',
            'items', 
            '_origin',
            '_destiny'
        ]
    
    def get_created_by(self, obj) -> str | None:
        """ 
        Retrieves creator's name for list view.
        
        Args:
            obj (Transfer): Transfer instance
            
        Returns:
            str | None: Creator's full name, or None if not available
        """
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str | None:
        """ 
        Retrieves last updater's name for list view.
        
        Args:
            obj (Transfer): Transfer instance
            
        Returns:
            str | None: Last updater's full name, or None if not available
        """
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def get__origin(self, obj) -> str:
        """
        Retrieves origin warehouse name
        """
        return obj.origin.name
    
    def get__destiny(self, obj) -> str:
        """
        Retrieves destination warehouse name
        """
        return obj.destiny.name
    
    def validate(self, data):
        """
        Validate transfer data
        
        Checks:
        1. Origin and destiny warehouses must be different
        2. Each item must have valid product and quantity
        3. At least one item must be provided
        
        Returns:
            dict: Validated data if all checks pass
            
        Raises:
            ValidationError: If any validation check fails
        """
        if data['origin'] == data['destiny']:
            logger.warning("Attempted to create transfer with same origin and destiny warehouse")
            raise ValidationError("Origin and destiny warehouses must be different")
            
        # Get items data
        items_data = data.get('items_data', [])
        if not items_data:
            logger.warning("Attempted to create transfer without items")
            raise ValidationError("At least one item is required")
            
        # Validate each item
        for item in items_data:
            if not isinstance(item, dict):
                logger.error(f"Invalid item format: {item}")
                raise ValidationError("Each item must be a dictionary")
                
            if 'product' not in item:
                logger.error("Item missing product field")
                raise ValidationError("Each item must have a product")
                
            if 'quantity' not in item:
                logger.error("Item missing quantity field")
                raise ValidationError("Each item must have a quantity")
                
            try:
                product = Product.objects.get(id=item['product'])
                item['product'] = product
            except Product.DoesNotExist:
                logger.error(f"Product with id {item['product']} not found")
                raise ValidationError(f"Product with id {item['product']} does not exist")
                
            if not isinstance(item['quantity'], int) or item['quantity'] < 1:
                logger.error(f"Invalid quantity: {item['quantity']}")
                raise ValidationError("Quantity must be a positive integer")
            
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new transfer with its items
        
        Args:
            validated_data (dict): Validated transfer data
            
        Returns:
            Transfer: Created transfer instance
            
        Raises:
            ValidationError: If creation fails
        """
        items_data = validated_data.pop('items_data')
        
        logger.info(f"Creating transfer from {validated_data['origin']} to {validated_data['destiny']}")
        
        # Create transfer instance
        transfer = Transfer.objects.create(**validated_data)
        
        # Create transfer items individually to trigger signals
        for item_data in items_data:
            try:
                TransferItems.objects.create(
                    transfer=transfer,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    companie=transfer.companie,
                    created_by=transfer.created_by,
                    updated_by=transfer.updated_by
                )
                logger.info(f"Created transfer item: {item_data['quantity']} units of {item_data['product']}")
            except Exception as e:
                logger.error(f"Error creating transfer item: {str(e)}")
                raise ValidationError(f"Error creating transfer item: {str(e)}")
        
        logger.info(f"Transfer {transfer.id} created successfully")
        return transfer
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update an existing transfer and its items
        
        Args:
            instance (Transfer): Existing transfer instance
            validated_data (dict): Validated transfer data
            
        Returns:
            Transfer: Updated transfer instance
            
        Raises:
            ValidationError: If update fails
        """
        items_data = validated_data.pop('items_data', None)
        
        logger.info(f"Updating transfer {instance.id}")
        
        # Update transfer instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update transfer items if provided
        if items_data is not None:
            # Delete existing items
            logger.info(f"Deleting existing items for transfer {instance.id}")
            instance.items.all().delete()
            
            # Create new items individually to trigger signals
            for item_data in items_data:
                try:
                    TransferItems.objects.create(
                        transfer=instance,
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        companie=instance.companie,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by
                    )
                    logger.info(f"Created new transfer item: {item_data['quantity']} units of {item_data['product']}")
                except Exception as e:
                    logger.error(f"Error creating transfer item: {str(e)}")
                    raise ValidationError(f"Error creating transfer item: {str(e)}")
        
        logger.info(f"Transfer {instance.id} updated successfully")
        return instance