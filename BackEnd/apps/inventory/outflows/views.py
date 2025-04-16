from django.shortcuts import render
from .models import Outflow
from .serializers import OutflowSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView, GenericAPIView
)
from .services.handlers import OutflowService
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class OutflowBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # Verify if it is a swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                    return OutflowSerializer
            
            employeer = user.employeer
            return Outflow.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except Outflow.DoesNotExist:
            return Outflow.objects.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='list_outflows',
        summary='List all outflows',
        description="""
        Retrieve a list of all outflows for the authenticated user's employeer.
        """,
        responses={
            200: OutflowSerializer,
        }
    )
)
class OutflowListView(OutflowBaseView, ListAPIView):
    serializer_class = OutflowSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[OUTFLOW VIEWS] - Outflows list retrieved successfully")
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='create_outflow',
        summary='Create a new outflow',
        description="""
        Create a new outflow record with the provided information
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
                    'type': {
                        'type': 'string',
                        'example': 'Exit'
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
                'required': ['origin', 'destiny', 'items_data', 'type']
            }
        },
        responses={
            201: OutflowSerializer,
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
class OutflowCreateView(OutflowBaseView, CreateAPIView):
    serializer_class = OutflowSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"[OUTFLOW VIEWS] - Outflow {serializer.data['id']} created successfully")
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
        except Exception as e:
            logger.error(f"[OUTFLOW VIEWS] - Error creating outflow: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='retrieve_outflow',
        summary='Retrieve an outflow',
        description='Get details of a specific outflow by its ID',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the outflow to retrieve',
                required=True
            )
        ],
        responses={
            200: OutflowSerializer,
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
class OutflowRetrieveView(OutflowBaseView, RetrieveAPIView):
    serializer_class = OutflowSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[OUTFLOW VIEWS] - Error retrieving outflow: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='update_outflow',
        summary='Update an outflow',
        description='Update an existing outflow with new information',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the outflow to update',
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
                    'type': {
                        'type': 'string',
                        'example': 'Exit'
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
                'required': ['origin', 'destiny', 'items_data', 'type']
            }
        },
        responses={
            200: OutflowSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Invalid data provided'
                    }
                }
            },
            500: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating outflow'
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='partial_update_outflow',
        summary='Partial update an outflow',
        description='Update an existing outflow with new information. Only the fields provided in the request will be updated.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the outflow to update',
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
                    'type': {
                        'type': 'string',
                        'example': 'Exit'
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
            200: OutflowSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Invalid data provided'
                    }
                }
            },
            500: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating outflow'
                    }
                }
            }
        }
    )
)
class OutflowUpdateView(OutflowBaseView, UpdateAPIView):
    serializer_class = OutflowSerializer
    
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
            logger.error(f"[OUTFLOW VIEWS] - Validation error updating outflow: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[OUTFLOW VIEWS] - Error updating outflow: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='delete_outflow',
        summary='Delete an outflow',
        description='Delete a specific outflow by its ID',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the outflow to delete',
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
class OutflowDestroyView(OutflowBaseView, DestroyAPIView):
    serializer_class = OutflowSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=204)
        except Exception as e:
            logger.error(f"[OUTFLOW VIEWS] - Error deleting outflow: {str(e)}")
            return Response(
                {"detail": "Error deleting outflow"},
                status=500
            )

@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='approve_outflow',
        summary='Approve an outflow',
        description='Approve a pending outflow to update inventory quantities',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the outflow to approve',
                required=True
            )
        ],
        responses={
            200: OutflowSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Only pending outflows can be approved'
                    }
                }
            }
        }
    )
)
class OutflowApproveView(OutflowBaseView, GenericAPIView):
    """View for approving a pending outflow"""
    serializer_class = OutflowSerializer
    
    def post(self, request, *args, **kwargs):
        """Approve an outflow"""
        try:
            outflow = self.get_object()
            
            service = OutflowService()
            approved_outflow = service.approve_outflow(outflow, request.user)
            
            serializer = self.get_serializer(approved_outflow)
            
            logger.info(f"Outflow approved successfully via API", extra={'outflow_id': outflow.id})
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(f"Validation error when approving outflow", extra={'error': str(e)})
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error approving outflow", extra={'error': str(e)}, exc_info=True)
            return Response(
                {'detail': 'An error occurred while approving the outflow'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Outflows'],
        operation_id='reject_outflow',
        summary='Reject an outflow',
        description='Reject a pending outflow with a reason',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the outflow to reject',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'rejection_reason': {
                        'type': 'string',
                        'description': 'Reason for rejecting the outflow',
                        'example': 'Products not available in the requested quantities'
                    }
                },
                'required': ['rejection_reason']
            }
        },
        responses={
            200: OutflowSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'A valid rejection reason is required'
                    }
                }
            }
        }
    )
)
class OutflowRejectView(OutflowBaseView, GenericAPIView):
    """View for rejecting a pending outflow"""
    serializer_class = OutflowSerializer
    
    def post(self, request, *args, **kwargs):
        """Reject an outflow"""
        try:
            outflow = self.get_object()
            
            # Get rejection reason from request data
            rejection_reason = request.data.get('rejection_reason')
            if not rejection_reason:
                return Response(
                    {'detail': 'Rejection reason is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            service = OutflowService()
            rejected_outflow = service.reject_outflow(outflow, request.user, rejection_reason)
            
            serializer = self.get_serializer(rejected_outflow)
            
            logger.info(f"Outflow rejected successfully via API", extra={'outflow_id': outflow.id})
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(f"Validation error when rejecting outflow", extra={'error': str(e)})
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error rejecting outflow", extra={'error': str(e)}, exc_info=True)
            return Response(
                {'detail': 'An error occurred while rejecting the outflow'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )