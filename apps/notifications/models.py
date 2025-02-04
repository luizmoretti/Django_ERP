from django.db import models
from basemodels.models import BaseModel
from apps.accounts.models import NormalUser
from django.utils.translation import gettext_lazy as _


class Notification(BaseModel):
    recipient = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    app_name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=100)
    data = models.JSONField(default=dict)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        
    def __str__(self):
        return f"{self.title} - {self.recipient.email}"