from django.shortcuts import render
from django.http import Http404, HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from apps.companies.customers.services import CustomerService
from apps.companies.customers.models import Customer
from apps.companies.customers.serializers import (
    CustomerSerializer
)
import logging

logger = logging.getLogger(__name__)

class BaseCustomerView:
    """
    Base view class with common configurations for customer views.
    
    Provides:
        - Common queryset with optimized related field loading
        - Default permission class requiring authentication
        - Logging setup for customer operations
        
    Note:
        By default, only active customers are included in the queryset
    Attributes:
        permission_classes (list): List of permission classes
        
    Methods:
        get_queryset(self): Override queryset to include only active customers from the same company as the logged-in user
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # Filters only customers from the same company as the logged-in user
            employeer = user.employeer_user
            return Customer.objects.select_related(
                'companie', 'created_by', 'updated_by'
            ).filter(companie=employeer.companie, is_active=True)
        except:
            return Customer.objects.none()


@extend_schema_view(
    post=extend_schema(
        tags=["Companies - Customers"],
        operation_id="create_customer",
        summary="Create new customer",
        description="""
        Creates a new customer record with the provided information.
        
        Company association and user tracking (created_by, updated_by) are handled automatically.
        
        Address Handling:
        - If another_billing_address=True, _billing_address_data will be used to create a custom billing address
        - If another_shipping_address=True, _shipping_address_data will be used to create a custom shipping address
        - If either is False, the corresponding address will be created using the customer's main address
        
        Note:
        - The response will include billing_address_data and shipping_address_data
        - For creation, use _billing_address_data and _shipping_address_data (with underscore)
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string', 'minLength': 1, 'required': True},
                    'last_name': {'type': 'string', 'minLength': 1, 'required': True},
                    'address': {'type': 'string', 'required': True},
                    'city': {'type': 'string', 'required': True},
                    'state': {'type': 'string', 'required': True},
                    'zip_code': {'type': 'string', 'required': True},
                    'country': {'type': 'string', 'default': 'USA', 'required': False},
                    'phone': {'type': 'string', 'required': False},
                    'email': {'type': 'string', 'format': 'email', 'required': False},
                    'another_billing_address': {'type': 'boolean', 'default': False, 'required': False},
                    '_billing_address_data': {
                        'type': 'object',
                        'properties': {
                            'address': {'type': 'string'},
                            'city': {'type': 'string'},
                            'state': {'type': 'string'},
                            'zip_code': {'type': 'string'},
                            'country': {'type': 'string'},
                            'phone': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'}
                        },
                        'required': False
                    },
                    'another_shipping_address': {'type': 'boolean', 'default': False, 'required': False},
                    '_shipping_address_data': {
                        'type': 'object',
                        'properties': {
                            'address': {'type': 'string'},
                            'city': {'type': 'string'},
                            'state': {'type': 'string'},
                            'zip_code': {'type': 'string'},
                            'country': {'type': 'string'},
                            'phone': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'}
                        },
                        'required': False
                    },
                    'is_active': {'type': 'boolean', 'default': True, 'required': False}
                },
                'required': ['first_name', 'last_name', 'address', 'city', 'state', 'zip_code']
            }
        },
        responses={
            201: CustomerSerializer,
            400: {
                'description': 'Invalid input data',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'detail': {'type': 'string'}
                }
            }
        }
    )
)
class CustomerCreateView(BaseCustomerView, CreateAPIView):
    """
    View for creating new customer records.
    
    This view handles customer creation with automatic employee
    association for tracking who created the record.
    """
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Customers"],
        operation_id="retrieve_customer_by_id",
        summary="Get customer details by ID",
        description="""
        Retrieves complete information for a specific customer using their UUID.
        
        Example:
        GET /api/customers/retrieve/123e4567-e89b-12d3-a456-426614174000/
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the customer to retrieve',
                required=True,
            ),
        ],
        responses={
            200: CustomerSerializer,
            400: {
                'description': 'Invalid UUID format',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'example': 'Invalid UUID format'}
                }
            },
            404: {
                'description': 'Customer not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'example': 'Customer not found'}
                }
            }
        }
    )
)
class CustomerRetrieveByIdView(BaseCustomerView, RetrieveAPIView):
    """
    View for retrieving specific customer details by UUID.
    
    Provides complete customer information including related
    company and employee data using the CustomerService.
    """
    serializer_class = CustomerSerializer
    lookup_field = 'pk'
    
    def get_object(self):
        try:
            pk = self.kwargs.get('pk')
            if not pk or len(pk) != 36:  # UUID tem 36 caracteres
                raise ValidationError('Invalid UUID format')
                
            customer = CustomerService.get_customers(id=pk)
            
            if not customer:
                raise Http404('Customer not found')
                
            # Check if user has permission to access this customer
            if customer.companie != self.request.user.employeer_user.companie:
                raise PermissionDenied("You don't have permission to access this customer")
                
            return customer
            
        except (TypeError, ValueError, ValidationError) as e:
            raise ValidationError(str(e))
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            logger.info(
                f"[VIEW] Customer retrieved by ID: {instance.first_name} {instance.last_name}",
                extra={
                    'customer_id': instance.id,
                    'requester_id': request.user.id
                }
            )
            
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(
                f"[VIEW] Invalid UUID format",
                extra={
                    'pk': kwargs.get('pk'),
                    'requester_id': request.user.id
                }
            )
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Http404:
            logger.warning(
                f"[VIEW] Customer not found by ID",
                extra={
                    'pk': kwargs.get('pk'),
                    'requester_id': request.user.id
                }
            )
            return Response(
                {'detail': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        except PermissionDenied as e:
            logger.warning(
                f"[VIEW] Permission denied accessing customer by ID: {str(e)}",
                extra={
                    'pk': kwargs.get('pk'),
                    'requester_id': request.user.id
                }
            )
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
            
        except Exception as e:
            logger.error(
                f"[VIEW] Error retrieving customer by ID: {str(e)}",
                extra={
                    'pk': kwargs.get('pk'),
                    'requester_id': request.user.id
                },
                exc_info=True
            )
            return Response(
                {'detail': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Customers"],
        operation_id="retrieve_customer_by_name",
        summary="Get customer details by full name",
        description="""
        Retrieves complete information for a specific customer using their full name.
        
        Example:
        GET /api/customers/retrieve/?first_name=John&last_name=Doe
        """,
        parameters=[
            OpenApiParameter(
                name='first_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='First name of the customer',
                required=True,
            ),
            OpenApiParameter(
                name='last_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Last name of the customer',
                required=True,
            ),
        ],
        responses={
            200: CustomerSerializer,
            400: {
                'description': 'Invalid input data or user not associated with employee',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'example': 'Invalid input data or user not associated with employee'}
                }
            },
            404: {
                'description': 'Customer not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'example': 'Customer not found'}
                }
            }
        }
    )
)
class CustomerRetrieveByNameView(BaseCustomerView, RetrieveAPIView):
    """
    View for retrieving specific customer details by full name.
    
    Provides complete customer information including related
    company and employee data using the CustomerService.
    """
    serializer_class = CustomerSerializer
    
    def get_object(self):
        first_name = self.request.query_params.get('first_name')
        last_name = self.request.query_params.get('last_name')
        
        if not (first_name and last_name):
            raise ValidationError("Both first_name and last_name are required")
            
        customer = CustomerService.get_customers(
            first_name=first_name,
            last_name=last_name
        )
        
        if not customer:
            raise Http404("Customer not found")
            
        # Check if user has permission to access this customer
        if customer.companie != self.request.user.employeer_user.companie:
            raise PermissionDenied("You don't have permission to access this customer")
            
        return customer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            logger.info(
                f"[VIEW] Customer retrieved by name: {instance.first_name} {instance.last_name}",
                extra={
                    'customer_id': instance.id,
                    'requester_id': request.user.id
                }
            )
            
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.warning(
                f"[VIEW] Invalid parameters for customer retrieval by name: {str(e)}",
                extra={
                    'first_name': request.query_params.get('first_name'),
                    'last_name': request.query_params.get('last_name'),
                    'requester_id': request.user.id
                }
            )
            raise
            
        except Http404:
            logger.warning(
                f"[VIEW] Customer not found by name",
                extra={
                    'first_name': request.query_params.get('first_name'),
                    'last_name': request.query_params.get('last_name'),
                    'requester_id': request.user.id
                }
            )
            raise
            
        except PermissionDenied as e:
            logger.warning(
                f"[VIEW] Permission denied accessing customer by name: {str(e)}",
                extra={
                    'first_name': request.query_params.get('first_name'),
                    'last_name': request.query_params.get('last_name'),
                    'requester_id': request.user.id
                }
            )
            raise
            
        except Exception as e:
            logger.error(
                f"[VIEW] Error retrieving customer by name: {str(e)}",
                extra={
                    'first_name': request.query_params.get('first_name'),
                    'last_name': request.query_params.get('last_name'),
                    'requester_id': request.user.id
                },
                exc_info=True
            )
            raise


@extend_schema_view(
    put=extend_schema(
        tags=["Companies - Customers"],
        operation_id="update_customer",
        summary="Update customer details",
        description="""
        Updates customer information. All fields are optional.
        
        Company association and user tracking (updated_by) are handled automatically.
        
        Address Handling:
        - If another_billing_address=True, _billing_address_data will update the billing address
        - If another_shipping_address=True, _shipping_address_data will update the shipping address
        - If either is False, the corresponding address will sync with the customer's main address
        
        Note:
        - The response will include billing_address_data and shipping_address_data
        - For updates, use _billing_address_data and _shipping_address_data (with underscore)
        - Validation ensures address data is provided when another_*_address is True
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string', 'minLength': 1},
                    'last_name': {'type': 'string', 'minLength': 1},
                    'address': {'type': 'string'},
                    'city': {'type': 'string'},
                    'state': {'type': 'string'},
                    'zip_code': {'type': 'string'},
                    'country': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                    'another_billing_address': {'type': 'boolean'},
                    '_billing_address_data': {
                        'type': 'object',
                        'properties': {
                            'address': {'type': 'string'},
                            'city': {'type': 'string'},
                            'state': {'type': 'string'},
                            'zip_code': {'type': 'string'},
                            'country': {'type': 'string'},
                            'phone': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'}
                        }
                    },
                    'another_shipping_address': {'type': 'boolean'},
                    '_shipping_address_data': {
                        'type': 'object',
                        'properties': {
                            'address': {'type': 'string'},
                            'city': {'type': 'string'},
                            'state': {'type': 'string'},
                            'zip_code': {'type': 'string'},
                            'country': {'type': 'string'},
                            'phone': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'}
                        }
                    },
                    'is_active': {'type': 'boolean'}
                }
            }
        },
        responses={
            200: CustomerSerializer,
            400: {
                'description': 'Invalid input data',
                'application/json':{
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'},
                        'detail': {'type': 'string'}
                    }
                },
            },
            404: {
                'description': 'Customer not found',
                'application/json':{
                    'type': 'object',
                    'properties': {
                        'detail': {'type': 'string'}
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=["Companies - Customers"],
        operation_id="partial_update_customer",
        summary="Partially update customer",
        description="""
        Updates specific fields of a customer record.
        
        Company association and user tracking (updated_by) are handled automatically.
        Changing another_billing_address or another_shipping_address will not affect
        existing address records.
        """,
        request=CustomerSerializer,
        responses={
            200: CustomerSerializer,
            400: {
                'description': 'Invalid input data',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'detail': {'type': 'string'}
                }
            },
            404: {
                'description': 'Customer not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        }
    )
)
class CustomerUpdateView(BaseCustomerView, UpdateAPIView):
    """
    View for updating customer records.
    
    Handles both complete (PUT) and partial (PATCH) updates with
    automatic tracking of the updating employee.
    """
    serializer_class = CustomerSerializer

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"[VIEW] Error updating customer: {str(e)}",
                extra={
                    'customer_id': kwargs.get('pk'),
                    'requester_id': request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise ValidationError({
                'error': "Error updating customer",
                'detail': str(e)
            })


@extend_schema_view(
    delete=extend_schema(
        tags=["Companies - Customers"],
        operation_id="delete_customer",
        summary="Delete customer",
        description="Permanently removes a customer record from the system",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the customer to delete',
                required=True,
            ),
        ],
        responses={
            204: {'description': 'Customer successfully deleted'},
            404: {'description': 'Customer not found'}
        }
    )
)
class CustomerDeleteView(BaseCustomerView, DestroyAPIView):
    """
    View for deleting customer records.
    
    Implements permanent deletion of customer records.
    Consider implementing soft delete if record preservation is needed.
    """
    serializer_class = CustomerSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"[VIEW] Error deleting customer: {str(e)}",
                extra={
                    'customer_id': kwargs.get('pk'),
                    'user_id': request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise ValidationError({
                'error': "Error deleting customer",
                'detail': str(e)
            })


@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Customers"],
        operation_id="list_customers",
        summary="List all customers",
        description="Retrieves a paginated list of all customers",
        responses={
            200: CustomerSerializer,
            401: {'description': 'Authentication credentials not provided'}
        }
    )
)
class CustomerListView(BaseCustomerView, ListAPIView):
    """
    View for listing all customers.
    
    Provides a paginated list of all customers with basic information,
    CustomerSerializer.
    """
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            logger.info(
                "Customer list retrieved",
                extra={
                    'requester_id': request.user.id,
                    'count': self.get_queryset().count()
                }
            )
            return response
        except Exception as e:
            logger.error(
                f"Error retrieving customer list: {str(e)}",
                extra={'requester_id': request.user.id},
                exc_info=True
            )
            raise
