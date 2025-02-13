from django.contrib import admin
from .models import Inflow, InflowItems

class InflowItemsAdmin(admin.TabularInline):
    model = InflowItems
    exclude = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    extra = 1

# Register your models here.
@admin.register(Inflow)
class InflowAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destiny', 'status', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('origin', 'destiny', 'created_at', 'updated_at')
    search_fields = ('origin__name', 'destiny__name')
    readonly_fields = ('id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = [InflowItemsAdmin]