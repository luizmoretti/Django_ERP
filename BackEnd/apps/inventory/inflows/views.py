from django.shortcuts import render
from .models import Inflow
from .serializers import InflowSerializer
from .services.handlers import InflowService
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
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
import logging
from .permissions import InflowBasePermission, CanApproveInflow, CanRejectInflow

logger = logging.getLogger(__name__)


class InflowBaseView:
    permission_classes = [IsAuthenticated, InflowBasePermission]
    
    def get_queryset(self):
        user = self.request.user
        try:
            if getattr(self, 'swagger_fake_view', False):
                return InflowSerializer
            else:
                employeer = user.employeer
                queryset = Inflow.objects.select_related(
                    'companie'
                ).filter(companie=employeer.companie)
            return queryset
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
                    'type': {
                        'type': 'string',
                        'example': 'Entry'
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
                    'type': {
                        'type': 'string',
                        'example': 'Entry'
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
                    'type': {
                        'type': 'string',
                        'example': 'Entry'
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
            return Response(serializer.data, status=200)
        except ValidationError as e:
            logger.error(f"[INFLOW VIEW] Validation error updating inflow: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=400
            )
        except Exception as e:
            logger.error(f"[INFLOW VIEW] Error updating inflow: {str(e)}")
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
            logger.error(f"[INFLOW VIEW] Error deleting inflow: {str(e)}")
            return Response(
                {"detail": "Error deleting inflow"},
                status=500
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='approve_inflow',
        summary='Approve an inflow',
        description='Approve a pending inflow to update inventory quantities',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the inflow to approve',
                required=True
        )
    ],
    responses={
        200: InflowSerializer,
        400: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Only pending inflows can be approved'
                }
            }
        },
        403: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'You do not have permission to approve inflows'
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
)
class InflowApproveView(InflowBaseView, GenericAPIView):
    """
    View for approving a pending inflow
    
    This view allows users with appropriate permissions to approve
    a pending inflow, which will update inventory quantities.
    """
    permission_classes = [IsAuthenticated, CanApproveInflow]
    serializer_class = InflowSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Approve an inflow
        
        Args:
            request: HTTP request
            *args, **kwargs: Additional arguments
            
        Returns:
            Response: HTTP response with approved inflow data
        """
        try:
            # Get inflow instance
            inflow = self.get_object()
            
            # Create service instance
            service = InflowService()
            
            # Approve inflow
            approved_inflow = service.approve_inflow(inflow)
            
            # Serialize and return
            serializer = self.get_serializer(approved_inflow)
            
            logger.info(
                f"[INFLOW VIEW] Inflow approved successfully via API",
                extra={
                    'inflow_id': inflow.id
                }
            )
            
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(
                f"[INFLOW VIEW] Validation error when approving inflow",
                extra={
                    'inflow_id': kwargs.get('pk'),
                    'user_id': request.user.id,
                    'error': str(e)
                }
            )
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(
                f"[INFLOW VIEW] Error approving inflow",
                extra={
                    'inflow_id': kwargs.get('pk'),
                    'user_id': request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except PermissionDenied as e:
            logger.warning(
                f"[INFLOW VIEW] Permission denied when approving inflow",
                extra={
                    'inflow_id': kwargs.get('pk'),
                    'user_id': request.user.id,
                    'error': str(e)
                }
            )
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Inflows'],
        operation_id='reject_inflow',
        summary='Reject an inflow',
        description='Reject a pending inflow with a reason',
        parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='UUID of the inflow to reject',
            required=True
        )
    ],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'rejection_reason': {
                    'type': 'string',
                    'description': 'Reason for rejecting the inflow',
                    'example': 'Products not matching order specifications'
                }
            },
            'required': ['rejection_reason']
        }
    },
    responses={
        200: InflowSerializer,
        400: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'A valid rejection reason is required'
                }
            }
        },
        403: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'You do not have permission to reject inflows'
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
)
class InflowRejectView(InflowBaseView, GenericAPIView):
    """
    View for rejecting a pending inflow
    
    This view allows users with appropriate permissions to reject
    a pending inflow with a reason.
    """
    permission_classes = [IsAuthenticated, CanRejectInflow]
    serializer_class = InflowSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Reject an inflow
        
        Args:
            request: HTTP request with rejection reason
            *args, **kwargs: Additional arguments
            
        Returns:
            Response: HTTP response with rejected inflow data
        """
        try:
            # Get inflow instance
            inflow = self.get_object()
            
            # Get rejection reason from request data
            rejection_reason = request.data.get('rejection_reason')
            if not rejection_reason:
                return Response(
                    {'detail': 'Rejection reason is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create service instance
            service = InflowService()
            
            # Reject inflow
            rejected_inflow = service.reject_inflow(inflow, rejection_reason)
            
            # Serialize and return
            serializer = self.get_serializer(rejected_inflow)
            
            logger.info(
                f"[INFLOW VIEW] Inflow rejected successfully via API",
                extra={
                    'inflow_id': inflow.id,
                    'reason': rejection_reason
                }
            )
            
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(
                f"[INFLOW VIEW] Validation error when rejecting inflow",
                extra={
                    'inflow_id': kwargs.get('pk'),
                    'error': str(e)
                }
            )
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(
                f"[INFLOW VIEW] Error rejecting inflow",
                extra={
                    'inflow_id': kwargs.get('pk'),
                    'error': str(e)
                },
                exc_info=True
            )
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except PermissionDenied as e:
            logger.warning(
                f"[INFLOW VIEW] Permission denied when rejecting inflow",
                extra={
                    'inflow_id': kwargs.get('pk'),
                    'error': str(e)
                }
            )
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
