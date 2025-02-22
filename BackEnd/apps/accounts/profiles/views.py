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
from rest_framework.exceptions import ValidationError
from .models import Profile
from .serializers import (
    ProfileBasicSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    ProfileAvatarSerializer
)
import logging

logger = logging.getLogger(__name__)

class ProfileBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employeer = user.employeer
            return Profile.objects.select_related(
                'user', 'employeer'
            ).filter(employeer__companie=employeer.companie)
        except Profile.DoesNotExist:
            return Profile.objects.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='list_profiles',
        summary='List all profiles',
        description='Retrieves a list of all profiles for the authenticated user\'s company.',
        responses={
            200: ProfileBasicSerializer,
        }
    )
)
class ProfileListView(ProfileBaseView, ListAPIView):
    serializer_class = ProfileBasicSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[PROFILE VIEWS] - Profiles list retrieved successfully")
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='create_profile',
        summary='Create a new profile',
        description='Creates a new profile with the specified information.',
        request=ProfileUpdateSerializer,
        responses={
            201: ProfileDetailSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error creating profile'
                    }
                }
            }
        }
    )
)
class ProfileCreateView(ProfileBaseView, CreateAPIView):
    serializer_class = ProfileUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"[PROFILE VIEWS] - Profile created successfully")
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error creating profile: {str(e)}")
            return Response(
                {"detail": "Error creating profile"},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='retrieve_profile',
        summary='Retrieve a profile',
        description='Retrieves a profile with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the profile to retrieve',
                required=True
            )
        ],
        responses={
            200: ProfileDetailSerializer,
            404: {
                'description': 'Profile not found',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Profile not found'
                    }
                }
            }
        }
    )
)
class ProfileRetrieveView(ProfileBaseView, RetrieveAPIView):
    serializer_class = ProfileDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[PROFILE VIEWS] - Profile {kwargs.get('pk')} retrieved successfully")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error retrieving profile: {str(e)}")
            return Response(
                {"detail": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='update_profile',
        summary='Update a profile',
        description='Updates a profile with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the profile to update',
                required=True
            )
        ],
        request=ProfileUpdateSerializer,
        responses={
            200: ProfileDetailSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating profile'
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='partial_update_profile',
        summary='Partially update a profile',
        description='Partially updates a profile with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the profile to update',
                required=True
            )
        ],
        request=ProfileUpdateSerializer,
        responses={
            200: ProfileDetailSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating profile'
                    }
                }
            }
        }
    )
)
class ProfileUpdateView(ProfileBaseView, UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                serializer = self.get_serializer(
                    instance,
                    data=request.data,
                    partial=False
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                logger.info(f"[PROFILE VIEWS] - Profile {kwargs.get('pk')} updated successfully")
                return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"[PROFILE VIEWS] - Validation error updating profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error updating profile: {str(e)}")
            return Response(
                {"detail": "Error updating profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                serializer = self.get_serializer(
                    instance,
                    data=request.data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                logger.info(f"[PROFILE VIEWS] - Profile {kwargs.get('pk')} partially updated successfully")
                return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"[PROFILE VIEWS] - Validation error updating profile: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error updating profile: {str(e)}")
            return Response(
                {"detail": "Error updating profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    delete=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='delete_profile',
        summary='Delete a profile',
        description='Deletes a profile with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the profile to delete',
                required=True
            )
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Profile deleted successfully'
                    }
                }
            }
        }
    )
)
class ProfileDestroyView(ProfileBaseView, DestroyAPIView):
    serializer_class = ProfileDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            logger.info(f"[PROFILE VIEWS] - Profile {kwargs.get('pk')} deleted successfully")
            return Response(
                {"detail": "Profile deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error deleting profile: {str(e)}")
            return Response(
                {"detail": "Error deleting profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Accounts - Profiles'],
        operation_id='update_profile_avatar',
        summary='Update profile avatar',
        description='Updates the avatar of a profile with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the profile to update avatar',
                required=True
            )
        ],
        request=ProfileAvatarSerializer,
        responses={
            200: ProfileAvatarSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating avatar'
                    }
                }
            }
        }
    )
)
class ProfileAvatarUpdateView(ProfileBaseView, UpdateAPIView):
    serializer_class = ProfileAvatarSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f"[PROFILE VIEWS] - Avatar updated successfully for profile {kwargs.get('pk')}")
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"[PROFILE VIEWS] - Validation error updating avatar: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[PROFILE VIEWS] - Error updating avatar: {str(e)}")
            return Response(
                {"detail": "Error updating avatar"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )