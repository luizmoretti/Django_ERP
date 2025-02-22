from django.shortcuts import render
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from .models import Vehicle
from .serializers import VehicleSerializer
import logging

logger = logging.getLogger(__name__)


class VehicleBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # Filtra apenas veículos da mesma empresa
            employeer = user.employeer
            return Vehicle.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except Vehicle.DoesNotExist:
            return Vehicle.objects.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Delivery - Vehicles'],
        operation_id='list_vehicles',
        summary='List all vehicles',
        description='Retrieve a list of all vehicles',
        responses={
            200: VehicleSerializer
        }
    )
)
class VehicleListView(VehicleBaseView, ListAPIView):
    serializer_class = VehicleSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[VEHICLE VIEWS] - Vehicles list retrieved successfully")
        return Response(serializer.data)
    
    
@extend_schema_view(
    post=extend_schema(
        tags=['Delivery - Vehicles'],
        operation_id='create_vehicle',
        summary='Create a new vehicle',
        description='Create a new vehicle',
        request={
            'application/json':{
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'plate': {'type': 'string'},
                    'driver': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'UUID of the employeer who drives the vehicle'
                    },
                    'drivers_license': {
                        'type': 'string',
                        'description': 'License of the driver'
                    },
                    'vehicle_maker': {'type': 'string'},
                    'vehicle_model': {'type': 'string'},
                    'vehicle_color': {'type': 'string'},
                    'type': {'type': 'string'},
                    'vehicle_is_active': {'type': 'boolean'}
                },
                'required': [
                    'name',
                    'plate',
                    'driver',
                    'drivers_license',
                    'vehicle_maker',
                    'vehicle_model',
                    'vehicle_color',
                    'type',
                ]
            }
        },
        responses={
            201: VehicleSerializer
        }
    )
)
class VehicleCreateView(VehicleBaseView, CreateAPIView):
    serializer_class = VehicleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"[VEHICLE VIEWS] - Vehicle created successfully")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

@extend_schema_view(
    put=extend_schema(
        tags=['Delivery - Vehicles'],
        operation_id='update_vehicle',
        summary='Update a vehicle',
        description='Update a vehicle',
        request={
            'application/json':{
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'plate': {'type': 'string'},
                    'driver': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'UUID of the employeer who drives the vehicle'
                    },
                    'drivers_license': {
                        'type': 'string',
                        'description': 'License of the driver'
                    },
                    'vehicle_maker': {'type': 'string'},
                    'vehicle_model': {'type': 'string'},
                    'vehicle_color': {'type': 'string'},
                    'type': {'type': 'string'},
                    'vehicle_is_active': {'type': 'boolean'}
                },
                'required': [
                    'name',
                    'plate',
                    'driver',
                    'drivers_license',
                    'vehicle_maker',
                    'vehicle_model',
                    'vehicle_color',
                    'type',
                    'vehicle_is_active'
                ]
            }
        },
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="The UUID of the vehicle to update",
                required=True
            )
        ],
        responses={
            200: VehicleSerializer,
            400: {
                'description': 'Error updating vehicle',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating vehicle'
                    }
                }
            },
            403: {
                'description': 'Forbidden',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Forbidden'
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=['Delivery - Vehicles'],
        operation_id='partial_update_vehicle',
        summary='Partial update a vehicle',
        description='Partial update a vehicle',
        request={
            'application/json':{
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'plate': {'type': 'string'},
                    'driver': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'UUID of the employeer who drives the vehicle'
                    },
                    'drivers_license': {'type': 'string'},
                    'vehicle_maker': {'type': 'string'},
                    'vehicle_model': {'type': 'string'},
                    'vehicle_color': {'type': 'string'},
                    'type': {'type': 'string'},
                    'vehicle_is_active': {'type': 'boolean'}
                },
                'required': ['driver']
            }
        },
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="The UUID of the vehicle to update",
                required=True
            )
        ],
        responses={
            200: VehicleSerializer,
            400: {
                'description': 'Error updating vehicle',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Error updating vehicle'
                    }
                }
            },
            403: {
                'description': 'Forbidden',
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Forbidden'
                    }
                }
            }
        }
    )
)
class VehicleUpdateView(VehicleBaseView, UpdateAPIView):
    serializer_class = VehicleSerializer

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"[VEHICLE VIEWS] - Vehicle updated successfully")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error updating vehicle: {str(e)}")
            return Response(
                {"detail": "Error updating vehicle"},
                status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema_view(
    get=extend_schema(
        tags=['Delivery - Vehicles'],
        summary="Retrieve a vehicle",
        description="Retrieve a vehicle by its ID",
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="The UUID of the vehicle to update",
                required=True
            )
        ],
        responses={
            200: VehicleSerializer,
            404: {
                'description': 'Vehicle not found',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},
                    'example': 'Vehicle not found'
                }
            }
        }
    )
)
class VehicleRetrieveView(VehicleBaseView, RetrieveAPIView):
    serializer_class = VehicleSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[VEHICLE VIEWS] - Vehicle retrieved successfully")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error retrieving vehicle: {str(e)}")
            return Response(
                {"detail": "Error retrieving vehicle, make sure the vehicle ID is correct"},
                status=status.HTTP_404_NOT_FOUND
            )
            

@extend_schema_view(
    delete=extend_schema(
        tags=['Delivery - Vehicles'],
        summary="Delete a vehicle",
        description="Delete a vehicle by its ID",
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description="The UUID of the vehicle to update",
                required=True
            )
        ],
        responses={
            200: {
                'description': 'Vehicle deleted successfully',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},
                    'example': 'Vehicle deleted successfully'
                }
            },
            500: {
                'description': 'Error deleting vehicle',
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},
                    'example': 'Error deleting vehicle'
                }
            }
        }
    )
)
class VehicleDeleteView(VehicleBaseView, DestroyAPIView):
    serializer_class = VehicleSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()            
            self.perform_destroy(instance)
            logger.info(f"[VEHICLE VIEWS] - Vehicle deleted successfully")
            return Response(
                {"detail": "Vehicle deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"[VEHICLE VIEWS] - Error deleting vehicle: {str(e)}")
            return Response(
                {"detail": "Error deleting vehicle"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )