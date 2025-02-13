from rest_framework import serializers
from ..product.models import Product
from .models import Warehouse, WarehouseProduct
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class WareHouseProductSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field='name', queryset=Product.objects.all())
    current_quantity = serializers.IntegerField()
    
    class Meta:
        model = WarehouseProduct
        fields = ['product', 'current_quantity']
    
    
class WarehouseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    name = serializers.CharField(required=True)
    limit = serializers.IntegerField(required=False, default=0)
    quantity = serializers.IntegerField(required=False, read_only=True)
    
    items = WareHouseProductSerializer(many=True, read_only=True)
    
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    companie = serializers.SerializerMethodField(read_only=True)
    
    def get_created_by(self, obj) -> str | None:
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str | None:
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def get_companie(self, obj) -> str | None:
        if obj.companie:
            return f'[{obj.companie.type}] {obj.companie.name}'
        return None
    
    def validate(self, attrs):
        if attrs['limit'] < 0:
            raise serializers.ValidationError("Limit cannot be negative.")
        
        if attrs['name'] == "":
            raise serializers.ValidationError("Name is required")
        
        # Check if warehouse with same name exists
        existing_warehouse = Warehouse.objects.filter(name=attrs['name']).first()
        
        if existing_warehouse:
            # If this is a creation (no self.instance) or if the existing warehouse
            # is different from the one being updated
            if not self.instance or existing_warehouse.id != self.instance.id:
                raise serializers.ValidationError("Warehouse with this name already exists")
        
        return attrs
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 
            'name', 
            'limit', 
            'quantity', 
            'items', 
            'created_at', 
            'updated_at',
            'created_by',
            'updated_by',
            'companie'
            ]
        
        read_only_fields = [
            'id', 
            'quantity',
            'items',
            'created_at', 
            'updated_at',
            'created_by',
            'updated_by',
            'companie'
            ]
        
        @transaction.atomic
        def create(self, validated_data) -> Warehouse:
            warehouse = Warehouse.objects.create(**validated_data)
            return warehouse
        
        @transaction.atomic
        def update(self, instance, validated_data) -> Warehouse:
            return super().update(instance, validated_data)