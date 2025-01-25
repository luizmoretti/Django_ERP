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
from apps.companies.employeers.serializers import (
    EmployeerSerializer, ListAllEmployeersSerializer
)
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
                'user', 'companie', 'created_by', 'updated_by'
            ).filter(is_active=True, companie=employeer.companie)
        except Employeer.DoesNotExist:
            return Employeer.objects.none()


@extend_schema_view(
    post=extend_schema(
        tags=["Companies - Employees"],
        operation_id="create_employee",
        summary="Create new employee",
        description="""
        Creates a new employee record with the provided information.
        
        The employee must be associated with both a user account and a company.
        Both created_by and updated_by will be set to the creating user.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string', 'minLength': 1},
                    'last_name': {'type': 'string', 'minLength': 1},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'email': {'type': 'string', 'format': 'email'},
                    'phone': {'type': 'string'},
                    'address': {'type': 'string'},
                    'city': {'type': 'string'},
                    'zip_code': {'type': 'string'},
                    'user_id': {'type': 'string', 'format': 'uuid'},
                    'companie_id': {'type': 'string', 'format': 'uuid'},
                },
                'required': ['first_name', 'last_name', 'email', 'user_id', 'companie_id']
            }
        },
        responses={
            201: EmployeerSerializer,
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
class EmployeerCreateView(BaseEmployeerView, CreateAPIView):
    """
    View for creating new employee records.
    
    This view handles employee creation with automatic user and company
    association, and tracks who created the record.
    """
    serializer_class = EmployeerSerializer

    def perform_create(self, serializer):
        try:
            instance = serializer.save(
                created_by=self.request.user,
                updated_by=self.request.user
            )
            logger.info(
                f"Employee created successfully: {instance.first_name} {instance.last_name}",
                extra={
                    'employee_id': instance.id,
                    'created_by': self.request.user.id,
                    'company_id': instance.companie_id,
                    'user_id': instance.user_id
                }
            )
        except Exception as e:
            logger.error(
                f"Error creating employee: {str(e)}",
                extra={
                    'user_id': self.request.user.id,
                    'error': str(e)
                },
                exc_info=True
            )
            raise ValidationError({
                'error': "Error creating employee record",
                'detail': str(e)
            })


@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Employees"],
        operation_id="retrieve_employee",
        summary="Get employee details",
        description="Retrieves complete information for a specific employee",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the employee to retrieve',
                required=True,
            ),
        ],
        responses={
            200: EmployeerSerializer,
            404: {'description': 'Employee not found'}
        }
    )
)
class EmployeerRetrieveView(BaseEmployeerView, RetrieveAPIView):
    """
    View for retrieving specific employee details.
    
    Provides complete employee information including related
    user, company, and audit data.
    """
    serializer_class = EmployeerSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(
                f"Employee retrieved: {instance.first_name} {instance.last_name}",
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
        Updates all employee information.
        
        Requires all fields to be provided, even if unchanged.
        The updated_by field will be set to the updating user.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the employee to update',
                required=True,
            ),
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string', 'minLength': 1},
                    'last_name': {'type': 'string', 'minLength': 1},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'email': {'type': 'string', 'format': 'email'},
                    'phone': {'type': 'string'},
                    'address': {'type': 'string'},
                    'city': {'type': 'string'},
                    'zip_code': {'type': 'string'},
                    'user_id': {'type': 'string', 'format': 'uuid'},
                    'companie_id': {'type': 'string', 'format': 'uuid'},
                },
                'required': ['first_name', 'last_name', 'email', 'user_id', 'companie_id']
            }
        },
        responses={
            200: EmployeerSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'Employee not found'}
        }
    ),
    patch=extend_schema(
        tags=["Companies - Employees"],
        operation_id="partial_update_employee",
        summary="Partially update employee",
        description="""
        Updates specific employee fields.
        
        Only provided fields will be updated.
        The updated_by field will be set to the updating user.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the employee to update',
                required=True,
            ),
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string', 'minLength': 1},
                    'last_name': {'type': 'string', 'minLength': 1},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'email': {'type': 'string', 'format': 'email'},
                    'phone': {'type': 'string'},
                    'address': {'type': 'string'},
                    'city': {'type': 'string'},
                    'zip_code': {'type': 'string'},
                    'user_id': {'type': 'string', 'format': 'uuid'},
                    'companie_id': {'type': 'string', 'format': 'uuid'},
                }
            }
        },
        responses={
            200: EmployeerSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'Employee not found'}
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
                'first_name': serializer.instance.first_name,
                'last_name': serializer.instance.last_name,
                'email': serializer.instance.email,
                'companie_id': serializer.instance.companie_id,
                'is_active': serializer.instance.is_active
            }
            instance = serializer.save(updated_by=self.request.user)
            
            # Log específico para reativação
            if 'is_active' in serializer.validated_data and instance.is_active:
                logger.info(
                    f"Employee reactivated: {instance.first_name} {instance.last_name}",
                    extra={
                        'employee_id': instance.id,
                        'reactivated_by': self.request.user.id
                    }
                )
            else:
                logger.info(
                    f"Employee updated: {instance.first_name} {instance.last_name}",
                    extra={
                        'employee_id': instance.id,
                        'updated_by': self.request.user.id,
                        'old_data': old_data,
                        'updated_fields': list(serializer.validated_data.keys())
                    }
                )
        except Exception as e:
            logger.error(
                f"Error updating employee: {str(e)}",
                extra={
                    'employee_id': serializer.instance.id,
                    'user_id': self.request.user.id,
                    'error': str(e)
                },
                exc_info=True
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
            employee_name = f"{instance.first_name} {instance.last_name}"
            
            # Perform soft delete
            instance = serializer.save(
                is_active=False,
                updated_by=self.request.user
            )
            
            logger.info(
                f"Employee soft deleted: {employee_name}",
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
                f"Error soft deleting employee: {str(e)}",
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
        operation_id="hard_delete_employeer",
        summary="Permanently delete employee",
        description="""
        Permanently deletes an employee record from the database.
        This operation cannot be undone. Use with caution.
        Consider using soft delete instead if you need to preserve history.
        """,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the employee to delete permanently',
                required=True,
            ),
        ],
        responses={
            200: {
                'description': 'Employee successfully deleted',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'default': 'Employee permanently deleted'}
                        }
                    }
                }
            },
            404: {'description': 'Employee not found'}
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
            employee_name = f"{instance.first_name} {instance.last_name}"
            instance.delete()
            
            logger.info(
                f"Employee permanently deleted: {employee_name}",
                extra={
                    'employee_id': employee_id,
                    'deleted_by': self.request.user.id
                }
            )
        except Exception as e:
            logger.error(
                f"Error permanently deleting employee: {str(e)}",
                extra={
                    'employee_id': instance.id,
                    'user_id': self.request.user.id,
                    'error': str(e)
                },
                exc_info=True
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
        description="Retrieves a paginated list of all employees",
        responses={
            200: ListAllEmployeersSerializer,
            401: {'description': 'Authentication credentials not provided'}
        }
    )
)
class EmployeerListView(BaseEmployeerView, ListAPIView):
    """
    View for listing all employees.
    
    Provides a paginated list of all employees with basic information,
    using the simplified ListAllEmployeersSerializer.
    """
    serializer_class = ListAllEmployeersSerializer

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
