from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from .models import PurchaseOrder, PurchaseOrderItem
from .serializers import PurchaseOrderSerializer
from .services.handlers import PurchaseOrderService, PurchaseOrderItemService
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
            employeer = user.employeer
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
class PurchaseOrderListView(generics.ListAPIView, PurchaseOrderBaseView):
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
        description='Delete a purchase order and all its items',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the purchase order to delete',
                required=True
            )
        ]
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

@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Approve Purchase Order',
        summary='Approve a purchase order',
        description='Approve a pending purchase order',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the purchase order to approve',
                required=True
            )
        ],
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid request',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Only pending orders can be approved'
                    }
                }
            }
        }
    )
)
class PurchaseOrderApproveView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Approve a purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                order = self.get_object()
                logger.info(f"Attempting to approve order {order.id}")
                logger.info(f"User permissions: {request.user.get_all_permissions()}")
                logger.info(f"User groups: {request.user.groups.all()}")
                logger.info(f"User type: {request.user.user_type}")
                logger.info(f"Order status: {order.status}")
                logger.info(f"Order company: {order.companie}")
                logger.info(f"User company: {request.user.employeer.companie}")
                logger.info(f"User employeer: {request.user.employeer}")
                updated_order = PurchaseOrderService.approve_order(
                    order=order,
                    user=request.user
                )
                serializer = self.get_serializer(updated_order)
                return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Validation error approving order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error approving purchase order: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal error approving order"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Reject Purchase Order',
        summary='Reject a purchase order',
        description='Reject a pending purchase order',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'reason': {
                        'type': 'string',
                        'description': 'Reason for rejection',
                        'required': True
                    }
                }
            }
        },
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid request',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Only pending orders can be rejected'
                    }
                }
            }
        }
    )
)
class PurchaseOrderRejectView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Reject a purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            reason = request.data.get('reason')
            if not reason:
                return Response(
                    {"error": "Reason for rejection is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            updated_order = PurchaseOrderService.reject_order(
                order_id=order.id,
                user=request.user,
                reason=reason
            )
            serializer = self.get_serializer(updated_order)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error rejecting purchase order: {str(e)}")
            return Response(
                {"error": "Internal error rejecting order"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Cancel Purchase Order',
        summary='Cancel a purchase order',
        description='Cancel a pending or approved purchase order',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'reason': {
                        'type': 'string',
                        'description': 'Reason for cancellation',
                        'required': True
                    }
                }
            }
        },
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid request',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Only pending or approved orders can be canceled'
                    }
                }
            }
        }
    )
)
class PurchaseOrderCancelView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Cancel a purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            reason = request.data.get('reason')
            if not reason:
                return Response(
                    {"error": "Reason for cancellation is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            updated_order = PurchaseOrderService.cancel_order(
                order_id=order.id,
                user=request.user,
                reason=reason
            )
            serializer = self.get_serializer(updated_order)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error canceling purchase order: {str(e)}")
            return Response(
                {"error": "Internal error canceling order"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Add Item to Purchase Order',
        summary='Add item to purchase order',
        description='Add a new item to a pending purchase order',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product': {
                        'type': 'string',
                        'description': 'Product UUID',
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
                }
            }
        },
        responses={
            201: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid request',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Items can only be added to pending orders'
                    }
                }
            }
        }
    )
)
class PurchaseOrderAddItemView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Add item to purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            item = PurchaseOrderItemService.add_item(
                order_id=order.id,
                product_id=request.data.get('product'),
                quantity=request.data.get('quantity'),
                unit_price=request.data.get('unit_price'),
                user=request.user
            )
            # Reload the order to include the new item
            order.refresh_from_db()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding item to purchase order: {str(e)}")
            return Response(
                {"error": "Internal error adding item"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Update Purchase Order Item',
        summary='Update purchase order item',
        description='Update quantity or price of a purchase order item',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'quantity': {
                        'type': 'integer',
                        'description': 'New quantity',
                        'minimum': 1,
                        'required': False
                    },
                    'unit_price': {
                        'type': 'number',
                        'description': 'New price per unit',
                        'format': 'decimal',
                        'minimum': 0,
                        'required': False
                    }
                }
            }
        },
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid request',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Items can only be updated in pending orders'
                    }
                }
            }
        }
    )
)
class PurchaseOrderUpdateItemView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Update purchase order item"""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def put(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            updated_item = PurchaseOrderItemService.update_item(
                item_id=item.id,
                quantity=request.data.get('quantity'),
                unit_price=request.data.get('unit_price'),
                user=request.user
            )
            # Reload the order to include the changes
            order = updated_item.purchase_order
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating purchase order item: {str(e)}")
            return Response(
                {"error": "Internal error updating item"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Remove Purchase Order Item',
        summary='Remove item from purchase order',
        description='Remove an item from a pending purchase order',
        responses={
            204: None,
            400: {
                'description': 'Invalid request',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Items can only be removed from pending orders'
                    }
                }
            }
        }
    )
)
class PurchaseOrderRemoveItemView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Remove item from purchase order"""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    def delete(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            PurchaseOrderItemService.remove_item(
                item_id=item.id,
                user=request.user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error removing purchase order item: {str(e)}")
            return Response(
                {"error": "Internal error removing item"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
