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
    CustomerSerializer, ListAllCustomersSerializer
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
        
        The creating user must be associated with an employee record.
        Both created_by and updated_by will be set to the creating employee.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'minLength': 1},
                    'address': {'type': 'string'},
                    'city': {'type': 'string'},
                    'zip_code': {'type': 'string'},
                    'country': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                    'companie_id': {'type': 'string', 'format': 'uuid'},
                },
                'required': ['name', 'companie_id']
            }
        },
        responses={
            201: CustomerSerializer,
            400: {
                'description': 'Invalid input data or user not associated with employee',
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

    def perform_create(self, serializer):
        try:
            employeer = self.request.user.employeer_user
            instance = serializer.save(
                created_by=employeer,
                updated_by=employeer
            )
            logger.info(
                f"Customer created successfully: {instance.name}",
                extra={
                    'customer_id': instance.id,
                    'created_by': employeer.id,
                    'companie_id': instance.companie_id
                }
            )
        except Exception as e:
            logger.error(
                f"Error creating customer: {str(e)}",
                extra={
                    'user_id': self.request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise serializer.ValidationError({
                'error': "User must be associated with an employee to create a customer",
                'detail': str(e)
            })


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
        summary="Update customer",
        description="""
        Updates all customer information.
        
        Requires all fields to be provided, even if unchanged.
        The updating user must be associated with an employee record.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the customer to update',
                required=True,
            ),
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'minLength': 1},
                    'address': {'type': 'string'},
                    'city': {'type': 'string'},
                    'zip_code': {'type': 'string'},
                    'country': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                    'companie_id': {'type': 'string', 'format': 'uuid'},
                },
                'required': ['name', 'address', 'city', 'zip_code', 'country', 'phone', 'email', 'companie_id']
            }
        },
        responses={
            200: CustomerSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'Customer not found'}
        }
    ),
    patch=extend_schema(
        tags=["Companies - Customers"],
        operation_id="partial_update_customer",
        summary="Partially update customer",
        description="""
        Updates specific customer fields.
        
        Only provided fields will be updated.
        The updating user must be associated with an employee record.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the customer to update',
                required=True,
            ),
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'minLength': 1},
                    'address': {'type': 'string'},
                    'city': {'type': 'string'},
                    'zip_code': {'type': 'string'},
                    'country': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                    'companie_id': {'type': 'string', 'format': 'uuid'},
                }
            }
        },
        responses={
            200: CustomerSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'Customer not found'}
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
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        try:
            employeer = self.request.user.employeer_user
            old_data = {
                'name': serializer.instance.name,
                'companie_id': serializer.instance.companie_id
            }
            instance = serializer.save(updated_by=employeer)
            
            logger.info(
                f"Customer updated: {instance.name}",
                extra={
                    'customer_id': instance.id,
                    'updated_by': employeer.id,
                    'old_data': old_data,
                    'updated_fields': list(serializer.validated_data.keys())
                }
            )
        except Exception as e:
            logger.error(
                f"Error updating customer: {str(e)}",
                extra={
                    'customer_id': serializer.instance.id,
                    'user_id': self.request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise serializer.ValidationError({
                'error': "User must be associated with an employee to update a customer",
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
    permission_classes = [IsAuthenticated]
    
    def perform_destroy(self, instance):
        try:
            customer_id = instance.id
            customer_name = instance.name
            instance.delete()
            
            logger.info(
                f"Customer deleted: {customer_name}",
                extra={
                    'customer_id': customer_id,
                    'deleted_by': self.request.user.id
                }
            )
        except Exception as e:
            logger.error(
                f"Error deleting customer: {str(e)}",
                extra={
                    'customer_id': instance.id,
                    'user_id': self.request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise serializers.ValidationError({
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
            200: ListAllCustomersSerializer,
            401: {'description': 'Authentication credentials not provided'}
        }
    )
)
class CustomerListView(BaseCustomerView, ListAPIView):
    """
    View for listing all customers.
    
    Provides a paginated list of all customers with basic information,
    using the simplified ListAllCustomersSerializer.
    """
    serializer_class = ListAllCustomersSerializer
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
