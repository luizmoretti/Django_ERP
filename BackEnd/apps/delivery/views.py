from django.shortcuts import render
from .serializers import DeliverySerializer, DeliveryCheckpointSerializer
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
from .models import Delivery, DeliveryCheckpoint
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import viewsets
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import json
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .services.validators import DeliveryValidator
from .services.handlers import DeliveryHandler
from .tasks.handlers import notify_delivery_status_change, generate_delivery_report
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from core.constants.choices import DELIVERY_STATUS_CHOICES, USER_TYPE_CHOICES

logger = logging.getLogger(__name__)

class DeliveryBaseView:
    """Base class for all delivery views with common functionality."""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns a queryset filtered based on user's role and permissions.
        
        - Managers can see all deliveries for their company
        - Drivers can only see deliveries assigned to them
        - Customers can only see their own deliveries
        - Other users can't see any deliveries
        
        Returns:
            QuerySet: Filtered Delivery queryset based on user permissions
        """
        user = self.request.user
        try:
            # Check for swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                return Delivery.objects.none()
            
            # If user is manager, show all company deliveries
            if user.user_type == 'Manager':
                return Delivery.objects.select_related(
                    'customer', 'driver', 'vehicle', 'companie'
                ).prefetch_related(
                    'load', 'checkpoints'
                ).filter(companie=user.companie)
            
            # If user is driver, show only their deliveries
            elif hasattr(user, 'employeer') and user.user_type == 'Driver':
                return Delivery.objects.select_related(
                    'customer', 'driver', 'vehicle', 'companie'
                ).prefetch_related(
                    'load', 'checkpoints'
                ).filter(companie=user.companie, driver=user.employeer)
            
            # If user is customer, show only their deliveries
            elif hasattr(user, 'customer'):
                return Delivery.objects.select_related(
                    'customer', 'driver', 'vehicle', 'companie'
                ).prefetch_related(
                    'load', 'checkpoints'
                ).filter(customer=user.customer)
            
            # Otherwise, show nothing
            else:
                return Delivery.objects.none()
            
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error getting queryset: {str(e)}")
            return Delivery.objects.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Delivery'],
        operation_id='list_deliveries',
        summary='List all deliveries',
        description='Returns a list of all deliveries for the authenticated user.',
        responses={
            200: DeliverySerializer(many=True),
        }
    )
)
class DeliveryListView(DeliveryBaseView, ListAPIView):
    """View for listing all deliveries based on user permissions."""
    serializer_class = DeliverySerializer
    ordering = ['-created_at']
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().order_by('-created_at')
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"[DELIVERY VIEWS] - List of {len(serializer.data)} deliveries successfully retrieved for user {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error listing deliveries: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Delivery'],
        operation_id='create_delivery',
        summary='Create a new delivery',
        description='Creates a new delivery with the specified parameters.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'customer': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the customer for the delivery'
                    },
                    'driver': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the driver assigned to the delivery'
                    },
                    'vehicle': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the vehicle assigned to the delivery'
                    },
                    'load': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the load order to be delivered'
                    },
                    'estimated_departure': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'The estimated time the delivery will depart'
                    },
                    'estimated_arrival': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'The estimated time the delivery will arrive at its destination'
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Additional notes about the delivery'
                    }
                },
                'required': ['customer', 'driver', 'vehicle', 'load']
            }
        },
        responses={
            201: DeliverySerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error creating delivery'
                    }
                }
            }
        }
    )
)
class DeliveryCreateView(DeliveryBaseView, CreateAPIView):
    """View for creating a new delivery."""
    serializer_class = DeliverySerializer
    
    def create(self, request, *args, **kwargs):
        try:
            # Create delivery using the handler
            delivery = DeliveryHandler.create_delivery(request.data, request.user)
            
            # Serialize result
            serializer = self.get_serializer(delivery)
            headers = self.get_success_headers(serializer.data)
            
            logger.info(f"[DELIVERY VIEWS] - Delivery {delivery.id} successfully created by {request.user.username}")
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except ValidationError as e:
            logger.warning(f"[DELIVERY VIEWS] - Validation error when creating delivery: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error creating delivery: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Delivery'],
        operation_id='retrieve_delivery',
        summary='Retrieve delivery details',
        description='Retrieves the details of a specific delivery.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='ID of the delivery to retrieve',
                required=True
            )
        ],
        responses={
            200: DeliverySerializer,
            404: {
                'description': 'Delivery not found',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Delivery not found'
                    }
                }
            }
        }
    )
)
class DeliveryRetrieveView(DeliveryBaseView, RetrieveAPIView):
    """View for retrieving details of a delivery."""
    serializer_class = DeliverySerializer
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[DELIVERY VIEWS] - Delivery {instance.id} successfully retrieved by {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error retrieving delivery: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Delivery'],
        operation_id='update_delivery',
        summary='Update a delivery',
        description='Completely updates a delivery with the specified parameters.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='ID of the delivery to update',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'customer': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the customer for the delivery'
                    },
                    'driver': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the driver assigned to the delivery'
                    },
                    'vehicle': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the vehicle assigned to the delivery'
                    },
                    'load': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the load order to be delivered'
                    },
                    'status': {
                        'type': 'string',
                        'enum': [status[0] for status in DELIVERY_STATUS_CHOICES],
                        'description': 'The current status of the delivery'
                    },
                    'estimated_departure': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'The estimated time the delivery will depart'
                    },
                    'estimated_arrival': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'The estimated time the delivery will arrive at its destination'
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Additional notes about the delivery'
                    }
                }
            }
        },
        responses={
            200: DeliverySerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating delivery'
                    }
                }
            },
            404: {
                'description': 'Delivery not found',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Delivery not found'
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=['Delivery'],
        operation_id='partial_update_delivery',
        summary='Partially update a delivery',
        description='Partially updates a delivery with the specified parameters.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='ID of the delivery to update',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'customer': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the customer for the delivery'
                    },
                    'driver': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the driver assigned to the delivery'
                    },
                    'vehicle': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the vehicle assigned to the delivery'
                    },
                    'load': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the load order to be delivered'
                    },
                    'status': {
                        'type': 'string',
                        'enum': [status[0] for status in DELIVERY_STATUS_CHOICES],
                        'description': 'The current status of the delivery'
                    },
                    'estimated_departure': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'The estimated time the delivery will depart'
                    },
                    'estimated_arrival': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'The estimated time the delivery will arrive at its destination'
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Additional notes about the delivery'
                    }
                }
            }
        },
        responses={
            200: DeliverySerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating delivery'
                    }
                }
            },
            404: {
                'description': 'Delivery not found',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Delivery not found'
                    }
                }
            }
        }
    )
)
class DeliveryUpdateView(DeliveryBaseView, UpdateAPIView):
    """View for updating a delivery."""
    serializer_class = DeliverySerializer
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check if user can edit the delivery
            if not request.user.user_type == 'Manager' and not (hasattr(request.user, 'employeer') and request.user.employeer == instance.driver):
                return Response(
                    {"detail": _("You don't have permission to update this delivery")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check previous status
            old_status = instance.status
                
            # Update delivery using the handler
            updated_delivery = DeliveryHandler.update_delivery(instance, request.data, request.user)
            
            # Check if status changed
            if 'status' in request.data and old_status != updated_delivery.status:
                # Trigger background notification task
                notify_delivery_status_change.delay(
                    str(updated_delivery.id), old_status, updated_delivery.status
                )
            
            # Serialize result
            serializer = self.get_serializer(updated_delivery)
            
            logger.info(f"[DELIVERY VIEWS] - Delivery {updated_delivery.id} updated by {request.user.username}")
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(f"[DELIVERY VIEWS] - Validation error when updating delivery: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error updating delivery: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, *args, **kwargs):
        # Use the same method for partial updates
        return self.update(request, *args, **kwargs)


@extend_schema_view(
    delete=extend_schema(
        tags=['Delivery'],
        operation_id='delete_delivery',
        summary='Delete a delivery',
        description='Removes a delivery from the system.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='ID of the delivery to delete',
                required=True
            )
        ],
        responses={
            204: None,
            404: {
                'description': 'Delivery not found',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Delivery not found'
                    }
                }
            }
        }
    )
)
class DeliveryDestroyView(DeliveryBaseView, DestroyAPIView):
    """View for deleting a delivery."""
    serializer_class = DeliverySerializer
    lookup_field = 'pk'
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check if user can delete the delivery (managers only)
            if not request.user.user_type == 'Manager':
                return Response(
                    {"detail": _("You don't have permission to delete this delivery")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete delivery using the handler
            DeliveryHandler.delete_delivery(instance)
            
            logger.info(f"[DELIVERY VIEWS] - Delivery {instance.id} deleted by {request.user.username}")
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error deleting delivery: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Delivery'],
    operation_id='update_delivery_location',
    summary='Update delivery location',
    description='Updates the current location of a delivery in transit.',
    parameters=[
        OpenApiParameter(
            name='id',
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.UUID,
            description='Delivery ID',
            required=True
        )
    ],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'latitude': {
                    'type': 'number',
                    'format': 'float',
                    'description': 'The latitude coordinate of the current delivery location'
                },
                'longitude': {
                    'type': 'number',
                    'format': 'float',
                    'description': 'The longitude coordinate of the current delivery location'
                },
                'estimated_arrival': {
                    'type': 'string',
                    'format': 'date-time',
                    'description': 'The estimated date and time when the delivery will arrive at its destination'
                },
                'create_checkpoint': {
                    'type': 'boolean',
                    'description': 'Whether to create a checkpoint record for this location update'
                },
                'notes': {
                    'type': 'string',
                    'description': 'Additional notes or information about this location update'
                }
            },
            'required': ['latitude', 'longitude']
        }
    },
    responses={
        200: DeliverySerializer,
        400: {
            'description': 'Invalid data',
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Error updating location'
                }
            }
        },
        404: {
            'description': 'Delivery not found',
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Delivery not found'
                }
            }
        }
    }
)
class DeliveryLocationUpdateView(DeliveryBaseView, APIView):
    """View for updating a delivery's location."""
    
    @transaction.atomic
    def post(self, request, pk):
        try:
            # Get object from filtered queryset
            queryset = Delivery.objects.filter(id=pk)
            if request.user.user_type == 'Manager':
                delivery = get_object_or_404(queryset.filter(companie=request.user.companie))
            elif hasattr(request.user, 'employeer') and request.user.user_type == 'Driver':
                delivery = get_object_or_404(queryset.filter(driver=request.user.employeer))
            else:
                return Response(
                    {"detail": _("You don't have permission to update the location of this delivery")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update location using the handler
            updated_delivery = DeliveryHandler.update_delivery_location(delivery, request.data, request.user)
            
            # Serialize result
            serializer = DeliverySerializer(updated_delivery)
            
            logger.info(f"[DELIVERY VIEWS] - Location of delivery {delivery.id} updated by {request.user.username}")
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(f"[DELIVERY VIEWS] - Validation error when updating location: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error updating location of delivery {pk}: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Delivery'],
    operation_id='update_delivery_status',
    summary='Update delivery status',
    description='Updates the current status of a delivery.',
    parameters=[
        OpenApiParameter(
            name='id',
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.UUID,
            description='Delivery ID',
            required=True
        )
    ],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'enum': [status[0] for status in DELIVERY_STATUS_CHOICES],
                    'description': 'The new status to set for the delivery'
                },
                'notes': {
                    'type': 'string',
                    'description': 'Additional notes about the status change'
                }
            },
            'required': ['status']
        }
    },
    responses={
        200: DeliverySerializer,
        400: {
            'description': 'Invalid data',
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Error updating status'
                }
            }
        },
        404: {
            'description': 'Delivery not found',
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Delivery not found'
                }
            }
        }
    }
)
class DeliveryStatusUpdateView(DeliveryBaseView, APIView):
    """View for updating the status of a delivery."""
    
    @transaction.atomic
    def post(self, request, pk):
        try:
            # Get object from filtered queryset
            queryset = Delivery.objects.filter(id=pk)
            if request.user.user_type == 'Manager':
                delivery = get_object_or_404(queryset.filter(companie=request.user.companie))
            elif hasattr(request.user, 'employeer') and request.user.user_type == 'Driver':
                delivery = get_object_or_404(queryset.filter(driver=request.user.employeer))
            else:
                return Response(
                    {"detail": _("You don't have permission to update the status of this delivery")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate new status
            if 'status' not in request.data:
                return Response(
                    {"detail": _("The status is required")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            old_status = delivery.status
            new_status = request.data['status']
            
            # Validate status transition
            DeliveryValidator.validate_status_change(delivery, new_status)
            
            # Prepare data for the handler
            data = {
                'status': new_status,
                'notes': request.data.get('notes', f"Status altered from {old_status} to {new_status}")
            }
            
            # Update delivery using the handler
            updated_delivery = DeliveryHandler.update_delivery(delivery, data, request.user)
            
            # Trigger background notification task
            notify_delivery_status_change.delay(
                str(updated_delivery.id), old_status, new_status
            )
            
            # If the status is 'delivered', generate report
            if new_status == 'delivered':
                generate_delivery_report.delay(str(updated_delivery.id))
            
            # Serialize result
            serializer = DeliverySerializer(updated_delivery)
            
            logger.info(f"[DELIVERY VIEWS] - Status of delivery {delivery.id} updated from {old_status} to {new_status} by {request.user.username}")
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(f"[DELIVERY VIEWS] - Validation error when updating status: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error updating delivery status {pk}: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Delivery'],
    operation_id='list_delivery_checkpoints',
    summary='List delivery checkpoints',
    description='Returns all checkpoints of a specific delivery.',
    parameters=[
        OpenApiParameter(
            name='delivery_pk',
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.UUID,
            description='Delivery ID',
            required=True
        )
    ],
    responses={
        200: DeliveryCheckpointSerializer(many=True),
        404: {
            'description': 'Delivery not found',
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Delivery not found'
                }
            }
        }
    }
)
class DeliveryCheckpointsListView(APIView):
    """List delivery checkpoints."""
    permission_classes = [IsAuthenticated]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get(self, request, delivery_pk):
        try:
            # Check access to delivery
            user = request.user
            delivery_queryset = Delivery.objects.filter(id=delivery_pk)
            
            if user.user_type == 'Manager':
                delivery = get_object_or_404(delivery_queryset.filter(companie=user.companie))
            elif hasattr(user, 'employeer') and user.user_type == 'Driver':
                delivery = get_object_or_404(delivery_queryset.filter(driver=user.employeer))
            elif hasattr(user, 'customer'):
                delivery = get_object_or_404(delivery_queryset.filter(customer=user.customer))
            else:
                return Response(
                    {"detail": _("You don't have permission to view this delivery")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get checkpoints
            checkpoints = DeliveryCheckpoint.objects.filter(delivery=delivery).order_by('-timestamp')
            
            # Serialize results
            serializer = DeliveryCheckpointSerializer(checkpoints, many=True)
            
            logger.info(f"[DELIVERY VIEWS] - Listing {len(serializer.data)} checkpoints for delivery {delivery.id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error listing checkpoints for delivery {delivery_pk}: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Delivery'],
    operation_id='generate_delivery_report',
    summary='Generate delivery report',
    description='Starts generating a detailed delivery report.',
    parameters=[
        OpenApiParameter(
            name='pk',
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.UUID,
            description='Delivery ID',
            required=True
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'task_id': {'type': 'string'}
            }
        },
        404: {
            'description': 'Delivery not found',
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Delivery not found'
                }
            }
        }
    }
)
class DeliveryReportView(DeliveryBaseView, APIView):
    """Generate delivery report."""
    
    def get(self, request, pk):
        try:
            # Get object from filtered queryset
            queryset = Delivery.objects.filter(id=pk)
            if request.user.user_type == 'Manager':
                delivery = get_object_or_404(queryset.filter(companie=request.user.companie))
            elif hasattr(request.user, 'employeer'):
                delivery = get_object_or_404(queryset.filter(driver=request.user.employeer))
            elif hasattr(request.user, 'customer'):
                delivery = get_object_or_404(queryset.filter(customer=request.user.customer))
            else:
                return Response(
                    {"detail": _("You don't have permission to generate report for this delivery")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Start generating report
            task = generate_delivery_report.delay(str(delivery.id))
            
            logger.info(f"[DELIVERY VIEWS] - Delivery report generation started for delivery {delivery.id} by {request.user.username}")
            return Response({
                "message": _("Delivery report generation started"),
                "task_id": task.id
            })
            
        except Exception as e:
            logger.error(f"[DELIVERY VIEWS] - Error generating delivery report for {pk}: {str(e)}")
            return Response(
                {"detail": _("Error processing request")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
