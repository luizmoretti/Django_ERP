from django.utils.translation import gettext as _
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from .models import Vehicle, VehicleMaintenanceRecord, VehicleFuelRecord
from .serializers import (
    VehicleSerializer, 
    VehicleMaintenanceRecordSerializer, 
    VehicleFuelRecordSerializer
)
import logging

logger = logging.getLogger(__name__)


class VehicleBaseView:
    """Base view for vehicle-related operations
    
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
                'assigned_driver',
                'created_by',
                'updated_by'
            ).filter(companie=employeer.companie)
        except Exception as e:
            logger.error(f"Error getting queryset: {str(e)}")
            return self.queryset.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle Management'],
        operation_id='List Vehicles',
        summary='List all vehicles',
        description='Retrieve a list of all vehicles for authenticated user\'s company'
    ),
    post=extend_schema(
        tags=['Vehicle Management'],
        operation_id='Create Vehicle',
        summary='Create a new vehicle',
        description='Creates a new vehicle with the provided data',
        request=VehicleSerializer,
        responses={
            201: VehicleSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error creating vehicle'
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
class VehicleListView(generics.ListCreateAPIView, VehicleBaseView):
    """List all vehicles or create a new vehicle
    
    Returns a list of vehicles that belong to the user's company.
    Also allows creation of new vehicles.
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error listing vehicles: {str(e)}")
            return Response(
                {"error": _("Error retrieving vehicles")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    companie=request.user.companie,
                    created_by=request.user,
                    updated_by=request.user
                )
                logger.info(f"Vehicle created: {serializer.data.get('plate_number')}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.warning(f"Invalid vehicle data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating vehicle: {str(e)}")
            return Response(
                {"error": _("An error occurred while creating the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle Management'],
        operation_id='Retrieve Vehicle',
        summary='Retrieve a vehicle',
        description='Returns the details of a specific vehicle',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            200: VehicleSerializer,
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    ),
    put=extend_schema(
        tags=['Vehicle Management'],
        operation_id='Update Vehicle',
        summary='Update a vehicle',
        description='Updates a vehicle with the provided data',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        request=VehicleSerializer,
        responses={
            200: VehicleSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error updating vehicle'
                    }
                }
            },
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    ),
    delete=extend_schema(
        tags=['Vehicle Management'],
        operation_id='Delete Vehicle',
        summary='Delete a vehicle',
        description='Deletes a vehicle',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            204: None,
            400: {
                'description': 'Cannot delete vehicle',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Cannot delete vehicle that is associated with load orders'
                    }
                }
            },
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    )
)
class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView, VehicleBaseView):
    """Retrieve, update or delete a vehicle
    
    Returns detailed information about a vehicle, allows updating vehicle details,
    or deleting a vehicle if it's not associated with any load orders.
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Vehicle.DoesNotExist:
            return Response(
                {"error": _("Vehicle not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving vehicle {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while retrieving the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                logger.info(f"Vehicle updated: {instance.plate_number}")
                return Response(serializer.data)
            logger.warning(f"Invalid vehicle data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Vehicle.DoesNotExist:
            return Response(
                {"error": _("Vehicle not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating vehicle {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while updating the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check if the vehicle is being used in any load orders
            if hasattr(instance, 'load_orders') and instance.load_orders.exists():
                return Response(
                    {"error": _("Cannot delete vehicle that is associated with load orders")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            vehicle_plate = instance.plate_number
            instance.delete()
            logger.info(f"Vehicle deleted: {vehicle_plate}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Vehicle.DoesNotExist:
            return Response(
                {"error": _("Vehicle not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting vehicle {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while deleting the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Vehicle Management'],
        operation_id='Assign Driver',
        summary='Assign a driver to a vehicle',
        description='Assigns a driver to a vehicle',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        request={"application/json": {"type": "object", "properties": {"driver_id": {"type": "string"}}}},
        responses={
            200: VehicleSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Driver not found'
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'You do not have permission to assign drivers'
                    }
                }
            },
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    )
)
class VehicleAssignDriverView(generics.UpdateAPIView, VehicleBaseView):
    """Assign a driver to a vehicle
    
    Allows assigning a driver to a vehicle if the user has the appropriate permissions.
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_field = 'pk'
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Assign a driver to a vehicle"""
        try:
            if not request.user.has_perm('vehicle.assign_driver'):
                return Response(
                    {"error": _("You do not have permission to assign drivers")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            instance = self.get_object()
            
            # Get the driver from the request
            driver_id = request.data.get('driver_id')
            if not driver_id:
                return Response(
                    {"error": _("Driver ID is required")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Import here to avoid circular imports
            from apps.users.models import Employeer
            
            try:
                driver = Employeer.objects.get(pk=driver_id, companie=request.user.companie)
            except Employeer.DoesNotExist:
                return Response(
                    {"error": _("Driver not found")},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Assign the driver to the vehicle
            instance.assigned_driver = driver
            instance.save(update_fields=['assigned_driver', 'updated_at', 'updated_by'])
            
            # Return the updated vehicle
            serializer = self.get_serializer(instance)
            logger.info(f"Driver {driver.user.username} assigned to vehicle {instance.plate_number}")
            return Response(serializer.data)
        except Vehicle.DoesNotExist:
            return Response(
                {"error": _("Vehicle not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error assigning driver to vehicle {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while assigning the driver")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle Maintenance'],
        operation_id='List Maintenance Records',
        summary='List maintenance records',
        description='Returns a list of maintenance records for a specific vehicle',
        parameters=[
            OpenApiParameter(name="vehicle_id", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            200: VehicleMaintenanceRecordSerializer(many=True),
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    ),
    post=extend_schema(
        tags=['Vehicle Maintenance'],
        operation_id='Create Maintenance Record',
        summary='Create a maintenance record',
        description='Creates a new maintenance record for a specific vehicle',
        parameters=[
            OpenApiParameter(name="vehicle_id", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        request=VehicleMaintenanceRecordSerializer,
        responses={
            201: VehicleMaintenanceRecordSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error creating maintenance record'
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'You do not have permission to record maintenance'
                    }
                }
            },
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    )
)
class VehicleMaintenanceRecordListView(generics.ListCreateAPIView, VehicleBaseView):
    """List all maintenance records for a vehicle or create a new maintenance record
    
    Returns a list of maintenance records for a specific vehicle or creates a new
    maintenance record if the user has the appropriate permissions.
    """
    serializer_class = VehicleMaintenanceRecordSerializer
    
    def get_queryset(self):
        vehicle_id = self.kwargs.get('vehicle_id')
        if vehicle_id:
            return VehicleMaintenanceRecord.objects.filter(
                vehicle__id=vehicle_id, 
                vehicle__companie=self.request.user.companie
            ).select_related('vehicle', 'created_by', 'updated_by')
        return VehicleMaintenanceRecord.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            vehicle_id = kwargs.get('vehicle_id')
            # Check if vehicle exists
            vehicle = Vehicle.objects.filter(
                pk=vehicle_id, 
                companie=request.user.companie
            ).first()
            
            if not vehicle:
                return Response(
                    {"error": _("Vehicle not found")},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error listing maintenance records: {str(e)}")
            return Response(
                {"error": _("An error occurred while retrieving maintenance records")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('vehicle.record_maintenance'):
                return Response(
                    {"error": _("You do not have permission to record maintenance")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            vehicle_id = kwargs.get('vehicle_id')
            vehicle = Vehicle.objects.filter(
                pk=vehicle_id, 
                companie=request.user.companie
            ).first()
            
            if not vehicle:
                return Response(
                    {"error": _("Vehicle not found")},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    vehicle=vehicle,
                    created_by=request.user,
                    updated_by=request.user
                )
                logger.info(f"Maintenance record created for vehicle: {vehicle.plate_number}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Invalid maintenance record data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating maintenance record: {str(e)}")
            return Response(
                {"error": _("An error occurred while creating the maintenance record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle Maintenance'],
        operation_id='Retrieve Maintenance Record',
        summary='Retrieve a maintenance record',
        description='Returns the details of a specific maintenance record',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            200: VehicleMaintenanceRecordSerializer,
            404: {
                'description': 'Maintenance record not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Maintenance record not found'
                    }
                }
            }
        }
    ),
    put=extend_schema(
        tags=['Vehicle Maintenance'],
        operation_id='Update Maintenance Record',
        summary='Update a maintenance record',
        description='Updates a maintenance record with the provided data',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        request=VehicleMaintenanceRecordSerializer,
        responses={
            200: VehicleMaintenanceRecordSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error updating maintenance record'
                    }
                }
            },
            403: {
                'description': 'Permission denied',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'You do not have permission to update maintenance records'
                    }
                }
            },
            404: {
                'description': 'Maintenance record not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Maintenance record not found'
                    }
                }
            }
        }
    ),
    delete=extend_schema(
        tags=['Vehicle Maintenance'],
        operation_id='Delete Maintenance Record',
        summary='Delete a maintenance record',
        description='Deletes a maintenance record',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            204: None,
            403: {
                'description': 'Permission denied',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'You do not have permission to delete maintenance records'
                    }
                }
            },
            404: {
                'description': 'Maintenance record not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Maintenance record not found'
                    }
                }
            }
        }
    )
)
class VehicleMaintenanceRecordDetailView(generics.RetrieveUpdateDestroyAPIView, VehicleBaseView):
    """Retrieve, update or delete a maintenance record
    
    Returns detailed information about a maintenance record, allows updating record details,
    or deleting a record if the user has the appropriate permissions.
    """
    serializer_class = VehicleMaintenanceRecordSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        return VehicleMaintenanceRecord.objects.filter(
            vehicle__companie=self.request.user.companie
        ).select_related('vehicle', 'created_by', 'updated_by')
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except VehicleMaintenanceRecord.DoesNotExist:
            return Response(
                {"error": _("Maintenance record not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving maintenance record {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while retrieving the maintenance record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('vehicle.record_maintenance'):
                return Response(
                    {"error": _("You do not have permission to update maintenance records")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                logger.info(f"Maintenance record updated: {instance.id}")
                return Response(serializer.data)
            
            logger.warning(f"Invalid maintenance record data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except VehicleMaintenanceRecord.DoesNotExist:
            return Response(
                {"error": _("Maintenance record not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating maintenance record {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while updating the maintenance record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('vehicle.record_maintenance'):
                return Response(
                    {"error": _("You do not have permission to delete maintenance records")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            instance = self.get_object()
            instance.delete()
            logger.info(f"Maintenance record deleted: {instance.id}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VehicleMaintenanceRecord.DoesNotExist:
            return Response(
                {"error": _("Maintenance record not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting maintenance record {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while deleting the maintenance record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle Fuel'],
        operation_id='List Fuel Records',
        summary='List fuel records',
        description='Returns a list of fuel records for a specific vehicle',
        parameters=[
            OpenApiParameter(name="vehicle_id", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            200: VehicleFuelRecordSerializer(many=True),
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    ),
    post=extend_schema(
        tags=['Vehicle Fuel'],
        operation_id='Create Fuel Record',
        summary='Create a fuel record',
        description='Creates a new fuel record for a specific vehicle',
        parameters=[
            OpenApiParameter(name="vehicle_id", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        request=VehicleFuelRecordSerializer,
        responses={
            201: VehicleFuelRecordSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error creating fuel record'
                    }
                }
            },
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle not found'
                    }
                }
            }
        }
    )
)
class VehicleFuelRecordListView(generics.ListCreateAPIView, VehicleBaseView):
    """List all fuel records for a vehicle or create a new fuel record
    
    Returns a list of fuel records for a specific vehicle or creates a new
    fuel record.
    """
    serializer_class = VehicleFuelRecordSerializer
    
    def get_queryset(self):
        vehicle_id = self.kwargs.get('vehicle_id')
        if vehicle_id:
            return VehicleFuelRecord.objects.filter(
                vehicle__id=vehicle_id, 
                vehicle__companie=self.request.user.companie
            ).select_related('vehicle', 'created_by', 'updated_by')
        return VehicleFuelRecord.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            vehicle_id = kwargs.get('vehicle_id')
            # Check if vehicle exists
            vehicle = Vehicle.objects.filter(
                pk=vehicle_id, 
                companie=request.user.companie
            ).first()
            
            if not vehicle:
                return Response(
                    {"error": _("Vehicle not found")},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error listing fuel records: {str(e)}")
            return Response(
                {"error": _("An error occurred while retrieving fuel records")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            vehicle_id = kwargs.get('vehicle_id')
            vehicle = Vehicle.objects.filter(
                pk=vehicle_id, 
                companie=request.user.companie
            ).first()
            
            if not vehicle:
                return Response(
                    {"error": _("Vehicle not found")},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    vehicle=vehicle,
                    created_by=request.user,
                    updated_by=request.user
                )
                logger.info(f"Fuel record created for vehicle: {vehicle.plate_number}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Invalid fuel record data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating fuel record: {str(e)}")
            return Response(
                {"error": _("An error occurred while creating the fuel record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle Fuel'],
        operation_id='Retrieve Fuel Record',
        summary='Retrieve a fuel record',
        description='Returns the details of a specific fuel record',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            200: VehicleFuelRecordSerializer,
            404: {
                'description': 'Fuel record not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Fuel record not found'
                    }
                }
            }
        }
    ),
    put=extend_schema(
        tags=['Vehicle Fuel'],
        operation_id='Update Fuel Record',
        summary='Update a fuel record',
        description='Updates a fuel record with the provided data',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        request=VehicleFuelRecordSerializer,
        responses={
            200: VehicleFuelRecordSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error updating fuel record'
                    }
                }
            },
            404: {
                'description': 'Fuel record not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Fuel record not found'
                    }
                }
            }
        }
    ),
    delete=extend_schema(
        tags=['Vehicle Fuel'],
        operation_id='Delete Fuel Record',
        summary='Delete a fuel record',
        description='Deletes a fuel record',
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            204: None,
            404: {
                'description': 'Fuel record not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Fuel record not found'
                    }
                }
            }
        }
    )
)
class VehicleFuelRecordDetailView(generics.RetrieveUpdateDestroyAPIView, VehicleBaseView):
    """Retrieve, update or delete a fuel record
    
    Returns detailed information about a fuel record, allows updating record details,
    or deleting a record.
    """
    serializer_class = VehicleFuelRecordSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        return VehicleFuelRecord.objects.filter(
            vehicle__companie=self.request.user.companie
        ).select_related('vehicle', 'created_by', 'updated_by')
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except VehicleFuelRecord.DoesNotExist:
            return Response(
                {"error": _("Fuel record not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving fuel record {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while retrieving the fuel record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                logger.info(f"Fuel record updated: {instance.id}")
                return Response(serializer.data)
            
            logger.warning(f"Invalid fuel record data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except VehicleFuelRecord.DoesNotExist:
            return Response(
                {"error": _("Fuel record not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating fuel record {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while updating the fuel record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            logger.info(f"Fuel record deleted: {instance.id}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VehicleFuelRecord.DoesNotExist:
            return Response(
                {"error": _("Fuel record not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting fuel record {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while deleting the fuel record")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
