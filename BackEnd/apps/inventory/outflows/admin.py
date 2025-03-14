from django.contrib import admin
from .models import Outflow, OutflowItems



class OutflowItemsInline(admin.TabularInline):
    model = OutflowItems
    extra = 0
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    

@admin.register(Outflow)
class OutflowAdmin(admin.ModelAdmin):
    inlines = [OutflowItemsInline]
    list_display = ('get_origin_address', 'get_destiny_address', 'status', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('origin', 'destiny', 'created_at', 'updated_at')
    search_fields = ('origin__name', 'destiny__name')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    
    def get_origin_address(self, obj):
        if obj.origin:
            if obj.origin.companie:
                return obj.origin.companie.companie_pick_up_address.first().full_address
        return "-"
    get_origin_address.short_description = "Origin"
    
    def get_destiny_address(self, obj):
        if obj.destiny:
            if obj.destiny.another_shipping_address:
                return obj.destiny.project_address.first()
        return obj.destiny.project_address.first()
    get_destiny_address.short_description = "Destiny"