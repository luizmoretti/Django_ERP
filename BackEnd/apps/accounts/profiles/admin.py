from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'city', 'country', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'companie')
