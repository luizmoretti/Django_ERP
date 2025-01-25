from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import NormalUser

@receiver(user_logged_in)
def update_user_ip(sender, user, request, **kwargs):
    """
    Signal para atualizar o IP do usuário quando ele faz login
    """
    if hasattr(user, 'get_ip_on_login'):
        user.get_ip_on_login(request)

@receiver(post_save, sender=NormalUser)
def ensure_ip_on_create(sender, instance, created, **kwargs):
    """
    Signal para garantir que o IP seja salvo na criação do usuário
    """
    if created and not instance.ip and hasattr(instance, '_request'):
        instance.get_ip_on_login(instance._request)