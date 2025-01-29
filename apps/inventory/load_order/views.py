from django.shortcuts import render
from .serializers import LoadOrderSerializer
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
from .models import LoadOrder
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class LoadOrderBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employeer = user.employeer_user
            return LoadOrder.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except LoadOrder.DoesNotExist:
            return LoadOrder.objects.none()
        
        
@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Load Orders'],
        operation_id='list_load_orders',
        summary='List all load orders',
        description='Retrieves a list of all load orders for the authenticated user.',
        responses={
            200: LoadOrderSerializer,
        }
    )
)
class LoadOrderListView(LoadOrderBaseView, ListAPIView):
    serializer_class = LoadOrderSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[LOAD ORDER VIEWS] - Load orders list retrieved successfully")
        return Response(serializer.data)
    

@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Load Orders'],
        operation_id='create_load_order',
        summary='Create a new load order',
        description='Creates a new load order with the specified items.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'load_to': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the vehicle to which the load order is going to be assigned'
                    },
                    'customer': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the customer to which the load order is going to be assigned'
                    },
                    'load_date': {
                        'type': 'string',
                        'format': 'date',
                        'description': 'The date that the vehicle is going to be loaded'
                    },
                    'items_data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product': {
                                    'type': 'string',
                                    'format': 'uuid',
                                    'description': 'The UUID of the product to be added to the load order'
                                },
                                'quantity': {
                                    'type': 'number',
                                    'description': 'The quantity of the product to be added to the load order'
                                }
                            },
                            'required': ['product', 'quantity']
                        }
                    }
                },
                'required': ['load_to', 'customer', 'items_data']
            }
        },
        responses={
            201: LoadOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error creating load order'
                    }
                }
            },
            403: {
                'description': 'Forbidden',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Permission denied'
                    }
                }
            }
        }
    )
)
class LoadOrderCreateView(LoadOrderBaseView, CreateAPIView):
    serializer_class = LoadOrderSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"[LOAD ORDER VIEWS] - Load order {serializer.data['id']} created successfully")
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
        except Exception as e:
            logger.error(f"[LOAD ORDER VIEWS] - Error creating load order: {str(e)}")
            return Response(
                {"detail": "Error creating load order"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Load Orders'],
        operation_id='retrieve_load_order',
        summary='Retrieve a load order',
        description='Retrieves a load order with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the load order to retrieve',
                required=True
            )
        ],
        responses={
            200: LoadOrderSerializer,
            404: {
                'description': 'Load order not found',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error retrieving load order'
                    }
                }
            }
        }
    )
)
class LoadOrderRetrieveView(LoadOrderBaseView, RetrieveAPIView):
    serializer_class = LoadOrderSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[LOAD ORDER VIEWS] - Load order {serializer.data['id']} retrieved successfully")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[LOAD ORDER VIEWS] - Error retrieving load order: {str(e)}")
            return Response(
                {"detail": "Error retrieving load order"},
                status=status.HTTP_400_BAD_REQUEST
            )



@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Load Orders'],
        operation_id='totaly_update_load_order',
        summary='Totaly update a load order',
        description='Totaly updates a load order with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the load order to update',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'load_to': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the vehicle to which the load order is going to be assigned'
                    },
                    'customer': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the customer to which the load order is going to be assigned'
                    },
                    'load_date': {
                        'type': 'string',
                        'format': 'date',
                        'description': 'The date that the vehicle is going to be loaded'
                    },
                    'items_data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product': {
                                    'type': 'string',
                                    'format': 'uuid',
                                    'description': 'The UUID of the product to be added to the load order'
                                },
                                'quantity': {
                                    'type': 'number',
                                    'description': 'The quantity of the product to be added to the load order'
                                }
                            },
                            'required': ['product', 'quantity']
                        }
                    }
                },
                'required': ['load_to', 'customer', 'items_data']
            }
        },
        responses={
            200: LoadOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating load order'
                    }
                }
            },
            403: {
                'description': 'Forbidden',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Permission denied'
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=['Inventory - Load Orders'],
        operation_id='partial_update_load_order',
        summary='Partial update a load order',
        description='Partial updates a load order with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the load order to update',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'load_to': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the vehicle to which the load order is going to be assigned'
                    },
                    'customer': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'The UUID of the customer to which the load order is going to be assigned'
                    },
                    'load_date': {
                        'type': 'string',
                        'format': 'date',
                        'description': 'The date that the vehicle is going to be loaded'
                    },
                    'items_data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product': {
                                    'type': 'string',
                                    'format': 'uuid',
                                    'description': 'The UUID of the product to be added to the load order'
                                },
                                'quantity': {
                                    'type': 'number',
                                    'description': 'The quantity of the product to be added to the load order'
                                }
                            },
                            'required': ['product', 'quantity']
                        }
                    }
                },
                'required': ['load_to', 'customer', 'items_data']
            }
        },
        responses={
            200: LoadOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating load order'
                    }
                }
            },
            403: {
                'description': 'Forbidden',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Permission denied'
                    }
                }
            }
        }
    )
)
class LoadOrderUpdateView(LoadOrderBaseView, UpdateAPIView):
    serializer_class = LoadOrderSerializer
    
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
            logger.error(f"[LOAD ORDER VIEWS] - Error updating load order: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[LOAD ORDER VIEWS] - Error updating load order: {str(e)}")
            return Response(
                {"detail": "Error updating load order"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"[LOAD ORDER VIEWS] - Error updating load order: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[LOAD ORDER VIEWS] - Error updating load order: {str(e)}")
            return Response(
                {"detail": "Error updating load order"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Load Orders'],
        operation_id='delete_load_order',
        summary='Delete a load order',
        description='Deletes a load order with the specified ID.',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='The UUID of the load order to delete',
                required=True
            )
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Load order deleted successfully'
                    }
                }
            }
        }
    )
)
class LoadOrderDestroyView(LoadOrderBaseView, DestroyAPIView):
    serializer_class = LoadOrderSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"detail": "Load order deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"[LOAD ORDER VIEWS] - Error deleting load order: {str(e)}")
            return Response(
                {"detail": "Error deleting load order"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
