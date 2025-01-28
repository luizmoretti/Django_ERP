from django.contrib import admin
from .models import Outflow, OutflowItems



class OutflowItemsInline(admin.TabularInline):
    model = OutflowItems
    extra = 0
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    

@admin.register(Outflow)
class OutflowAdmin(admin.ModelAdmin):
    inlines = [OutflowItemsInline]
    list_display = ('get_origin_address', 'get_destiny_address', 'created_at', 'updated_at', 'get_created_by_full_name', 'get_updated_by_full_name')
    list_filter = ('origin', 'destiny', 'created_at', 'updated_at')
    search_fields = ('origin__name', 'destiny_full_name')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return "-"
    get_created_by_full_name.short_description = "Created By"
    
    def get_origin_address(self, obj):
        if obj.origin:
            if obj.origin.companie:
                return obj.origin.companie.pick_up_companie_address_companie.first().full_address
        return "-"
    get_origin_address.short_description = "Origin"
    
    def get_destiny_address(self, obj):
        if obj.destiny:
            if obj.destiny.another_shipping_address:
                return obj.destiny.customer_project_address_customer.first()
        return "-"
    get_destiny_address.short_description = "Destiny"
    
    def get_updated_by_full_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return "-"
    get_updated_by_full_name.short_description = "Updated By"
