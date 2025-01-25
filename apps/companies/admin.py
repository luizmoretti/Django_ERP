from django.contrib import admin
from .models import Companie, PickUpCompanieAddress


@admin.register(Companie)
class CompanieAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'address', 'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by']
    list_filter = ['created_at', 'updated_at', 'created_by', 'updated_by']
    search_fields = ['name', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    
@admin.register(PickUpCompanieAddress)
class PickUpCompanieAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'companie', 'full_address', 'created_at', 'updated_at']
