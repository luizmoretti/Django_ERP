from django.contrib import admin
from django.contrib import messages
from .models import Product, ProductSku, ProductInStoreID
from apps.inventory.supplier.models import Supplier
from .service.product_services import ProductServices
import logging

# Configurar logger
logger = logging.getLogger(__name__)


class ProductInStoreIDInline(admin.TabularInline):
    model = ProductInStoreID
    extra = 0
    exclude = ['companie', 'created_at', 'updated_at', 'created_by', 'updated_by', 'id']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductInStoreIDInline]
    list_display = ('id', 'name', 'quantity', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'created_by__name', 'updated_by__name')
    readonly_fields = ('id', 'quantity', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    actions = ['search_on_home_depot', 'update_from_home_depot']
    
    def search_on_home_depot(self, request, queryset):
        """Search for products on Home Depot and save their IDs"""
        success_count = 0
        error_count = 0
        
        for product in queryset:
            result = ProductServices.search_and_save_home_depot_id(str(product.id))
            
            if result['status'] == 'success':
                success_count += 1
                self.message_user(
                    request,
                    f"Success: {result['message']}. Price: ${result.get('price')}",
                    level=messages.SUCCESS
                )
            else:
                error_count += 1
                self.message_user(
                    request,
                    f"Error: {result['message']}",
                    level=messages.ERROR
                )
                
        # Mensagem final
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully processed {success_count} products",
                level=messages.SUCCESS
            )
        if error_count > 0:
            self.message_user(
                request,
                f"Failed to process {error_count} products",
                level=messages.WARNING
            )
            
    search_on_home_depot.short_description = "Search and save Home Depot IDs"
    
    def update_from_home_depot(self, request, queryset):
        """Update product information from Home Depot"""
        success_count = 0
        error_count = 0
        
        for product in queryset:
            result = ProductServices.update_product_from_home_depot(str(product.id))
            
            if result['status'] == 'success':
                success_count += 1
                self.message_user(
                    request,
                    f"Success: {result['message']}. Price: ${result.get('price')}",
                    level=messages.SUCCESS
                )
            else:
                error_count += 1
                self.message_user(
                    request,
                    f"Error: {result['message']}",
                    level=messages.ERROR
                )
                
        # Mensagem final
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully updated {success_count} products",
                level=messages.SUCCESS
            )
        if error_count > 0:
            self.message_user(
                request,
                f"Failed to update {error_count} products",
                level=messages.WARNING
            )
            
    update_from_home_depot.short_description = "Update from Home Depot"


@admin.register(ProductSku)
class ProductSkuAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('product', 'sku', 'created_at', 'updated_at')
    search_fields = ('product__name', 'sku', 'created_by__name', 'updated_by__name')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
