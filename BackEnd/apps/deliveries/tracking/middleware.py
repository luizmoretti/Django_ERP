import logging
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from apps.accounts.models import User
from rest_framework_simplejwt.tokens import AccessToken
from core.unified_middleware import UnifiedAuthMiddlewareStack
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(user_id):
    """
    Asynchronously retrieve a user by ID.
    
    Args:
        user_id: The ID of the user to retrieve.
        
    Returns:
        User or AnonymousUser: The user if found, otherwise AnonymousUser.
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

@database_sync_to_async
def get_delivery_permissions(user, delivery_id):
    """
    Check if a user has permission to access a specific delivery.
    
    Args:
        user: The user to check permissions for.
        delivery_id: The ID of the delivery to check access for.
        
    Returns:
        bool: True if the user has permission, False otherwise.
    """
    if user.is_anonymous:
        return False
        
    try:
        from apps.deliveries.models import Delivery
        
        # For authenticated users, check permissions
        employeer = user.employeer
        return Delivery.objects.filter(
            id=delivery_id,
            companie=employeer.companie
        ).exists()
    except Exception as e:
        logger.error(f"Error checking delivery permissions: {str(e)}")
        return False

class DeliveryTokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for token-based WebSocket authentication for delivery tracking.
    """

    async def __call__(self, scope, receive, send):
        try:
            # Log connection attempt
            headers = dict(scope.get('headers', []))
            logger.info("[DELIVERY TRACKING] WebSocket connection attempt")
            
            # Extract token from headers
            auth_header = headers.get(b'authorization', b'').decode('utf-8')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    # Validate token
                    logger.debug(f"[DELIVERY TRACKING] Validating token: {token[:10]}...")
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    
                    # Get user from database
                    scope['user'] = await get_user(user_id)
                    
                    if scope['user'].is_authenticated:
                        logger.info(f"[DELIVERY TRACKING] User authenticated: {scope['user'].email}")
                        
                        # Check delivery-specific permissions if delivery_id is in URL
                        if 'url_route' in scope and 'kwargs' in scope['url_route'] and 'delivery_id' in scope['url_route']['kwargs']:
                            delivery_id = scope['url_route']['kwargs']['delivery_id']
                            has_permission = await get_delivery_permissions(scope['user'], delivery_id)
                            
                            if not has_permission:
                                logger.warning(f"[DELIVERY TRACKING] User {scope['user'].email} does not have permission to access delivery {delivery_id}")
                                scope['user'] = AnonymousUser()
                    else:
                        logger.warning(f"[DELIVERY TRACKING] User {user_id} not found in database")
                        scope['user'] = AnonymousUser()
                        
                except (InvalidToken, TokenError, InvalidTokenError) as e:
                    logger.error(f"[DELIVERY TRACKING] Token validation error: {str(e)}")
                    scope['user'] = AnonymousUser()
            else:
                logger.warning("[DELIVERY TRACKING] No Bearer token found in headers")
                scope['user'] = AnonymousUser()
                
        except Exception as e:
            logger.error(f"[DELIVERY TRACKING] Authentication middleware error: {str(e)}")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

def DeliveryTokenAuthMiddlewareStack(inner):
    """
    Deprecated: Use UnifiedAuthMiddlewareStack instead.
    Kept for backward compatibility.
    """
    return UnifiedAuthMiddlewareStack(inner)