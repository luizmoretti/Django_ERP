from django.shortcuts import render
from django.core.cache import cache
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from .models import NormalUser
from .serializers import UserSerializer, ListAllUsersSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging

# Configure logger for the accounts app
logger = logging.getLogger(__name__)



class BaseUserView:
    """
    Base view class with common configurations for user views.
    
    Provides:
        - Common queryset with optimized related field loading
        - Default permission class requiring authentication
        - Logging setup for user operations
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # Filtra apenas usuários da mesma empresa
            employeer = user.employeer_user
            return NormalUser.objects.filter(
                employeer_user__companie=employeer.companie
            ).select_related().prefetch_related('groups', 'user_permissions')
        except:
            return NormalUser.objects.none()


@extend_schema_view(
    post=extend_schema(
        tags=["Users - Authentication"],
        operation_id="create_user",
        summary="Create new user account",
        description="""
        Creates a new user account with the provided information.
        
        The email address must be unique and will be used as the username.
        Password must meet security requirements:
        - Minimum 8 characters
        - At least one number
        - At least one letter
        - At least one uppercase letter
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string', 'format': 'password', 'minLength': 8},
                    'first_name': {'type': 'string', 'minLength': 1},
                    'last_name': {'type': 'string', 'minLength': 1},
                    'img': {'type': 'string', 'format': 'binary'},
                },
                'required': ['email', 'password', 'first_name', 'last_name']
            }
        },
        responses={
            201: UserSerializer,
            400: {
                'description': 'Invalid input data',
                'type': 'object',
                'properties': {
                    'email': {'type': 'array', 'items': {'type': 'string'}},
                    'password': {'type': 'array', 'items': {'type': 'string'}},
                }
            }
        }
    )
)
class UserCreateView(BaseUserView, CreateAPIView):
    """
    View for creating new user accounts.
    
    This view handles user registration with comprehensive validation
    and error handling. It's the only view that allows unauthenticated
    access.
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Allows creation without authentication

    def perform_create(self, serializer):
        try:
            instance = serializer.save()
            instance._request = self.request
            instance.get_ip_on_login(self.request)
            logger.info(
                f"User created successfully: {instance.email}",
                extra={
                    'user_id': instance.id,
                    'ip': instance.ip
                }
            )
        except Exception as e:
            logger.error(
                f"Error creating user: {str(e)}",
                extra={
                    'email': serializer.validated_data.get('email'),
                    'error': str(e)
                },
                exc_info=True
            )
            raise


@extend_schema_view(
    get=extend_schema(
        tags=["Users - Authentication"],
        operation_id="current_user",
        summary="Get current user details",
        description="Returns the complete profile of the currently authenticated user",
        responses={
            200: UserSerializer,
            401: {'description': 'Authentication credentials not provided'}
        }
    )
)
class CurrentUserView(BaseUserView, RetrieveAPIView):
    """
    View for retrieving current user's profile.
    
    This view returns the complete profile of the authenticated user,
    including groups and permissions.
    """
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        logger.info(
            f"Current user profile accessed: {user.email}",
            extra={'user_id': user.id}
        )
        return user


@extend_schema_view(
    get=extend_schema(
        tags=["Users - Management"],
        operation_id="retrieve_user",
        summary="Get specific user details",
        description="Retrieves complete profile information for a specific user by UUID",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the user to retrieve',
                required=True,
            ),
        ],
        responses={
            200: UserSerializer,
            404: {'description': 'User not found'}
        }
    )
)
class UserRetrieveView(BaseUserView, RetrieveAPIView):
    """
    View for retrieving specific user profiles.
    
    Allows administrators to view complete profile information
    for any user in the system.
    """
    serializer_class = UserSerializer
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(
                f"User profile retrieved: {instance.email}",
                extra={
                    'user_id': instance.id,
                    'requester_id': request.user.id
                }
            )
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error retrieving user profile: {str(e)}",
                extra={
                    'pk': kwargs.get('pk'),
                    'requester_id': request.user.id
                },
                exc_info=True
            )
            raise


@extend_schema_view(
    put=extend_schema(
        tags=["Users - Management"],
        operation_id="update_user",
        summary="Update user profile",
        description="""
        Updates user profile information.
        
        Can update:
        - Personal information (name, email)
        - Password (with validation)
        - Profile image
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the user to update',
                required=True,
            ),
        ],
        responses={
            200: UserSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'User not found'}
        }
    ),
    patch=extend_schema(
        tags=["Users - Management"],
        operation_id="partial_update_user",
        summary="Partially update user profile",
        description="""
        Partially updates user profile information.
        
        Can update:
        - Personal information (name, email)
        - Password (with validation)
        - Profile image
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the user to update',
                required=True,
            ),
        ],
        responses={
            200: UserSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'User not found'}
        }
    )
)
class UserUpdateView(BaseUserView, UpdateAPIView):
    """
    View for updating user profiles.
    
    Handles complete and partial updates to user profiles,
    with special handling for password changes.
    """
    serializer_class = UserSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        try:
            old_email = serializer.instance.email
            instance = serializer.save()
            instance._request = self.request
            instance.get_ip_on_login(self.request)
            
            logger.info(
                f"User profile updated: {instance.email}",
                extra={
                    'user_id': instance.id,
                    'old_email': old_email,
                    'new_email': instance.email,
                    'updated_fields': list(serializer.validated_data.keys())
                }
            )
        except Exception as e:
            logger.error(
                f"Error updating user profile: {str(e)}",
                extra={
                    'user_id': serializer.instance.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise
    
    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error updating user profile: {str(e)}",
                extra={
                    'user_id': instance.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise


@extend_schema_view(
    delete=extend_schema(
        tags=["Users - Management"],
        operation_id="deactivate_user",
        summary="Deactivate user account",
        description="""
        Soft deletes a user account by marking it as inactive.
        The account data is preserved but the user cannot login.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the user to deactivate',
                required=True,
            ),
        ],
        responses={
            204: {'description': 'User successfully deactivated'},
            404: {'description': 'User not found'}
        }
    )
)
class UserDeleteView(BaseUserView, DestroyAPIView):
    """
    View for deactivating user accounts.
    
    Implements soft delete by marking accounts as inactive
    rather than removing them from the database.
    """
    serializer_class = UserSerializer
    
    def perform_destroy(self, instance):
        try:
            email = instance.email
            instance.is_active = False
            instance.save(update_fields=['is_active'])
            
            logger.info(
                f"User account deactivated: {email}",
                extra={
                    'user_id': instance.id,
                    'deactivated_by': self.request.user.id
                }
            )
        except Exception as e:
            logger.error(
                f"Error deactivating user account: {str(e)}",
                extra={
                    'user_id': instance.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise


@extend_schema_view(
    get=extend_schema(
        tags=["Users - Management"],
        operation_id="list_users",
        summary="List all users",
        description="Retrieves a paginated list of all users in the system",
        responses={
            200: ListAllUsersSerializer,
            401: {'description': 'Authentication credentials not provided'}
        }
    )
)
class UserListView(BaseUserView, ListAPIView):
    """
    View for listing all users.
    
    Provides a paginated list of all users with basic information,
    using the simplified ListAllUsersSerializer.
    """
    serializer_class = ListAllUsersSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            logger.info(
                "User list retrieved",
                extra={
                    'requester_id': request.user.id,
                    'count': self.get_queryset().count()
                }
            )
            return response
        except Exception as e:
            logger.error(
                f"Error retrieving user list: {str(e)}",
                extra={'requester_id': request.user.id},
                exc_info=True
            )
            raise