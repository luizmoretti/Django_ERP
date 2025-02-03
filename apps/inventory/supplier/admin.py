from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_number', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'tax_number', 'created_by__name', 'updated_by__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'companie')
