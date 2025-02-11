from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer
import logging

logger = logging.getLogger(__name__)


class PurchaseOrderBaseView:
    """Base view for purchase order views
    
    Handles:
    - Authentication
    - Company-specific queryset filtering
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employeer = user.employeer_user
            return self.queryset.select_related(
                'companie',
                'supplier',
                'created_by',
                'updated_by'
            ).prefetch_related(
                'items',
                'items__product'
            ).filter(companie=employeer.companie)
        except Exception as e:
            logger.error(f"Error getting queryset: {str(e)}")
            return self.queryset.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='List Purchase Orders',
        summary='List all purchase orders',
        description='Retrieve a list of all purchase orders for authenticated user'
    )
)
class PurchaseOrderListView(PurchaseOrderBaseView, generics.ListAPIView):
    """List all purchase orders
    
    Returns a list of purchase orders that belong to the user's company.
    Each order includes basic information and a list of its items.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error listing purchase orders: {str(e)}")
            return Response(
                {"error": "Error retrieving purchase orders"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Create Purchase Order',
        summary='Create a new purchase order',
        description='Create a new purchase order with items',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'supplier': {
                        'type': 'string',
                        'description': 'UUID of the supplier',
                        'format': 'uuid',
                        'required': True
                    },
                    'expected_delivery': {
                        'type': 'string',
                        'description': 'Expected delivery date',
                        'format': 'date',
                        'required': True
                    },
                    'status': {
                        'type': 'string',
                        'description': 'Order status',
                        'maxLength': 20,
                        'required': True
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Additional notes about the order',
                        'maxLength': 255,
                        'required': False
                    },
                    'items_data': {
                        'type': 'array',
                        'description': 'List of items to be included in the order',
                        'required': True,
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product': {
                                    'type': 'string',
                                    'description': 'UUID of the product',
                                    'format': 'uuid',
                                    'required': True
                                },
                                'quantity': {
                                    'type': 'integer',
                                    'description': 'Quantity to order',
                                    'minimum': 1,
                                    'required': True
                                },
                                'unit_price': {
                                    'type': 'number',
                                    'description': 'Price per unit',
                                    'format': 'decimal',
                                    'minimum': 0,
                                    'required': True
                                }
                            },
                            'required': ['product', 'quantity', 'unit_price']
                        }
                    }
                },
                'required': ['supplier', 'expected_delivery', 'status', 'items_data']
            }
        },
        responses={
            201: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error creating purchase order'
                    }
                }
            },
            403: {
                'description': 'You do not have permission to perform this action',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'You do not have permission to perform this action'
                    }
                }
            },
            500: {
                'description': 'Internal server error',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Internal server error'
                    }
                }
            }
        }
    )
)
class PurchaseOrderCreateView(PurchaseOrderBaseView, generics.CreateAPIView):
    """Create a new purchase order
    
    Creates a new purchase order with the provided supplier and items.
    The order is created in a transaction to ensure data consistency.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error creating purchase order: {str(e)}")
            return Response(
                {"error": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Retrieve Purchase Order',
        summary='Get purchase order details',
        description='Get detailed information about a specific purchase order'
    )
)
class PurchaseOrderRetrieveView(PurchaseOrderBaseView, generics.RetrieveAPIView):
    """Retrieve a specific purchase order
    
    Returns detailed information about a purchase order, including all its items
    and related information like supplier and product details.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error retrieving purchase order: {str(e)}")
            return Response(
                {"error": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Update Purchase Order',
        summary='Update purchase order',
        description='Update an existing purchase order and its items'
    ),
    patch=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Partial Update Purchase Order',
        summary='Partially update purchase order',
        description='Update specific fields of an existing purchase order'
    )
)
class PurchaseOrderUpdateView(PurchaseOrderBaseView, generics.UpdateAPIView):
    """Update a purchase order
    
    Updates an existing purchase order and its items. The update is performed
    in a transaction to ensure data consistency. Supports both PUT and PATCH methods.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error updating purchase order: {str(e)}")
            return Response(
                {"error": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Delete Purchase Order',
        summary='Delete purchase order',
        description='Delete a purchase order and all its items'
    )
)
class PurchaseOrderDeleteView(PurchaseOrderBaseView, generics.DestroyAPIView):
    """Delete a purchase order
    
    Deletes a purchase order and all its associated items.
    The deletion is performed in a transaction to ensure data consistency.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error deleting purchase order: {str(e)}")
            return Response(
                {"error": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
