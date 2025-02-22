from django.shortcuts import render
from .models import Inflow
from .serializers import InflowSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError
import logging
from .permissions import InflowBasePermission

logger = logging.getLogger(__name__)


class InflowBaseView:
    permission_classes = [IsAuthenticated, InflowBasePermission]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employeer = user.employeer
            return Inflow.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except Inflow.DoesNotExist:
            return Inflow.objects.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='list_inflows',
        summary='List all inflows',
        description="""
        Retrieve a list of all inflows for the authenticated user's employeer.
        """,
        responses={
            200: InflowSerializer,
        }
    )
)
class InflowListView(InflowBaseView, ListAPIView):
    serializer_class = InflowSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[INFLOW VIEWS] - Inflows list retrieved successfully")
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='create_inflow',
        summary='Create a new inflow',
        description="""
        Create a new inflow record with the provided information
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'origin': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'destiny': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'items_data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {   
                                'product': {
                                    'type': 'string',
                                    'format': 'uuid'
                                },
                                'quantity': {
                                    'type': 'integer'
                                }
                            },
                            'required': ['product', 'quantity']
                        }
                    }
                },
                'required': ['origin', 'destiny', 'items_data']
            }
        },
        responses={
            201: InflowSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Invalid data provided'
                    }
                }
            }
        }
    )
)
class InflowCreateView(InflowBaseView, CreateAPIView):
    serializer_class = InflowSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"[INFLOW VIEWS] - Inflow {serializer.data['id']} created successfully")
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
        except Exception as e:
            logger.error(f"[INFLOW VIEWS] - Error creating inflow: {str(e)}")
            return Response(
                {"detail": "Error creating inflow"},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='retrieve_inflow',
        summary='Retrieve an inflow',
        description='Get details of a specific inflow by its ID',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the inflow to retrieve',
                required=True
            )
        ],
        responses={
            200: InflowSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Not found.'
                    }
                }
            }
        }
    )
)
class InflowRetrieveView(InflowBaseView, RetrieveAPIView):
    serializer_class = InflowSerializer
        
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[INFLOW VIEWS] - Error retrieving inflow: {str(e)}")
            return Response(
                {"detail": "Error retrieving inflow"},
                status=500
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='update_inflow',
        summary='Update an inflow',
        description='Update an existing inflow with new information',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the inflow to update',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'origin': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'destiny': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'items_data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {   
                                'product': {
                                    'type': 'string',
                                    'format': 'uuid'
                                },
                                'quantity': {
                                    'type': 'integer'
                                }
                            },
                            'required': ['product', 'quantity']
                        }
                    }
                },
                'required': ['origin', 'destiny', 'items_data']
            }
        },
        responses={
            200: InflowSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Invalid data provided'
                    }
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Not found.'
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='partial_update_inflow',
        summary='Partial update an inflow',
        description='Update an existing inflow with new information. Only the fields provided in the request will be updated.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the inflow to update',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'origin': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'destiny': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'items_data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {   
                                'product': {
                                    'type': 'string',
                                    'format': 'uuid'
                                },
                                'quantity': {
                                    'type': 'integer'
                                }
                            }
                        }
                    }
                }
            }
        },
        responses={
            200: InflowSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Invalid data provided'
                    }
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Not found.'
                    }
                }
            }
        }
    )
)
class InflowUpdateView(InflowBaseView, UpdateAPIView):
    serializer_class = InflowSerializer
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=False
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"[INFLOW VIEWS] - Validation error updating inflow: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=400
            )
        except Exception as e:
            logger.error(f"[INFLOW VIEWS] - Error updating inflow: {str(e)}")
            return Response(
                {"detail": "Error updating inflow"},
                status=500
            )


@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='delete_inflow',
        summary='Delete an inflow',
        description='Delete a specific inflow by its ID',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the inflow to delete',
                required=True
            )
        ],
        responses={
            204: None,
            404: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Not found.'
                    }
                }
            }
        }
    )
)
class InflowDestroyView(InflowBaseView, DestroyAPIView):
    serializer_class = InflowSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=204)
        except Exception as e:
            logger.error(f"[INFLOW VIEWS] - Error deleting inflow: {str(e)}")
            return Response(
                {"detail": "Error deleting inflow"},
                status=500
            )
