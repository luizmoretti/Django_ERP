"""Profile views"""
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from .services.filters import ProfileFilter, CustomPagination
from .services.handlers import ProfileService
import django_filters.rest_framework as filters
from .models import Profile
from .serializers import (
    ProfileBasicSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    ProfileAvatarSerializer
)
from apps.companies.employeers.models import Employeer
import logging

logger = logging.getLogger(__name__)

class ProfileBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        try:
            # Check specific permission for each operation type
            if self.request.method == 'GET':
                if not (user.has_perm('profiles.view_profile') or user.has_perm('profiles.view_own_profile')):
                    raise PermissionDenied('You do not have permission to view profiles')
            elif self.request.method in ['POST', 'PUT', 'PATCH']:
                if not (user.has_perm('profiles.change_profile') or user.has_perm('profiles.change_own_profile')):
                    raise PermissionDenied('You do not have permission to modify profiles')
            elif self.request.method == 'DELETE':
                if not user.has_perm('profiles.delete_profile'):
                    raise PermissionDenied('You do not have permission to delete profiles')
            
            # Get the employeer for the user
            employeer = Employeer.objects.get(user=user)
            
            # Base queryset filtered by company
            queryset = Profile.objects.select_related('user', 'companie').filter(companie=employeer.companie)
            
            # If user only has permission to see own profile, filter further
            if not user.has_perm('profiles.view_profile') and user.has_perm('profiles.view_own_profile'):
                queryset = queryset.filter(user=user)
                
            return queryset
            
        except Employeer.DoesNotExist:
            raise ValidationError('User is not associated with any company')
            
@extend_schema_view(
    get=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='list_profiles',
        summary='List all profiles',
        description='Retrieves a list of all profiles for the authenticated user\'s company.',
        responses={200: ProfileBasicSerializer}
    )
)
class ProfileListView(ProfileBaseView, ListAPIView):
    serializer_class = ProfileBasicSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProfileFilter
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        
        # Explicitly checks permission for the list view
        # If the user only has permission to view their own profile,
        # but not all profiles, denies access
        if not user.has_perm('profiles.view_profile') and user.has_perm('profiles.view_own_profile'):
            # Use PermissionDenied instead of ValidationError to get a 403 instead of a 400
            raise PermissionDenied('You do not have permission to view all profiles')
        
        return super().get_queryset()
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            logger.info(f"[PROFILE VIEWS] - Profiles list retrieved successfully")
            return self.get_paginated_response(serializer.data)
        except PermissionDenied as e:
            # Propagate PermissionDenied exception without converting it
            logger.warning(f"[PROFILE VIEWS] - Permission denied: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error retrieving profiles list: {str(e)}")
            raise ValidationError(detail=str(e))


@extend_schema_view(
    get=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='retrieve_profile',
        summary='Retrieve a profile',
        description='Retrieves detailed information about a specific profile.',
        responses={200: ProfileDetailSerializer}
    )
)
class ProfileDetailView(ProfileBaseView, RetrieveAPIView):
    serializer_class = ProfileDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = ProfileService.get_profile_detail(kwargs['pk'])
            serializer = self.get_serializer(instance)
            logger.info(f"[PROFILE VIEWS] - Profile {instance.id} retrieved successfully")
            return Response(serializer.data)
        except Profile.DoesNotExist:
            logger.error(f"[PROFILE VIEWS] - Profile {kwargs['pk']} not found")
            return Response(
                {"detail": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error retrieving profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='create_profile',
        summary='Create a new profile',
        description='Creates a new profile with the specified information.',
        request=ProfileUpdateSerializer,
        responses={201: ProfileDetailSerializer}
    )
)
class ProfileCreateView(ProfileBaseView, CreateAPIView):
    serializer_class = ProfileUpdateSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                response_serializer = ProfileDetailSerializer(instance)
                logger.info(f"[PROFILE VIEWS] - Profile {instance.id} created successfully")
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error creating profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='update_profile',
        summary='Update a profile',
        description='Updates an existing profile with new information.',
        request=ProfileUpdateSerializer,
        responses={200: ProfileDetailSerializer}
    ),
    patch=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='partial_update_profile',
        summary='Partially update a profile',
        description='Partially updates an existing profile.',
        request=ProfileUpdateSerializer,
        responses={200: ProfileDetailSerializer}
    )
)
class ProfileUpdateView(ProfileBaseView, UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = ProfileService.update_profile(
                    kwargs['pk'],
                    request.data,
                    request.user
                )
                serializer = ProfileDetailSerializer(instance)
                logger.info(f"[PROFILE VIEWS] - Profile {instance.id} updated successfully")
                return Response(serializer.data)
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error updating profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


@extend_schema_view(
    delete=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='delete_profile',
        summary='Delete a profile',
        description='Soft deletes a profile by marking it as inactive.',
        responses={204: None}
    )
)
class ProfileDeleteView(ProfileBaseView, DestroyAPIView):
    serializer_class = ProfileDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = ProfileService.delete_profile(
                kwargs['pk'],
                request.user
            )
            logger.info(f"[PROFILE VIEWS] - Profile {instance.id} deleted successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error deleting profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='update_profile_avatar',
        summary='Update profile avatar',
        description='Updates the avatar image of a profile.',
        request=ProfileAvatarSerializer,
        responses={200: ProfileAvatarSerializer}
    )
)
class ProfileAvatarView(ProfileBaseView, UpdateAPIView):
    serializer_class = ProfileAvatarSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def update(self, request, *args, **kwargs):
        try:
            instance = ProfileService.handle_avatar_upload(
                kwargs['pk'],
                request.FILES.get('avatar'),
                request.user
            )
            serializer = self.get_serializer(instance)
            logger.info(f"[PROFILE VIEWS] - Avatar updated for profile {instance.id}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error updating avatar: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )