import logging
from typing import Optional, Dict, Any, Union
from uuid import UUID
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()

def send_notification(
    user_id: Union[str, UUID],
    title: str,
    message: str,
    app_name: str = "",
    notification_type: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Envia uma notificação em tempo real para um usuário específico.
    
    Args:
        user_id: ID do usuário (UUID ou string)
        title: Título da notificação
        message: Mensagem da notificação
        app_name: Nome da aplicação que está enviando a notificação
        notification_type: Tipo da notificação (info, warning, error, success)
        data: Dados adicionais da notificação (opcional)
    
    Returns:
        bool: True se a notificação foi enviada com sucesso, False caso contrário
    """
    try:
        # Garante que user_id é uma string
        user_id_str = str(user_id)
        
        # Cria a notificação no banco de dados
        try:
            user = User.objects.get(id=user_id_str)
            notification = Notification.objects.create(
                recipient=user,
                title=title,
                app_name=app_name,
                message=message,
                notification_type=notification_type,
                data=data or {}
            )
            notification_id = str(notification.id)
        except User.DoesNotExist:
            logger.error(f"User {user_id_str} not found")
            return False
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            notification_id = "temp-" + user_id_str
        
        # Envia a notificação via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id_str}",
            {
                "type": "notification_message",
                "title": title,
                "message": message,
                # "notification_id": notification_id,
                "data": {
                    "app_name": app_name,
                    "type": notification_type,
                    **(data or {})
                }
            }
        )
        
        logger.info(f"Notification sent to user {user_id_str}: {title}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return False

def send_bulk_notification(
    user_ids: list[Union[str, UUID]],
    title: str,
    message: str,
    app_name: str = "",
    notification_type: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, bool]:
    """
    Envia uma notificação em tempo real para múltiplos usuários.
    
    Args:
        user_ids: Lista de IDs de usuários
        title: Título da notificação
        message: Mensagem da notificação
        app_name: Nome da aplicação que está enviando a notificação
        notification_type: Tipo da notificação (info, warning, error, success)
        data: Dados adicionais da notificação (opcional)
    
    Returns:
        Dict[str, bool]: Dicionário com o status de envio para cada usuário
    """
    results = {}
    for user_id in user_ids:
        results[str(user_id)] = send_notification(
            user_id=user_id,
            title=title,
            message=message,
            app_name=app_name,
            notification_type=notification_type,
            data=data
        )
    return results