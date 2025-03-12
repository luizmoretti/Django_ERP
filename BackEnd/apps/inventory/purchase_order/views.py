from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from .models import PurchaseOrder, PurchaseOrderItem
from .serializers import PurchaseOrderSerializer
from .services.handlers import PurchaseOrderService, PurchaseOrderItemService
from .services.validators import PurchaseOrderValidator
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
            # Validate purchase order data
            PurchaseOrderValidator.validate_purchase_order_data(request.data)
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error creating purchase order: {str(e)}")
            return Response(
                {"error": f"{str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating purchase order: {str(e)}")
            return Response(
                {"error": f"Error creating purchase order: {str(e)}"},
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
        description='Update an existing purchase order',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'supplier': {
                        'type': 'string',
                        'description': 'UUID of the supplier',
                        'format': 'uuid',
                        'required': False
                    },
                    'expected_delivery': {
                        'type': 'string',
                        'description': 'Expected delivery date',
                        'format': 'date',
                        'required': False
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Additional notes about the order',
                        'maxLength': 255,
                        'required': False
                    }
                }
            }
        },
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Invalid data'
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
            404: {
                'description': 'Not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Purchase order not found'
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
class PurchaseOrderUpdateView(PurchaseOrderBaseView, generics.UpdateAPIView):
    """Update a purchase order
    
    Updates an existing purchase order with the provided data.
    Only pending orders can be updated.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            
            # Validate can modify order
            PurchaseOrderValidator.validate_can_modify_order(order)
            
            # Update order
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error updating purchase order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating purchase order: {str(e)}")
            return Response(
                {"error": f"Error updating purchase order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    patch=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Partial Update Purchase Order',
        summary='Partially update purchase order',
        description='Update specific fields of an existing purchase order'
    )
)
class PurchaseOrderUpdateView(PurchaseOrderBaseView, generics.UpdateAPIView):
    """Update a purchase order
    
    Updates an existing purchase order with the provided data.
    Only pending orders can be updated.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            
            # Validate can modify order
            PurchaseOrderValidator.validate_can_modify_order(order)
            
            # Update order
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error updating purchase order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating purchase order: {str(e)}")
            return Response(
                {"error": f"Error updating purchase order: {str(e)}"},
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
        description='Change the status of a purchase order to approved',
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Only pending orders can be approved'
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
            404: {
                'description': 'Not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Purchase order not found'
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
class PurchaseOrderApproveView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Approve a purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            
            # Validate status transition
            PurchaseOrderValidator.validate_status_transition(order, 'approved', request.user)
            
            # Validate order has items
            PurchaseOrderValidator.validate_order_has_items(order.id)
            
            # Approve order
            order = PurchaseOrderService.approve_order(order, request.user)
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Error approving purchase order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error approving purchase order: {str(e)}")
            return Response(
                {"error": f"Error approving purchase order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Reject Purchase Order',
        summary='Reject a purchase order',
        description='Change the status of a purchase order to rejected',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'reason': {
                        'type': 'string',
                        'description': 'Reason for rejection',
                        'maxLength': 255,
                        'required': True
                    }
                },
                'required': ['reason']
            }
        },
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Only pending orders can be rejected'
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
            404: {
                'description': 'Not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Purchase order not found'
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
class PurchaseOrderRejectView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Reject a purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            
            # Check if reason is provided
            if 'reason' not in request.data or not request.data['reason']:
                raise ValidationError({"reason": "Reason for rejection is required"})
            
            # Validate status transition
            PurchaseOrderValidator.validate_status_transition(order, 'rejected', request.user)
            
            # Reject order
            order = PurchaseOrderService.reject_order(
                order.id, 
                request.user, 
                request.data['reason']
            )
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Error rejecting purchase order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error rejecting purchase order: {str(e)}")
            return Response(
                {"error": f"Error rejecting purchase order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Cancel Purchase Order',
        summary='Cancel a purchase order',
        description='Change the status of a purchase order to cancelled',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'reason': {
                        'type': 'string',
                        'description': 'Reason for cancellation',
                        'maxLength': 255,
                        'required': True
                    }
                },
                'required': ['reason']
            }
        },
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Only pending or approved orders can be cancelled'
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
            404: {
                'description': 'Not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Purchase order not found'
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
class PurchaseOrderCancelView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Cancel a purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            
            # Check if reason is provided
            if 'reason' not in request.data or not request.data['reason']:
                raise ValidationError({"reason": "Reason for cancellation is required"})
            
            # Validate status transition
            PurchaseOrderValidator.validate_status_transition(order, 'cancelled', request.user)
            
            # Cancel order
            order = PurchaseOrderService.cancel_order(
                order.id, 
                request.user, 
                request.data['reason']
            )
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Error cancelling purchase order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error cancelling purchase order: {str(e)}")
            return Response(
                {"error": f"Error cancelling purchase order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Add Item to Purchase Order',
        summary='Add an item to a purchase order',
        description='Add a new item to an existing purchase order',
        request={
            'application/json': {
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
        },
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Invalid item data'
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
            404: {
                'description': 'Not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Purchase order not found'
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
class PurchaseOrderAddItemView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Add item to purchase order"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            
            # Validate item data
            item_data = {
                'product': request.data.get('product'),
                'quantity': request.data.get('quantity'),
                'unit_price': request.data.get('unit_price')
            }
            PurchaseOrderValidator.validate_purchase_order_item_data(item_data)
            
            # Validate can add item
            PurchaseOrderValidator.validate_can_add_item(order)
            
            # Add item
            PurchaseOrderItemService.add_item(
                order_id=order.id,
                product_id=request.data.get('product'),
                quantity=request.data.get('quantity'),
                unit_price=request.data.get('unit_price'),
                user=request.user
            )
            
            # Refresh order
            order.refresh_from_db()
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Error adding item to purchase order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding item to purchase order: {str(e)}")
            return Response(
                {"error": f"Error adding item to purchase order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Update Purchase Order Item',
        summary='Update a purchase order item',
        description='Update an existing item in a purchase order',
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
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Invalid item data'
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
            404: {
                'description': 'Not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Item not found'
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
class PurchaseOrderUpdateItemView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Update purchase order item"""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            
            # Validate can update item
            PurchaseOrderValidator.validate_can_update_item(item)
            
            # Update item
            updated_item = PurchaseOrderItemService.update_item(
                item_id=item.id,
                quantity=request.data.get('quantity'),
                unit_price=request.data.get('unit_price'),
                user=request.user
            )
            
            # Return the updated order
            order = updated_item.purchase_order
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Error updating purchase order item: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating purchase order item: {str(e)}")
            return Response(
                {"error": f"Error updating purchase order item: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Purchase Orders'],
        operation_id='Remove Item from Purchase Order',
        summary='Remove an item from a purchase order',
        description='Remove an existing item from a purchase order',
        responses={
            200: PurchaseOrderSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Cannot remove the last item from a purchase order'
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
            404: {
                'description': 'Not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Item not found'
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
class PurchaseOrderRemoveItemView(PurchaseOrderBaseView, generics.GenericAPIView):
    """Remove item from purchase order"""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            order = item.purchase_order
            
            # Validate can remove item
            PurchaseOrderValidator.validate_can_remove_item(item)
            
            # Remove item
            PurchaseOrderItemService.remove_item(
                item_id=item.id,
                user=request.user
            )
            
            # Refresh order
            order.refresh_from_db()
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Error removing item from purchase order: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error removing item from purchase order: {str(e)}")
            return Response(
                {"error": f"Error removing item from purchase order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
