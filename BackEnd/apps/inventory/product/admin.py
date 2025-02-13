from django.contrib import admin
from .models import Product, ProductSku

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'quantity', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'created_by__name', 'updated_by__name')
    readonly_fields = ('id', 'quantity', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')

@admin.register(ProductSku)
class ProductSkuAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('product', 'sku', 'created_at', 'updated_at')
    search_fields = ('product__name', 'sku', 'created_by__name', 'updated_by__name')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
