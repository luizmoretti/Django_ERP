from django.shortcuts import render
from django.core.exceptions import ValidationError

from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView
)

from .models import Companie

from .serializers import CompanieSerializer

import logging

logger = logging.getLogger(__name__)

class CompaniesBaseView:
    """Base class for all companie views with common functionality."""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns a queryset filtered based on user's role and permissions.
                
        
        Returns:
            QuerySet: Filtered Companie queryset based on user permissions
        """
        user = self.request.user
        try:
            # Check for swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                return Companie.objects.none()                 
        
        except Exception as e:
            logger.error(f"[COMPANIE VIEWS] - Error getting queryset: {str(e)}")
            return Companie.objects.none()
        
    
@extend_schema_view(
    get=extend_schema(
        tags=['Companie'],
        operation_id='list_companie',
        summary='List all companies',
        description='Returns a list of all companies for the authenticated user.',
        responses={
            200: CompanieSerializer(many=True),
        }
    )
)
class CompanieListView(CompaniesBaseView, ListAPIView):
    """View for listing all deliveries based on user permissions."""
    serializer_class = CompanieSerializer
    ordering = ['-created_at']
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().order_by('-created_at')
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"[COMPANIE VIEWS] - List of {len(serializer.data)} companies successfully retrieved for user {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[COMPANIE VIEWS] - Error listing companies: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
@extend_schema_view(
    post=extend_schema(
        tags=['Companie'],
        operation_id='create_companie',
        summary='Create a new companie',
        description='Creates a new companie with the specified parameters.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Name of the company'
                    },
                    'type': {
                        'type': 'string',
                        'description': 'Type of the company',
                        'enum': ['Headquarters', 'Subsidiary']
                    },
                    'address': {
                        'type': 'string',
                        'description': 'Address of the company'
                    },
                    'state': {
                        'type': 'string',
                        'description': 'State of the company'
                    },
                    'city': {
                        'type': 'string',
                        'description': 'City of the company'
                    },
                    'zip_code': {
                        'type': 'string',
                        'description': 'Zip code of the company'
                    },
                    'country': {
                        'type': 'string',
                        'description': 'Country of the company',
                    },
                    'phone': {
                        'type': 'string',
                        'description': 'Phone number of the company'
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'Email of the company'
                    }                                         
                },
                'required': ['name', 'type', 'address', 'state', 'city', 'zip_code', 'country', 'phone', 'email'],
            }
        },
        responses={
            201: CompanieSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error creating companie'
                    }
                }
            }
        }
    )
)
class CompanieCreateView(CompaniesBaseView, CreateAPIView):
    """View for creating a new delivery."""
    serializer_class = CompanieSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            # Create delivery using the handler
            companie = CompanieHandler.create_companie(request.data, request.user)
            
            # Serialize result
            serializer = self.get_serializer(companie)
            headers = self.get_success_headers(serializer.data)
            
            logger.info(f"[COMPANIE VIEWS] - Companie {companie.id} successfully created by {request.user.username}")
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except ValidationError as e:
            logger.warning(f"[COMPANIE VIEWS] - Validation error when creating companie: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[COMPANIE VIEWS] - Error creating companie: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

