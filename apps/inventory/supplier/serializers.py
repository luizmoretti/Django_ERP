from rest_framework import serializers
from .models import Supplier, SupplierProductPrice
from apps.inventory.product.serializers import ProductSerializer

class SupplierProductPriceSerializer(serializers.ModelSerializer):
    """Serializer for supplier product prices
    
    Fields:
        - supplier: UUID of the supplier
        - product: UUID of the product
        - unit_price: Decimal price per unit
        - last_purchase_date: Date of last purchase
        - is_current: Boolean indicating if this is the current price
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SupplierProductPrice
        fields = [
            'product_name',
            'unit_price',
            'last_purchase_date',
            'is_current',
        ]
        read_only_fields = ['product_name']

class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for suppliers
    
    Fields:
        - name: Supplier name
        - tax_number: Tax identification number
        - phone: Contact phone
        - email: Contact email
        - address: Physical address
        - city: City
        - state: State/Province
        - zip_code: Postal code
        - country: Country
        - product_prices: List of product prices from this supplier
    """
    product_prices = SupplierProductPriceSerializer(many=True, read_only=True)
    
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    companie = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'tax_number',
            'phone',
            'email',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
            'product_prices',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'companie'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'companie', 'product_prices']
        
    def get_created_by(self, obj) -> str:
        """Get the name of the user who created the supplier"""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_updated_by(self, obj) -> str:
        """Get the name of the user who last updated the supplier"""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return None
    
    def get_companie(self, obj) -> str | None:
        """Get the name of the companie"""
        if obj.companie:
            return f'[{obj.companie.type}] {obj.companie.name}'
        return None