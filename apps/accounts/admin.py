from django.contrib import admin
from .models import NormalUser


@admin.register(NormalUser)
class NormalUserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'type',
        'is_active',
        'is_staff',
        'is_superuser',
        'ip',
    )
    readonly_fields = ('date_joined', 'last_login')
    
    def save_model(self, request, obj, form, change):
        obj._request = request
        super().save_model(request, obj, form, change)
