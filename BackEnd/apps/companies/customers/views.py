from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    UpdateAPIView, DestroyAPIView, GenericAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from apps.companies.customers.services import CustomerService, CustomerLeadService
from apps.companies.customers.models import Customer, CustomerLeads
from apps.companies.customers.serializers import (
    CustomerSerializer,
    CustomerLeadsSerializer
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
            if not hasattr(user, 'employeer'):
                queryset = Customer.objects.none()
            else:
                queryset = Customer.objects.select_related(
                    'companie', 'created_by', 'updated_by'
                ).filter(companie=user.employeer.companie, is_active=True)
            return queryset
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
            if customer.companie != self.request.user.employeer.companie:
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
        if customer.companie != self.request.user.employeer.companie:
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



class BaseLeadsView:
    """
    Base view for CustomerLeads operations.
    
    This class provides common functionality for all lead-related views,
    including permission checking, queryset filtering, and logging.
    
    Attributes:
        permission_classes (list): List of permission classes requiring authentication
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset to only show leads from the user's company.
        
        Returns:
            QuerySet: Filtered CustomerLeads queryset
        """
        user = self.request.user
        
        # Ensure user has a valid employeer with company association
        if not hasattr(user, 'employeer') or not user.employeer or not user.employeer.companie:
            logger.warning(
                "[CUSTOMER LEADS VIEW] - User without valid company association attempted to access leads",
                extra={'user_id': user.id}
            )
            return CustomerLeads.objects.none()
        
        # Filter by company
        queryset = CustomerLeads.objects.filter(companie=user.employeer.companie)
        
        logger.debug(
            f"[CUSTOMER LEADS VIEW] - Filtered queryset by company",
            extra={
                'company_id': str(user.employeer.companie.id),
                'lead_count': queryset.count(),
                'user_id': user.id
            }
        )
        
        return queryset



@extend_schema_view(
    post=extend_schema(
        tags=["Customers - Leads"],
        operation_id="generate_customer_leads",
        summary="Generate customer leads from Google Local Search",
        description="""
        Generates leads by searching for businesses through Google Local Search API.
        
        This endpoint queries Google Local Search via SerpAPI to find businesses matching
        the specified search criteria. Results are automatically converted to CustomerLeads
        records in the system, with duplicate detection to prevent creating duplicate leads.
        
        The search supports filtering by location and can retrieve either a single page of
        results or all available pages (which may take longer but provides more comprehensive results).
        """,
        parameters=[
            OpenApiParameter(
                name='query',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search term for businesses (e.g., "plumbers", "restaurants")',
                required=True
            ),
            OpenApiParameter(
                name='location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Geographic location to focus search (e.g., "Miami, FL")',
                required=False
            ),
            OpenApiParameter(
                name='limit',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results to return per page',
                required=False
            ),
            OpenApiParameter(
                name='include_all_pages',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Whether to retrieve results from all pages (may increase response time)',
                required=False
            )
        ],
        responses={
            200: {
                'description': 'Leads generated successfully',
                'type': 'object',
                'properties': {
                    'total_results': {
                        'type': 'integer',
                        'description': 'Total number of business results found'
                    },
                    'new_leads': {
                        'type': 'integer',
                        'description': 'Number of new leads created'
                    },
                    'existing_leads': {
                        'type': 'integer',
                        'description': 'Number of existing leads updated'
                    },
                    'message': {
                        'type': 'string',
                        'description': 'Summary message about the operation',
                        'examples': [
                            'Successfully generated 5 new leads.',
                            'No new leads were generated.'
                        ]
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'description': 'Error message explaining the validation failure'
                    }
                }
            },
            401: {
                'description': 'Authentication credentials not provided or invalid'
            },
            403: {
                'description': 'Insufficient permissions to perform this operation'
            },
            500: {
                'description': 'Server error',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'description': 'Error message'
                    }
                }
            }
        }
    )
)
class GenerateLeadsView(BaseLeadsView, CreateAPIView):
    """
    View for generating leads from Google Local search results.
    
    This view processes customer search queries to fetch detailed business information
    from Google Local using SerpAPI. It then populates the customer records with this data.
    
    Attributes:
        permission_classes (list): List of permission classes requiring authentication
        
    Methods:
        post(self, request, *args, **kwargs): Handles the generation of leads by processing search queries
        
    Note:
        The view requires authentication and proper configuration of SerpAPI credentials.
        
    Inherits:
        BaseCustomerView{
            permission_classes: List of permission classes requiring authentication
        }
    """
    serializer_class = None # Not used in this view
    
    def post(self, request, *args, **kwargs):
        """
        Generate leads from Google Local search results.
        
        Args:
            request: HTTP request object containing search parameters
            
        Returns:
            Response: JSON response with summary of generated leads
            
        Raises:
            ValidationError: If required parameters are missing or invalid
        """
        try:
            # Extract parameters from request data
            query = request.query_params.get('query')
            location = request.query_params.get('location', '')
            limit = request.query_params.get('limit')
            include_all_pages = request.query_params.get('include_all_pages', False)
            
            # Validate required parameters
            if not query:
                logger.error(
                    "[CUSTOMER LEADS VIEW] - Missing required parameter: query",
                    extra={'requester_id': request.user.id}
                )
                return Response(
                    {"error": "Search query is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize lead service
            lead_service = CustomerLeadService()
            
            # Generate leads using the service
            result = lead_service.generate_leads_from_search(
                query=query,
                location=location,
                user=request.user,
                limit=limit,
                include_all_pages=include_all_pages
            )
            
            # Log success
            logger.info(
                f"[CUSTOMER LEADS VIEW] - Generated leads successfully: {result['new_leads']} new, {result['existing_leads']} existing",
                extra={
                    'requester_id': request.user.id,
                    'total_results': result['total_results']
                }
            )
            
            # Return result summary (excluding actual lead objects for performance)
            return Response({
                "total_results": result['total_results'],
                "new_leads": result['new_leads'],
                "existing_leads": result['existing_leads'],
                "message": result['message']
            })
            
        except ValidationError as e:
            logger.error(
                f"[CUSTOMER LEADS VIEW] - Validation error generating leads: {str(e)}",
                extra={'requester_id': request.user.id},
                exc_info=True
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"[CUSTOMER LEADS VIEW] - Error generating leads: {str(e)}",
                extra={'requester_id': request.user.id},
                exc_info=True
            )
            return Response(
                {"error": "An unexpected error occurred while generating leads"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
@extend_schema_view(
    get=extend_schema(
        tags=["Customers - Leads"],
        operation_id="list_customer_leads",
        description="""List all customer leads associated with the user's company.
        
        Supports filtering by status and searching by name.
        
        Returns:
            List[CustomerLeads]: List of customer leads associated with the user's company.
        """,
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter leads by status (e.g., 'New', 'Contacted', 'Converted')",
                required=False,
                type=OpenApiTypes.STR,
                enum=[
                    'New',
                    'Contacted',
                    'Converted'
                ]
            ),
            OpenApiParameter(
                name="search",
                description="Search leads by name (case insensitive partial match)",
                required=False,
                type=OpenApiTypes.STR
            )
        ],
        responses={
            200: CustomerLeadsSerializer(many=True)
        }
    )
)
class ListLeadsView(BaseLeadsView, ListAPIView):
    """
    View for listing customer leads.
    
    This view returns a paginated list of all customer leads associated with
    the user's company, sorted by creation date (newest first).
    """
    serializer_class = CustomerLeadsSerializer
    
    def get_queryset(self):
        """
        Get optimized queryset with proper ordering and prefetching.

        Returns:
            QuerySet: Optimized CustomerLeads queryset
        """
        # Get base queryset from parent class (with company filtering)
        queryset = super().get_queryset()
        
        # Optimize with select_related for foreign keys, but only select necessary fields
        queryset = queryset.select_related(
            'companie',       # Pre-fetch company data
            'created_by',     # Pre-fetch user who created the lead
            'updated_by'      # Pre-fetch user who last updated the lead
        ).only(
            'id', 'name', 'status', 'created_at', 'updated_at',
            'companie__id', 'companie__name',
            'created_by__id', 'created_by__name', 
            'updated_by__id', 'updated_by__name'
        )
        
        # Apply filters if provided in query params
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Allow search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        # Order by newest first
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        List all customer leads for the user's company with optimized performance.
        """
        try:
            # Get the queryset and apply filters
            queryset = self.filter_queryset(self.get_queryset())
            
            # Apply standard pagination
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                
                logger.info(
                    "[CUSTOMER LEADS VIEW] - Customer leads listed successfully",
                    extra={'requester_id': request.user.id}
                )
                return self.get_paginated_response(serializer.data)
            
            # If pagination is not required (which should be rare)
            serializer = self.get_serializer(queryset, many=True)
            
            logger.info(
                "[CUSTOMER LEADS VIEW] - Customer leads listed successfully",
                extra={'requester_id': request.user.id}
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"[CUSTOMER LEADS VIEW] - Error listing leads: {str(e)}",
                extra={'requester_id': request.user.id},
                exc_info=True
            )
            raise