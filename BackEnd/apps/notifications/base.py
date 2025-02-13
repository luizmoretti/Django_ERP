# Adicionar em apps/notifications/base.py
from apps.accounts.models import NormalUser
from apps.notifications.utils import send_notification


class BaseNotificationHandler:
    @staticmethod
    def get_recipients_by_type(*user_types):
        return NormalUser.objects.filter(
            user_type__in=user_types,
            is_active=True
        )
    
    @staticmethod
    def send_to_recipients(recipient_ids, title, message, app_name, notification_type, data):
        for user_id in recipient_ids:
            send_notification(
                user_id=user_id,
                title=title,
                app_name=app_name,
                message=message,
                notification_type=notification_type,
                data=data
            )