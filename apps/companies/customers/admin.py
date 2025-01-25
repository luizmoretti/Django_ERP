from django.contrib import admin
from apps.companies.customers.models import Customer, CustomerProjectAddress, CustomerBillingAddress


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'address', 'city', 'zip_code', 'country', 'phone', 'email', 'created_at', 'updated_at']
    search_fields = ['full_name', 'address', 'city', 'zip_code', 'country', 'phone', 'email']
    list_filter = ['created_at', 'updated_at', 'companie']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'companie']


@admin.register(CustomerProjectAddress)
class CustomerProjectAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'address','city', 'state', 'zip_code', 'country', 'created_at', 'updated_at']
    search_fields = ['customer__name', 'customer__companie__name']
    list_filter = ['created_at', 'updated_at', 'customer']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    

@admin.register(CustomerBillingAddress)
class CustomerBillingAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'address', 'city', 'state', 'zip_code', 'country', 'created_at', 'updated_at']
    search_fields = ['customer__name', 'customer__companie__name']
    list_filter = ['created_at', 'updated_at', 'customer']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']