import logging
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from crum import get_current_user
from django.contrib.auth.models import AnonymousUser
from apps.accounts.models import NormalUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(user_id):
    try:
        return NormalUser.objects.get(id=user_id)
    except NormalUser.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for token-based WebSocket authentication.
    """

    async def __call__(self, scope, receive, send):
        try:
            # Log all headers for debugging
            headers = dict(scope.get('headers', []))
            logger.info("WebSocket connection attempt")
            logger.debug(f"Headers received: {headers}")
            
            # Extract token from headers
            auth_header = headers.get(b'authorization', b'').decode('utf-8')
            logger.debug(f"Authorization header: {auth_header}")

            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    # Validate token
                    logger.debug(f"Attempting to validate token: {token[:10]}...")
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    logger.debug(f"Token valid. User ID: {user_id}")
                    
                    # Get user from database
                    scope['user'] = await get_user(user_id)
                    if scope['user'].is_authenticated:
                        logger.info(f"User authenticated successfully: {scope['user'].email}")
                    else:
                        logger.warning(f"User {user_id} not found in database")
                        scope['user'] = AnonymousUser()
                    
                except (InvalidToken, TokenError, InvalidTokenError) as e:
                    logger.error(f"Token validation error: {str(e)}")
                    scope['user'] = AnonymousUser()
            else:
                logger.warning("No Bearer token found in headers")
                scope['user'] = AnonymousUser()
                
        except Exception as e:
            logger.error(f"Authentication middleware error: {str(e)}")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    """Helper function to wrap TokenAuthMiddleware around the ASGI application."""
    return TokenAuthMiddleware(inner)