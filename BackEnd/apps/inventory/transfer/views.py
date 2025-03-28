from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from .models import Transfer
from .serializers import TransferSerializer
from .notifications.handlers import TransferNotificationHandler
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)


class TransferBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # Verify if it is a swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                return TransferSerializer
            
            employeer = user.employeer
            return Transfer.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except Transfer.DoesNotExist:
            return Transfer.objects.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Transfers'],
        operation_id='list_transfers',
        summary='List all transfers',
        description="""
        Retrieve a list of all transfers for the authenticated user's employeer.
        """,
        responses={
            200: TransferSerializer,
        }
    )
)
class TransferListView(TransferBaseView, generics.ListAPIView):
    serializer_class = TransferSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[TRANSFER VIEWS] - Transfers list retrieved successfully")
        return Response(serializer.data)
    


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Transfers'],
        operation_id='create_transfer',
        summary='Create a new transfer',
        description="""
        Create a new transfer record with the provided information
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
                        'example': 'Transfer'
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
            201: TransferSerializer,
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
class TransferCreateView(TransferBaseView, generics.CreateAPIView):
    serializer_class = TransferSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"[TRANSFER VIEWS] - Transfer {serializer.data['id']} created successfully")
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
        except Exception as e:
            logger.error(f"[TRANSFER VIEWS] - Error creating transfer: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    
@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Transfers'],
        operation_id='retrieve_transfer',
        summary='Retrieve a transfer',
        description='Get details of a specific transfer by its ID',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                description='UUID of the transfer to retrieve',
                required=True
            )
        ],
        responses={
            200: TransferSerializer,
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
class TransferRetrieveView(TransferBaseView, generics.RetrieveAPIView):
    serializer_class = TransferSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[TRANSFER VIEWS] - Error retrieving transfer: {str(e)}")
            return Response(
                {"detail": "Error retrieving transfer"},
                status=500
            )

@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Transfers'],
        operation_id='update_transfer',
        summary='Update a transfer',
        description='Update an existing transfer with new information',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the transfer to update',
                required=True
            )
        ],
        request={
            'application/json':{
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
            },
        },
        responses={
            200: TransferSerializer,
            400: {
                'application/json':{
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': 'string',
                            'example': 'Invalid data provided'
                        }
                    }
                }
            },
            404: {
                'application/json':{
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': 'string',
                            'example': 'Not found.'
                        }
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=['Inventory - Transfers'],
        operation_id='partial_update_transfer',
        summary='Partial update a transfer',
        description='Update an existing transfer with new information. Only the fields provided in the request will be updated.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the transfer to update',
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
            200: TransferSerializer,
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
class TransferUpdateView(TransferBaseView, generics.UpdateAPIView):
    serializer_class = TransferSerializer
    
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
            logger.error(f"[TRANSFER VIEWS] - Validation error updating transfer: {str(e)}")
            return Response(
                {"detail": str(e)}
            )
        except Exception as e:
            logger.error(f"[TRANSFER VIEWS] - Error updating transfer: {str(e)}")
            return Response(
                {"detail": "Error updating transfer"},
                status=500
            )

@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Transfers'],
        operation_id='delete_transfer',
        summary='Delete a transfer',
        description='Delete a specific transfer by its ID',
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
class TransferDestroyView(TransferBaseView, generics.DestroyAPIView):
    serializer_class = TransferSerializer
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=204)
        except Exception as e:
            logger.error(f"Error deleting transfer: {str(e)}")
            return Response(
                {"detail": "Error deleting transfer"},
                status=500
            )
    
    
