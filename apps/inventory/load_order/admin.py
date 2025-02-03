from django.contrib import admin
from .models import LoadOrder, LoadOrderItem


class LoadOrderItemInline(admin.TabularInline):
    model = LoadOrderItem
    extra = 0
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    

@admin.register(LoadOrder)
class LoadOrderAdmin(admin.ModelAdmin):
    inlines = [LoadOrderItemInline]
    list_display = ('order_number', 'load_date', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('order_number', 'created_by__name', 'updated_by__name')
    readonly_fields = ('id', 'order_number', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    
    # def get_created_by_full_name(self, obj):
    #     if obj.created_by:
    #         return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
    #     return "-"
    # get_created_by_full_name.short_description = "Created By"
    
    # def get_updated_by_full_name(self, obj):
    #     if obj.updated_by:
    #         return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
    #     return "-"
    # get_updated_by_full_name.short_description = "Updated By"