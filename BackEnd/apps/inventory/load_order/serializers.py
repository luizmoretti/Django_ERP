from rest_framework import serializers
from .models import LoadOrder, LoadOrderItem
from apps.companies.customers.models import Customer
from apps.deliveries.vehicles.models import Vehicle
from apps.inventory.product.models import Product
from rest_framework.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class LoadOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, required=True)
    quantity = serializers.IntegerField(required=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = LoadOrderItem
        fields = [
            'product',
            'product_name', 
            'quantity'
        ]
        read_only_fields = ['product_name']
        
    def get_product_name(self, obj) -> str:
        if obj.product:
            return obj.product.name
        return ''
    
    def validate(self, attrs):
        if not attrs.get('product'):
            raise ValidationError("Product is required")
        
        if not attrs.get('quantity'):
            raise ValidationError("Quantity is required")
        return attrs
    
    def validate_quantity(self, quantity):
        if quantity < 1:
            raise ValidationError("Quantity must be positive")
        return quantity
    


class LoadOrderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    order_number = serializers.CharField(read_only=True)
    
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False, write_only=True)
    customer_name = serializers.SerializerMethodField(read_only=True)
    
    load_to = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), required=True, write_only=True)
    load_to_name = serializers.SerializerMethodField(read_only=True)
    
    load_date = serializers.DateField(required=True)
    
    
    items = LoadOrderItemSerializer(many=True, read_only=True)
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    
    
    companie = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = LoadOrder
        fields = [
            'id',
            'order_number', 
            'customer',
            'customer_name',
            'load_to', 
            'load_to_name',
            'load_date',
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
            'order_number',
            'customer_name',
            'load_to_name',
            'items',
            'companie',
            'created_at', 
            'updated_at',
            'created_by',
            'updated_by'
        ]
        
    def get_customer_name(self, obj) -> str:
        return obj.customer.first_name + ' ' + obj.customer.last_name
    
    def get_load_to_name(self, obj) -> str:
        return obj.load_to.name + ' | ' + obj.load_to.plate
    
    def get_companie(self, obj) -> str | None:
        if obj.companie:
            return f'[{obj.companie.type}] {obj.companie.name}'
        return None

    def get_created_by(self, obj) -> str | None:
        """Get the name of the user who created the load order"""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str | None:
        """Get the name of the user who last updated the load order"""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    @transaction.atomic
    def create(self, validated_data):
        """Create a new load order with items
        
        Creates the load order and its associated items in a single transaction.
        """
        items_data = validated_data.pop('items_data')
        load_order = LoadOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            item_serializer = LoadOrderItemSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            LoadOrderItem.objects.create(
                load_order=load_order,
                product=item_serializer.validated_data['product'],
                quantity=item_serializer.validated_data['quantity'],
                created_by=load_order.created_by,
                updated_by=load_order.updated_by,
            )
        return load_order 
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a load order and its items
        
        Updates the load order and its associated items in a single transaction.
        """
        if 'items_data' in validated_data:
            items_data = validated_data.pop('items_data')
            instance.items.all().delete()
            
            for item_data in items_data:
                item_serializer = LoadOrderItemSerializer(data=item_data)
                item_serializer.is_valid(raise_exception=True)
                LoadOrderItem.objects.create(
                    load_order=instance,
                    product=item_serializer.validated_data['product'],
                    quantity=item_serializer.validated_data['quantity'],
                    created_by=instance.created_by,
                    updated_by=instance.updated_by,
                )
        return super().update(instance, validated_data)
            