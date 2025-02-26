# Em BackEnd/apps/deliveries/tracking/admin.py
from django.contrib import admin
from .models import DeliveryLocationUpdate, DeliveryRoute, DeliveryStatusUpdate

@admin.register(DeliveryLocationUpdate)
class DeliveryLocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'created_at', 'accuracy', 'speed')
    list_filter = ('delivery', 'created_at')
    search_fields = ('delivery__number',)
    date_hierarchy = 'created_at'

@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'estimated_distance', 'estimated_arrival')
    list_filter = ('delivery', 'created_at')
    search_fields = ('delivery__number',)

@admin.register(DeliveryStatusUpdate)
class DeliveryStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('delivery__number', 'notes')
    date_hierarchy = 'created_at'