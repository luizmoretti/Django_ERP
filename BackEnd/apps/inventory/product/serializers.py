from rest_framework import serializers
from .models import Product, ProductSku
from apps.inventory.brand.models import Brand
from apps.inventory.categories.models import Category


class ProductSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSku
        fields = [
            'sku'
        ]
        
class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, help_text='The name of the product', required=True)
    description = serializers.CharField(max_length=255, help_text='The description of the product', required=False)
    quantity = serializers.IntegerField(help_text='The total quantity of the product', read_only=True)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), help_text='The brand of the product', required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), help_text='The category of the product', required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='Current price of the product', required=False, default=0.00)
    skus = ProductSKUSerializer(many=True, read_only=False, required=False)
    
    
    updated_by = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    companie = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'quantity',
            'brand',
            'category',
            'price',
            'skus',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'companie'
        ]
        read_only_fields = [
            'quantity', 
            'created_at', 
            'updated_at',
            'created_by',
            'updated_by',
            'companie'
            ]
        
    def get_updated_by(self, obj) -> str | None:
        """Get the name of the user who last updated the product"""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def get_created_by(self, obj) -> str | None:
        """Get the name of the user who created the product"""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_companie(self, obj) -> str | None:
        """Get the name of the companie"""
        if obj.companie:
            return f'[{obj.companie.type}] {obj.companie.name}'
        return None
    
    
    def create(self, validated_data):
        """Create a new product"""
        product = Product.objects.create(**validated_data)
        return product
    
    
    def update(self, instance, validated_data):
        """Update an existing product"""
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.category = validated_data.get('category', instance.category)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance
    