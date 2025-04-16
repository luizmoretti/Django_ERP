from django.db import models
from basemodels.models import BaseModel
from django.conf import settings
from django.utils.translation import gettext


class Notification(BaseModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    app_name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=100)
    data = models.JSONField(default=dict)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = gettext('Notification')
        verbose_name_plural = gettext('Notifications')
        
    def __str__(self):
        return f"{self.recipient.email} - {self.title}"