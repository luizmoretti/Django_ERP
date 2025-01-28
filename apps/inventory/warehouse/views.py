from django.shortcuts import render
from .models import Warehouse
from .serializers import WarehouseSerializer
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
            employeer = user.employeer_user
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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[WAREHOUSE VIEWS] - Warehouses list retrieved successfully")
        return Response(serializer.data)


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
                    'items': {
                        'type': 'array', 
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product': {'type': 'string'},
                                'current_quantity': {'type': 'number'},
                            },
                        },
                    },
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
        serializer.save()
        logger.info(f"[WAREHOUSE VIEWS] - Warehouse created successfully")
        return Response(serializer.data, status=status.HTTP_201_CREATED)