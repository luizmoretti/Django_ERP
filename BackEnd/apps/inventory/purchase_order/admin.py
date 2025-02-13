from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [PurchaseOrderItemInline]
    list_display = ('order_number', 'supplier', 'order_date', 'expected_delivery', 'status', 'total', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('order_date', 'expected_delivery', 'status', 'created_at', 'updated_at')
    search_fields = ('order_number', 'supplier__name', 'created_by__name', 'updated_by__name')
    readonly_fields = ('order_number','id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')