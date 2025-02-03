from django.contrib import admin
from .models import Warehouse, WarehouseProduct


class WareHouseProductInline(admin.TabularInline):
    model = WarehouseProduct
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    autocomplete_fields = ('product', )
    extra = 1
    

@admin.register(Warehouse)
class WareHouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'limit', 'quantity', 'created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = (WareHouseProductInline, )
    search_fields = ('name', 'created_by', 'updated_by')
    list_filter = ('name', 'created_at', 'updated_at', 'created_by', 'updated_by')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')