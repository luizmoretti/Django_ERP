from django.contrib import admin
from .models import Employeer


@admin.register(Employeer)
class EmployeerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'user__user_type','age', 'created_at', 'updated_at', 'created_by', 'updated_by', 'companie']
    list_filter = ['created_at', 'updated_at', 'created_by', 'updated_by', 'companie']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'companie__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
