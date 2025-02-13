from django.contrib import admin
from .models import Delivery, DeliveryItems

class DeliveryItemsInline(admin.TabularInline):
    model = DeliveryItems
    extra = 0
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    # readonly_fields = ['total']

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    inlines = [DeliveryItemsInline]
    list_display = ['number', 'origin', 'destiny', 'status', 'created_at', 'updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'companie', 
                      'created_by', 'updated_by', 'number']
