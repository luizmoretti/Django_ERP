from django.shortcuts import render
from .models import Warehouse
from .serializers import WarehouseSerializer
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.cache import (
    cache_response, 
    invalidate_cache_key, 
    get_cache_key,
    cache_get_or_set
)
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView
)
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class WareHouseBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # Verify if it is a swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                return Warehouse.objects.none()
            
            employeer = user.employeer
            return Warehouse.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except Warehouse.DoesNotExist:
            return Warehouse.objects.none()
        


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Warehouse'],
        operation_id='List Warehouses',
        summary='List all warehouses',
        description='Retrieve a list of all warehouses for authenticated user',
        responses={
            200: WarehouseSerializer
        }
    )
)
class WarehouseListView(WareHouseBaseView, ListAPIView):
    serializer_class = WarehouseSerializer
    
    def list(self, request, *args, **kwargs):
        cache_key = 'warehouse_list:GET:/api/v1/warehouse/'
        
        def get_fresh_data():
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"[WAREHOUSE VIEWS] - Warehouses list retrieved successfully (cache miss)")
            return serializer.data
        
        # Get the latest updated_at from all warehouses to use as cache version
        latest_warehouse = Warehouse.objects.order_by('-updated_at').first()
        cache_version = int(latest_warehouse.updated_at.timestamp()) if latest_warehouse else 0
        
        data = cache_get_or_set(
            key=cache_key,
            default_func=get_fresh_data,
            timeout=300,
            cache_alias='default'
        )
        
        logger.info(f"[WAREHOUSE VIEWS] - Warehouses list retrieved successfully (cache hit)")
        return Response(data, headers={'Cache-Version': str(cache_version)})

@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Warehouse'],
        operation_id='Create Warehouse',
        summary='Create a new warehouse',
        description='Create a new warehouse for authenticated user',
        request={
            'application/json':{
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'limit': {'type': 'number'},
                },
                'required': ['name']
            }
        },
        responses={
            201: WarehouseSerializer
        }
    )
)
class WarehouseCreateView(WareHouseBaseView, CreateAPIView):
    serializer_class = WarehouseSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.save()
        logger.info(f"[WAREHOUSE VIEWS] - Warehouse created successfully")
        
        # Invalidate warehouse list cache
        invalidate_cache_key('warehouse_list:GET:/api/v1/warehouse/', cache_alias='drywall')
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Warehouse'],
        operation_id='retrieve_warehouse',
        summary='Retrieve a warehouse',
        description='Retrieve a warehouse',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='Warehouse UUID',
                required=True
            )
        ],
        responses={
            200: WarehouseSerializer
        }
    )
)
class WarehouseRetrieveView(WareHouseBaseView, RetrieveAPIView):
    serializer_class = WarehouseSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            cache_key = f'warehouse_detail:GET:/api/v1/warehouse/{instance.id}/'
            
            def get_fresh_data():
                serializer = self.get_serializer(instance)
                logger.info(f"[WAREHOUSE VIEWS] - Warehouse {instance.id} retrieved successfully (cache miss)")
                return serializer.data
            
            # Use cache_get_or_set with version based on updated_at
            cache_version = int(instance.updated_at.timestamp())
            data = cache_get_or_set(
                key=cache_key,
                default_func=get_fresh_data,
                timeout=300,
                cache_alias='default'
            )
            
            logger.info(f"[WAREHOUSE VIEWS] - Warehouse {instance.id} retrieved successfully (cache hit)")
            return Response(data, headers={'Cache-Version': str(cache_version)})
            
        except Exception as e:
            logger.error(f"[WAREHOUSE VIEWS] - Error retrieving warehouse: {str(e)}")
            return Response(
                {"detail": "Error retrieving warehouse"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    put=extend_schema(
        tags=['Inventory - Warehouse'],
        operation_id='update_warehouse',
        summary='Update a warehouse',
        description='Update a warehouse',
        request={
            'application/json':{
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'limit': {'type': 'number'},
                },
                'required': ['name']
            }
        },
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='Warehouse UUID',
                required=True
            )
        ],
        responses={
            200: WarehouseSerializer
        }
    ),
    patch=extend_schema(
        tags=['Inventory - Warehouse'],
        operation_id='partial_update_warehouse',
        summary='Partial update a warehouse',
        description='Partial update a warehouse',
        request={
            'application/json':{
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Warehouse 1'},
                    'limit': {'type': 'number', 'example': 1000}
                }
            }
        },
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='Warehouse UUID',
                required=True
            )
        ],
        responses={
            200: WarehouseSerializer
        }
    )
)
class WarehouseUpdateView(WareHouseBaseView, UpdateAPIView):
    serializer_class = WarehouseSerializer
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                warehouse = serializer.save()
                
                # Invalidar todos os caches relacionados
                cache_keys = [
                    'warehouse_list:GET:/api/v1/warehouse/',  # warehouse list
                    f'warehouse_detail:GET:/api/v1/warehouse/{instance.id}/',  # warehouse detail
                    get_cache_key('warehouse', id=instance.id),  # Object cache
                    f'warehouse_total_quantity:{instance.__class__.__name__}:{instance.id}',  # Quantity cache
                ]
                
                for key in cache_keys:
                    invalidate_cache_key(key, cache_alias='default')
                    logger.info(f"[WAREHOUSE VIEWS] - Cache invalidated for key: {key}")
                
                logger.info(f"[WAREHOUSE VIEWS] - Warehouse {instance.id} updated successfully")
                return Response(serializer.data)
                
        except Exception as e:
            logger.error(f"[WAREHOUSE VIEWS] - Error updating warehouse: {str(e)}")
            return Response(
                {"detail": f"Error updating warehouse: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
@extend_schema_view(
    delete=extend_schema(
        tags=['Inventory - Warehouse'],
        operation_id='delete_warehouse',
        summary='Delete a warehouse',
        description='Delete a warehouse',
        parameters=[
            OpenApiParameter(
                name='id',
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.UUID,
                description='Warehouse UUID',
                required=True
            )
        ],
        responses={
            200: WarehouseSerializer
        }
    )
)
class WarehouseDeleteView(WareHouseBaseView, DestroyAPIView):
    serializer_class = WarehouseSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            warehouse_id = instance.id
            self.perform_destroy(instance)
            logger.info(f"[WAREHOUSE VIEWS] - Warehouse deleted successfully")
            
            # Invalidate all related caches
            invalidate_cache_key('warehouse_list:GET:/api/v1/warehouse/', cache_alias='drywall')
            invalidate_cache_key(f'warehouse_detail:GET:/api/v1/warehouse/{warehouse_id}/', cache_alias='drywall')
            invalidate_cache_key(get_cache_key('warehouse', id=warehouse_id), cache_alias='drywall')
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"[WAREHOUSE VIEWS] - Error deleting warehouse: {str(e)}")
            return Response(
                {"detail": f"Error deleting warehouse: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
