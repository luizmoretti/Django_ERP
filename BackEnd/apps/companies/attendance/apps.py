from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.companies.attendance'
    
    def ready(self):
        import apps.companies.attendance.signals
