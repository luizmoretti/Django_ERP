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
    list_display = ('origin', 'destiny', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('origin', 'destiny', 'created_at', 'updated_at')
    search_fields = ('origin__name', 'destiny__name')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
