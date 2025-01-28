from django.contrib import admin
from .models import Product, ProductSku

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'quantity', 'companie', 'created_at', 'updated_at', 'get_created_by_full_name', 'get_updated_by_full_name')
    list_filter = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'created_by__first_name', 'created_by__last_name', 'updated_by__first_name', 'updated_by__last_name')
    readonly_fields = ('id', 'quantity', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return "-"
    get_created_by_full_name.short_description = "Created By"
    
    def get_updated_by_full_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return "-"
    get_updated_by_full_name.short_description = "Updated By"

@admin.register(ProductSku)
class ProductSkuAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'companie', 'created_at', 'updated_at', 'get_created_by_full_name', 'get_updated_by_full_name')
    list_filter = ('product', 'sku', 'created_at', 'updated_at')
    search_fields = ('product__name', 'sku', 'created_by__first_name', 'created_by__last_name', 'updated_by__first_name', 'updated_by__last_name')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return "-"
    get_created_by_full_name.short_description = "Created By"
    
    def get_updated_by_full_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return "-"
    get_updated_by_full_name.short_description = "Updated By"
