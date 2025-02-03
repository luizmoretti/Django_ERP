from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle, VehicleMilageHistory, VehicleMaintenance, VehicleMaintenanceHistory


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'plate', 'vehicle_info', 'driver_details', 'type', 'is_active', 'created_at')
    list_filter = ('type', 'created_at', 'companie')
    search_fields = ('plate', 'vehicle', 'driver__first_name', 'driver__last_name', 'drivers_license')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'companie')
    fieldsets = (
        ('Vehicle Information', {
            'fields': (
                'plate', 'name', 'vehicle_maker', 'vehicle_model', 'vehicle_color', 'type', 'vehicle_is_active'
            )
        }),
        ('Driver Information', {
            'fields': (
                'driver', 'drivers_license'
            )
        }),
        ('Audit Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by', 'companie'
            )
        })
    )
    
    def vehicle_info(self, obj):
        return format_html(
            "<strong>{}</strong> - {} {}",
            obj.name,
            obj.vehicle_maker,
            obj.vehicle_model
        )
    vehicle_info.short_description = "Vehicle Info"
    
    def driver_details(self, obj):
        if obj.driver:
            return format_html(
                "<strong>{}</strong><br/>License: {}",
                obj.driver.display_name,
                obj.drivers_license
            )
        return "-"
    driver_details.short_description = "Driver Details"


@admin.register(VehicleMilageHistory)
class VehicleMilageHistoryAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'milage', 'created_at')
    list_filter = ('vehicle', 'created_at')
    search_fields = ('vehicle__tag', 'vehicle__vehicle')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        (None, {
            'fields': (
                'vehicle', 'milage'
            )
        }),
        ('Audit Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            )
        })
    )


@admin.register(VehicleMaintenance)
class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_status', 'scheduled_info', 'created_at')
    list_filter = ('is_in_service', 'is_scheduled', 'created_at')
    search_fields = ('vehicle__tag', 'vehicle__vehicle', 'reason')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': (
                'vehicle', 'reason', 'is_in_service'
            )
        }),
        ('Schedule', {
            'fields': (
                'is_scheduled', 'date_of_scheduled'
            )
        }),
        ('Audit Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            )
        })
    )
    
    def maintenance_status(self, obj):
        status = "In Service" if obj.is_in_service else "Completed"
        color = "red" if obj.is_in_service else "green"
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            status
        )
    maintenance_status.short_description = "Status"
    
    def scheduled_info(self, obj):
        if obj.is_scheduled:
            return format_html(
                '<span style="color: blue;">Scheduled for: {}</span>',
                obj.date_of_scheduled.strftime("%Y-%m-%d %H:%M")
            )
        return "Not Scheduled"
    scheduled_info.short_description = "Schedule"


@admin.register(VehicleMaintenanceHistory)
class VehicleMaintenanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('vehicle_maintenance', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('vehicle_maintenance__vehicle__tag', 'vehicle_maintenance__vehicle__vehicle')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        (None, {
            'fields': (
                'vehicle_maintenance',
            )
        }),
        ('Audit Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            )
        })
    )
