from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login as auth_login
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
from rest_framework import generics
from django.core.cache import cache
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)
from .models import User
from .serializers import UserSerializer, ListAllUsersSerializer, LoginSerializer, PasswordResetConfirmSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login as auth_login
from core.email_handlers import AuthEmailHandler
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from crum import get_current_request, get_current_user

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
            
            # Verify if it is a swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                return User.objects.none()
            # Filter users from the same company
            employeer = user.employeer
            return User.objects.filter(
                employeer__companie=employeer.companie
            ).select_related().prefetch_related('groups', 'user_permissions')
        except:
            return User.objects.none()


@extend_schema_view(
    post=extend_schema(
        tags=["Accounts - Management"],
        operation_id="create_user",
        summary="Create new user account",
        description="""
        Creates a new user account with the provided information.
        
        Required fields:
        - email (used as username for login)
        - password
        - first_name
        - last_name
        - user_type
        
        Password requirements:
        - Minimum 8 characters
        - At least one number
        - At least one lowercase letter
        - At least one uppercase letter
        - At least one special character
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string', 'format': 'password', 'minLength': 8},
                    'first_name': {'type': 'string', 'minLength': 1},
                    'last_name': {'type': 'string', 'minLength': 1},
                    'user_type': {
                        'type': 'string',
                        'description': 'The type of user',
                        'enum': ['Owner', 'Employee', 'Customer', 'Supplier', 'Installer', 'Driver', 'Admin', 'Manager']
                    },
                },
                'required': ['email', 'password', 'first_name', 'last_name', 'user_type']
            }
        },
        examples=[
            OpenApiExample(
                name="Create Owner User",
                value={
                    "email": "owner@example.com",
                    "password": "owner123@",
                    "first_name": "Owner",
                    "last_name": "User",
                    "user_type": "Owner"
                }
            ),
            OpenApiExample(
                name="Create Employee User",
                value={
                    "email": "employee@example.com",
                    "password": "employee123@",
                    "first_name": "Employee",
                    "last_name": "User",
                    "user_type": "Employee"
                }
            ),
            OpenApiExample(
                name="Create Customer User",
                value={
                    "email": "customer@example.com",
                    "password": "customer123@",
                    "first_name": "Customer",
                    "last_name": "User",
                    "user_type": "Customer"
                }
            )
        ],
        responses={
            201: UserSerializer,
            400: {
                'description': 'Invalid input data',
                'type': 'object',
                'properties': {
                    'email': {'type': 'array', 'items': {'type': 'string'}},
                    'password': {'type': 'array', 'items': {'type': 'string'}},
                    'first_name': {'type': 'array', 'items': {'type': 'string'}},
                    'last_name': {'type': 'array', 'items': {'type': 'string'}},
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
            
            # Ensure current request is available
            if not get_current_request():
                from crum import CurrentRequestUserMiddleware
                middleware = CurrentRequestUserMiddleware(get_response=lambda x: None)
                middleware.process_request(self.request)
            
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
        tags=["Accounts - Management"],
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
        tags=["Accounts - Management"],
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
    lookup_field = 'pk'
    
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
        tags=["Accounts - Management"],
        operation_id="update_user",
        summary="Update user profile",
        description="""
        Updates user profile information. All fields are required in a full update.
        
        Required fields:
        - email
        - first_name
        - last_name
        - user_type
        
        Optional:
        - password (if provided, must meet security requirements)
        
        Note: IP address is automatically updated on each request
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
        tags=["Accounts - Management"],
        operation_id="partial_update_user",
        summary="Partially update user profile",
        description="""
        Partially updates user profile information. Only specified fields will be updated.
        
        Updatable fields:
        - email (must be unique)
        - first_name
        - last_name
        - user_type
        - password (if provided, must meet security requirements)
        
        Note: IP address is automatically updated on each request
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
        tags=["Accounts - Management"],
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
        tags=["Accounts - Management"],
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
        
@extend_schema_view(
    post=extend_schema(
        tags=["Accounts - Authentication"],
        operation_id="user_login",
        summary="User login",
        description="""
        Authenticates a user with email and password.
        
        On successful login:
        - Returns authentication token
        - Returns user information
        - Tracks login IP for security
        
        Failed attempts are tracked by Django-Axes for security.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string', 'format': 'password'},
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: {
                'description': 'Login successful',
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'},
                    'name': {'type': 'string'},
                    'redirect_url': {'type': 'string'}
                }
            },
            400: {
                'description': 'Invalid credentials',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    get=extend_schema(
        tags=["Accounts - Authentication"],
        summary="This method for login is for server uses only | Front Developer should ignore it and only use the POST method"
    )
)
@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(generics.GenericAPIView):
    """
    API endpoint for user authentication.
    
    This view handles the login process:
    1. Validates credentials
    2. Authenticates user
    3. Returns authentication token and user data
    4. Provides redirect URL based on permissions
    
    Security Features:
        - CSRF protection enabled
        - Never caches responses
        - Handles sensitive parameters
        - Integrates with Django-Axes for login attempt tracking
        - IP tracking for audit logs
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to ensure CSRF cookie is set.
        
        Returns:
            Response: Empty response with CSRF cookie set
        """
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_success_url(self, user):
        """
        Determine the success URL based on user type and permissions.
        
        Args:
            user: The authenticated user instance
            
        Returns:
            str: URL to redirect to after successful login
            
        Note:
            URLs are checked in order of priority defined in redirect_rules
        """
        redirect_rules = [
            {
                'url': 'inflows:list_inflows',
                'permission': 'inflows.view_inflow',
            },
            {
                'url': 'outflows:list_outflows',
                'permission': 'outflows.view_outflow',
            },
            {
                'url': 'product:list_products',
                'permission': 'product.view_product',
            },
            {
                'url': 'customers:list_customers',
                'permission': 'customers.view_customer',
            },
            {
                'url': 'employeers:list_employeers',
                'permission': 'employeers.view_employeer',
            },
        ]
        
        for rule in redirect_rules:
            if user.has_perm(rule['permission']):
                return reverse_lazy(rule['url'])
        
        for rule in reversed(redirect_rules):
            url_name = rule['url']
            try:
                url = reverse_lazy(url_name)
                if user.has_module_perms(url_name.split(':')[0]):
                    return url
            except:
                continue
        
        return reverse_lazy('profiles:profile_detail')

    def post(self, request, *args, **kwargs):
        """
        Handle login requests.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: JSON response with authentication results
            
        Security:
            Integrates with Django-Axes for login attempt tracking
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            user.get_ip_on_login(request)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'token': str(refresh.access_token),
                'name': user.get_full_name(),
                'redirect_url': str(self.get_success_url(user))
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )



@extend_schema_view(
    post=extend_schema(
        tags=["Accounts - Password Reset"],
        operation_id="password_reset_request",
        summary="Request password reset email",
        description="""
        Initiates the password reset process by sending a reset email.
        
        The email will contain a secure link that allows the user to reset their password.
        The link expires after a configured time period for security.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                },
                'required': ['email']
            }
        },
        responses={
            200: {
                'description': 'Password reset email sent successfully',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Password reset email has been sent'
                    }
                }
            },
            400: {
                'description': 'Invalid email address',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    )
)
@method_decorator(csrf_exempt, name='dispatch')
class CustomPasswordResetView(APIView):
    """
    API endpoint for initiating password reset process.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email, is_active=True)
            context = {
                'email': user.email,
                'domain': request.get_host(),
                'site_name': 'DryWall WareHouse',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
                'reset_url': f"/api/v1/user/reset/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}/"
            }
            
            auth_handler = AuthEmailHandler()
            auth_handler.template_name = 'auth/password_reset_email'  # Corrigido o nome do template
            auth_handler.send_password_reset_email(context, email)
            
            return Response(
                {'detail': 'Password reset email has been sent'},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {'detail': 'Password reset email has been sent'},
                status=status.HTTP_200_OK
            )
            
@extend_schema_view(
    post=extend_schema(
        tags=["Accounts - Password Reset"],
        operation_id="password_reset_confirm",
        summary="Confirm password reset",
        description="Reset user's password using token from email",
        parameters=[
            OpenApiParameter(
                name="uidb64",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="Base64 encoded user ID"
            ),
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Password reset token"
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'password': {'type': 'string', 'format': 'password'},
                    'password_confirm': {'type': 'string', 'format': 'password'}
                },
                'required': ['password', 'password_confirm']
            }
        },
        responses={
            200: {'description': 'Password successfully reset'},
            400: {'description': 'Invalid token or passwords do not match'}
        }
    )
)
@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetConfirmView(APIView):
    """
    API endpoint for confirming password reset.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def get(self, request, uidb64, token, *args, **kwargs):
        """
        Validate token and return status
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                return Response({
                    'status': 'valid',
                    'message': 'Token is valid'
                })
            return Response({
                'status': 'invalid',
                'message': 'Token is invalid or expired'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'status': 'invalid',
                'message': 'Invalid reset link'
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token, *args, **kwargs):
        """
        Reset password if token is valid
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if not default_token_generator.check_token(user, token):
                return Response({
                    'error': 'Token is invalid or expired'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['password'])
            user.save()
            
            return Response({
                'detail': 'Password has been reset successfully'
            }, status=status.HTTP_200_OK)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Invalid reset link'
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        tags=["Accounts - Password Reset"],
        operation_id="password_reset_complete",
        summary="Password reset complete",
        description="Confirm that password reset was successful",
        responses={
            200: {'description': 'Password reset completed'}
        }
    )
)
class PasswordResetCompleteView(APIView):
    """
    API endpoint for password reset completion confirmation.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Password reset completed successfully'},
            status=status.HTTP_200_OK
        )