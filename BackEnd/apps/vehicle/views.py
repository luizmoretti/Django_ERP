from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from .models import Vehicle
from .serializers import VehicleSerializer
import logging

logger = logging.getLogger(__name__)


class VehicleBaseView:
    """Base class for Vehicle views
    
    Provides common functionality for Vehicle views, such as
    permission classes and queryset filtering by company.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset filtered by user's company"""
        return Vehicle.objects.filter(
            companie=self.request.user.companie
        ).select_related('assigned_driver')


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle'],
        operation_id='list_vehicles',
        summary='List vehicles',
        description="""
        Returns a list of all vehicles belonging to the user's company.
        """,
        responses={
            200: VehicleSerializer(many=True),
        }
    )
)
class VehicleListView(VehicleBaseView, generics.ListAPIView):
    """List all vehicles
    
    Returns a list of all vehicles belonging to the user's company.
    """
    serializer_class = VehicleSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            logger.info("[VEHICLE VIEWS] - Vehicles listed successfully")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error listing vehicles: {str(e)}")
            return Response(
                {"error": _("An error occurred while retrieving vehicles")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Vehicle'],
        operation_id='create_vehicle',
        summary='Create a vehicle',
        description="""
        Creates a new vehicle with the provided information.
        """,
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
            }
        }
    )
)
class VehicleCreateView(VehicleBaseView, generics.CreateAPIView):
    """Create a new vehicle
    
    Creates a new vehicle with the provided information.
    """
    serializer_class = VehicleSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("[VEHICLE VIEWS] - Vehicle created successfully")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            logger.warning(f"[VEHICLE VIEWS] - Invalid vehicle data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error creating vehicle: {str(e)}")
            return Response(
                {"error": _("An error occurred while creating the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicle'],
        operation_id='retrieve_vehicle',
        summary='Retrieve a vehicle',
        description="""
        Returns the details of a specific vehicle.
        """,
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
    )
)
class VehicleRetrieveView(VehicleBaseView, generics.RetrieveAPIView):
    """Retrieve a vehicle
    
    Returns detailed information about a specific vehicle.
    """
    serializer_class = VehicleSerializer
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[VEHICLE VIEWS] - Vehicle {instance.plate_number} retrieved successfully")
            return Response(serializer.data)
        except Vehicle.DoesNotExist:
            logger.warning(f"[VEHICLE VIEWS] - Vehicle with ID {kwargs.get('pk')} not found")
            return Response(
                {"error": _("Vehicle not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error retrieving vehicle {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while retrieving the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    put=extend_schema(
        tags=['Vehicle'],
        operation_id='update_vehicle',
        summary='Update a vehicle',
        description="""
        Updates a vehicle with the provided information.
        """,
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True
            )
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
    )
)
class VehicleUpdateView(VehicleBaseView, generics.UpdateAPIView):
    """Update a vehicle
    
    Updates a specific vehicle with the provided information.
    """
    serializer_class = VehicleSerializer
    lookup_field = 'pk'
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                logger.info(f"[VEHICLE VIEWS] - Vehicle {instance.plate_number} updated successfully")
                return Response(serializer.data)
            
            logger.warning(f"[VEHICLE VIEWS] - Invalid vehicle data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Vehicle.DoesNotExist:
            logger.warning(f"[VEHICLE VIEWS] - Vehicle with ID {kwargs.get('pk')} not found")
            return Response(
                {"error": _("Vehicle not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error updating vehicle {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while updating the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    delete=extend_schema(
        tags=['Vehicle'],
        operation_id='delete_vehicle',
        summary='Delete a vehicle',
        description="""
        Deletes a vehicle.
        """,
        parameters=[
            OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=str)
        ],
        responses={
            204: None,
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
class VehicleDestroyView(VehicleBaseView, generics.DestroyAPIView):
    """Delete a vehicle
    
    Deletes a specific vehicle.
    """
    serializer_class = VehicleSerializer
    lookup_field = 'pk'
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            plate_number = instance.plate_number
            instance.delete()
            logger.info(f"[VEHICLE VIEWS] - Vehicle {plate_number} deleted successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Vehicle.DoesNotExist:
            logger.warning(f"[VEHICLE VIEWS] - Vehicle with ID {kwargs.get('pk')} not found")
            return Response(
                {"error": _("Vehicle not found")},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error deleting vehicle {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"error": _("An error occurred while deleting the vehicle")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=['Vehicle'],
        operation_id='assign_driver',
        summary='Assign driver to vehicle',
        description="""
        Assigns a driver to a specific vehicle.
        """,
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the vehicle to assign driver to',
                required=True
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'driver_id': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'UUID of the driver to assign'
                    }
                },
                'required': ['driver_id']
            }
        },
        responses={
            200: VehicleSerializer,
            400: {
                'description': 'Invalid data',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Driver ID is required'
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
                'description': 'Vehicle or driver not found',
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Vehicle or driver not found'
                    }
                }
            }
        }
    )
)
class VehicleAssignDriverView(VehicleBaseView, generics.GenericAPIView):
    """Assign a driver to a vehicle
    
    Assigns a driver to a specific vehicle if the user has the appropriate permissions.
    """
    serializer_class = VehicleSerializer
    lookup_field = 'pk'
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # Get the driver ID from the request data
            driver_id = request.data.get('driver_id')
            if not driver_id:
                return Response(
                    {"error": _("Driver ID is required")},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            # Get the vehicle ID from the URL parameter
            vehicle_id = kwargs.get('pk')
        
            # Use the service to assign the driver
            from apps.vehicle.services.handlers import VehicleService
        
            vehicle_service = VehicleService()
            try:
                # The method assign_driver handles all validations and business rules
                vehicle = vehicle_service.assign_driver(
                    vehicle_id=vehicle_id,
                    driver_id=driver_id,
                    user=request.user
                )
            
                # Serialize and return the updated vehicle
                serializer = self.get_serializer(vehicle)
                return Response(serializer.data)
            except ValidationError as e:
                # The service already handles logs and validations
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Unexpected error in assign driver view: {str(e)}")
            return Response(
                {"error": _("An error occurred while assigning the driver")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )