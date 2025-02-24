from django.contrib import admin
from .models import Movement

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'type', 'origin', 'destination', 'status', 'total_items', 'total_value', 'data']