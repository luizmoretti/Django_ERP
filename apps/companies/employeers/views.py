from django.shortcuts import render
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from apps.companies.employeers.models import Employeer
from apps.companies.employeers.serializers import EmployeerSerializer
import logging

logger = logging.getLogger(__name__)


class BaseEmployeerView:
    """
    Base view class with common configurations for employee views.
    
    Provides:
        - Common queryset with optimized related field loading
        - Default permission class requiring authentication
        - Logging setup for employee operations
        
    Note:
        By default, only active employees are included in the queryset
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employeer = user.employeer_user
            return Employeer.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except Employeer.DoesNotExist:
            return Employeer.objects.none()


@extend_schema_view(
    post=extend_schema(
        tags=["Companies - Employees"],
        operation_id="create_employee",
        summary="Create new employee",
        description="""
        Creates a new employee record with the provided information.
        
        The employee must be associated with a user account.
        Both created_by and updated_by will be set automatically.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Full name of the employee'},
                    'id_number': {'type': 'string', 'description': 'Employee identification number', 'example': '123-45-6789'},
                    'date_of_birth': {'type': 'string', 'format': 'date', 'description': 'Birth date (YYYY-MM-DD)', 'example': '1990-01-01'},
                    'payroll_schedule': {'type': 'string', 'description': 'Payroll schedule', 'example': 'Weekly'},
                    'payment_type': {'type': 'string', 'description': 'Payment type', 'example': 'Day'},
                    'rate': {'type': 'number', 'description': 'Hourly rate or monthly salary', 'example': 150.00},
                    'email': {'type': 'string', 'format': 'email', 'description': 'Contact email', 'example': 'employee@example.com'},
                    'phone': {'type': 'string', 'description': 'Contact phone number', 'example': '(123) 456-7890'},
                    'address': {'type': 'string', 'description': 'Physical address', 'example': '123 Main St'},
                    'city': {'type': 'string', 'description': 'City name', 'example': 'Los Angeles'},
                    'state': {'type': 'string', 'description': 'State/Province', 'example': 'CA'},
                    'zip_code': {'type': 'string', 'description': 'ZIP/Postal code', 'example': '12345'},
                    'country': {'type': 'string', 'description': 'Country name', 'default': 'USA'},
                    'user': {'type': 'string', 'format': 'uuid', 'description': 'UUID of the associated user account'}
                },
                'required': ['name', 'id_number', 'date_of_birth', 'payroll_schedule', 'payment_type', 'rate']
            }
        },
        responses={
            201: EmployeerSerializer,
            400: {
                'description': 'Invalid input data',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'example': 'Error creating employee'}
                }
            }
        }
    )
)
class EmployeerCreateView(BaseEmployeerView, CreateAPIView):
    """
    View for creating new employee records.
    
    This view handles employee creation with automatic user association,
    and tracks who created the record.
    """
    serializer_class = EmployeerSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            logger.info(
                f"Employee created: {instance.name}",
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        except Exception as e:
            logger.error(
                f"Error creating employee: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "Error creating employee"},
                status=HTTP_400_BAD_REQUEST
            )
        


@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Employees"],
        operation_id="retrieve_employee",
        summary="Get employee details",
        description="Retrieves complete information about a specific employee.",
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="UUID of the employee to retrieve",
                required=True
            )
        ],
        responses={
            200: EmployeerSerializer,
            404: {
                'description': 'Employee not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        }
    )
)
class EmployeerRetrieveView(BaseEmployeerView, RetrieveAPIView):
    """
    View for retrieving specific employee details.
    
    Provides complete employee information including related
    user and audit data.
    """
    serializer_class = EmployeerSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(
                f"Employee retrieved: {instance.name}",
                extra={
                    'employee_id': instance.id,
                    'requester_id': request.user.id
                }
            )
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error retrieving employee: {str(e)}",
                extra={
                    'employee_id': kwargs.get('id'),
                    'requester_id': request.user.id
                },
                exc_info=True
            )
            raise


@extend_schema_view(
    put=extend_schema(
        tags=["Companies - Employees"],
        operation_id="update_employee",
        summary="Update employee",
        description="""
        Updates an existing employee record with the provided information.
        All fields are optional except date_of_birth and user.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Full name of the employee'},
                    'id_number': {'type': 'string', 'description': 'Employee identification number'},
                    'date_of_birth': {'type': 'string', 'format': 'date', 'description': 'Birth date (YYYY-MM-DD)'},
                    'email': {'type': 'string', 'format': 'email', 'description': 'Contact email'},
                    'phone': {'type': 'string', 'description': 'Contact phone number'},
                    'address': {'type': 'string', 'description': 'Physical address'},
                    'city': {'type': 'string', 'description': 'City name'},
                    'state': {'type': 'string', 'description': 'State/Province'},
                    'zip_code': {'type': 'string', 'description': 'ZIP/Postal code'},
                    'country': {'type': 'string', 'description': 'Country name'},
                    'user': {'type': 'string', 'format': 'uuid', 'description': 'UUID of the associated user account'}
                },
                'required': ['date_of_birth', 'user']
            }
        },
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="UUID of the employee to update",
                required=True
            )
        ],
        responses={
            200: EmployeerSerializer,
            400: {
                'description': 'Invalid input data',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            },
            404: {
                'description': 'Employee not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        }
    ),
    patch=extend_schema(
        tags=["Companies - Employees"],
        operation_id="partial_update_employee",
        summary="Partial update employee",
        description="Updates specific fields of an existing employee record.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Full name of the employee'},
                    'id_number': {'type': 'string', 'description': 'Employee identification number'},
                    'date_of_birth': {'type': 'string', 'format': 'date', 'description': 'Birth date (YYYY-MM-DD)'},
                    'email': {'type': 'string', 'format': 'email', 'description': 'Contact email'},
                    'phone': {'type': 'string', 'description': 'Contact phone number'},
                    'address': {'type': 'string', 'description': 'Physical address'},
                    'city': {'type': 'string', 'description': 'City name'},
                    'state': {'type': 'string', 'description': 'State/Province'},
                    'zip_code': {'type': 'string', 'description': 'ZIP/Postal code'},
                    'country': {'type': 'string', 'description': 'Country name'},
                    'user': {'type': 'string', 'format': 'uuid', 'description': 'UUID of the associated user account'}
                }
            }
        },
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="UUID of the employee to update",
                required=True
            )
        ],
        responses={
            200: EmployeerSerializer,
            400: {
                'description': 'Invalid input data',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            },
            404: {
                'description': 'Employee not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        }
    )
)
class EmployeerUpdateView(BaseEmployeerView, UpdateAPIView):
    """
    View for updating employee records.
    
    Handles both complete (PUT) and partial (PATCH) updates with
    automatic tracking of the updating user.
    
    Note:
        Attempts to update an inactive employee will result in an error,
        except when updating only the is_active field.
    """
    serializer_class = EmployeerSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Override queryset to include inactive employees in the lookup,
        but prevent their update with a custom message.
        """
        return Employeer.objects.select_related(
            'user', 'companie', 'created_by', 'updated_by'
        )
    
    def get_object(self):
        """
        Retrieve the object, checking if it's inactive.
        
        Allows update if only updating is_active field.
        
        Raises:
            ValidationError: If the employee is inactive and trying to update other fields
        """
        obj = super().get_object()
        request_data = self.request.data
        
        # Se o funcionário está inativo e não é uma atualização apenas do is_active
        if not obj.is_active and (
            len(request_data) != 1 or 'is_active' not in request_data
        ):
            raise ValidationError({
                'error': 'Inactive employee',
                'detail': 'The employee was removed from the records or is inactive.'
            })
        return obj

    def perform_update(self, serializer):
        try:
            old_data = {
                'name': serializer.instance.name,
                'email': serializer.instance.email,
                'user_id': serializer.instance.user_id
            }
            instance = serializer.save(updated_by=self.request.user)
            
            logger.info(
                f"[EMPLOYEER VIEWS] - Employee updated: {instance.name}",
                extra={
                    'employee_id': instance.id,
                    'updated_by': self.request.user.id,
                    'old_data': old_data,
                    'new_data': serializer.validated_data
                }
            )
            return instance
        except Exception as e:
            logger.error(
                f"[EMPLOYEER VIEWS] - Error updating employee: {str(e)}",
                extra={'error': str(e)}
            )
            raise ValidationError({
                'error': "Erro ao atualizar funcionário",
                'detail': str(e)
            })


@extend_schema_view(
    put=extend_schema(
        tags=["Companies - Employees Soft Delete"],
        operation_id="soft_delete_employeer_put",
        summary="Soft delete employee (PUT)",
        description="""
        Marks an employee as inactive in the system (soft delete).
        Use this endpoint for complete updates of the is_active status.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the employee to soft delete',
                required=True,
            ),
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'is_active': {'type': 'boolean'}
                },
                'required': ['is_active']
            }
        },
        responses={
            200: {
                'description': 'Employee successfully deactivated',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'employee': {'$ref': '#/components/schemas/Employeer'}
                        }
                    }
                }
            },
            404: {'description': 'Employee not found'}
        }
    ),
    patch=extend_schema(
        tags=["Companies - Employees Soft Delete"],
        operation_id="soft_delete_employeer_patch",
        summary="Soft delete employee (PATCH)",
        description="""
        Marks an employee as inactive in the system (soft delete).
        Use this endpoint for partial updates of the is_active status.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the employee to soft delete',
                required=True,
            ),
        ],
        responses={
            200: {
                'description': 'Employee successfully deactivated',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'employee': {'$ref': '#/components/schemas/Employeer'}
                        }
                    }
                }
            },
            404: {'description': 'Employee not found'}
        }
    )
)
class EmployeerSoftDeleteView(BaseEmployeerView, UpdateAPIView):
    """
    View for soft deleting employee records.
    
    Instead of permanently deleting the record, this view marks
    the employee as inactive (is_active=False).
    """
    serializer_class = EmployeerSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Override queryset to include all employees (active and inactive).
        This is necessary to allow soft delete operations.
        """
        return Employeer.objects.select_related(
            'user', 'companie', 'created_by', 'updated_by'
        )
    
    def validate_soft_delete(self, instance, data):
        """
        Validate if the soft delete operation can be performed.
        
        Args:
            instance: The employee instance
            data: Request data
            
        Raises:
            ValidationError: If employee is already inactive
        """
        if not instance.is_active:
            raise ValidationError({
                'error': 'Inactive employee',
                'detail': 'The employee is already deactivated.'
            })
    
    def update(self, request, *args, **kwargs):
        """
        Handle both PUT and PATCH requests for soft delete.
        Validates the operation before proceeding.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Force is_active to False for soft delete
        request.data['is_active'] = False
        
        # Validate before proceeding
        self.validate_soft_delete(instance, request.data)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            employee_id = instance.id
            employee_name = instance.name
            
            # Perform soft delete
            instance = serializer.save(
                is_active=False,
                updated_by=self.request.user
            )
            
            logger.info(
                f"[EMPLOYEER VIEWS] - Employee soft deleted: {employee_name}",
                extra={
                    'employee_id': employee_id,
                    'deactivated_by': self.request.user.id
                }
            )
            
            return Response({
                'message': 'Employee successfully deactivated',
                'employee': EmployeerSerializer(instance).data
            }, status=HTTP_200_OK)
            
        except Exception as e:
            logger.error(
                f"[EMPLOYEER VIEWS] - Error soft deleting employee: {str(e)}",
                extra={
                    'employee_id': instance.id,
                    'user_id': self.request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise ValidationError({
                'error': 'Error when deactivating employee',
                'detail': str(e)
            })

@extend_schema_view(
    delete=extend_schema(
        tags=["Companies - Employees"],
        operation_id="delete_employee",
        summary="Delete employee",
        description="Permanently deletes an employee record.",
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="UUID of the employee to delete",
                required=True
            )
        ],
        responses={
            204: {'description': 'Employee successfully deleted'},
            404: {
                'description': 'Employee not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        }
    )
)
class EmployeerDestroyView(BaseEmployeerView, DestroyAPIView):
    """
    View for permanently deleting employee records.
    
    This view performs a hard delete, which means the record
    is permanently removed from the database.
    """
    serializer_class = EmployeerSerializer
    lookup_field = 'id'
    
    
    def get_queryset(self):
        """
        Override queryset to include inactive employees in the lookup,
        but prevent their update with a custom message.
        """
        return Employeer.objects.select_related(
            'user', 'companie', 'created_by', 'updated_by'
        )
    
    def perform_destroy(self, instance):
        """
        Perform the hard delete of the employee record.
        
        Logs the deletion action with employee details.
        """
        try:
            employee_id = instance.id
            employee_name = instance.name
            instance.delete()
            
            logger.info(
                f"[EMPLOYEER VIEWS] - Employee permanently deleted: {employee_name}",
                extra={
                    'employee_id': employee_id,
                    'deleted_by': self.request.user.id
                }
            )
        except Exception as e:
            logger.error(
                f"[EMPLOYEER VIEWS] - Error deleting employee: {str(e)}",
                extra={
                    'employee_id': instance.id,
                    'error': str(e)
                }
            )
            raise ValidationError({
                'error': "Error deleting employee record",
                'detail': str(e)
            })
    
    def delete(self, request, *args, **kwargs):
        """
        Override delete to return a success message.
        """
        self.destroy(request, *args, **kwargs)
        return Response(data={"message": "Employee deleted successfully"}, status=HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Employees"],
        operation_id="list_employees",
        summary="List all employees",
        description="Retrieves a paginated list of all active employees.",
        responses={
            200: EmployeerSerializer,
            401: {'description': 'Authentication credentials not provided'}
        }
    )
)
class EmployeerListView(BaseEmployeerView, ListAPIView):
    """
    View for listing all employees.
    
    Provides a paginated list of all employees with basic information,
    using the EmployeerSerializer.
    """
    serializer_class = EmployeerSerializer

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            logger.info(
                "Employee list retrieved",
                extra={
                    'requester_id': request.user.id,
                    'count': self.get_queryset().count()
                }
            )
            return response
        except Exception as e:
            logger.error(
                f"Error retrieving employee list: {str(e)}",
                extra={'requester_id': request.user.id},
                exc_info=True
            )
            raise
