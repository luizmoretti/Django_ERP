from django.contrib import admin
from .models import Transfer, TransferItems


class TransferItemsInline(admin.TabularInline):
    model = TransferItems
    extra = 0
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    autocomplete_fields = ('product', )
    

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    inlines = [TransferItemsInline]
    list_display = ('origin', 'destiny', 'created_at', 'updated_at', 'get_created_by_full_name', 'get_updated_by_full_name')
    list_filter = ('origin', 'destiny', 'created_at', 'updated_at')
    search_fields = ('origin__name', 'destiny__name')
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
