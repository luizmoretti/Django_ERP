from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from core.cache import cache_response, cache_get_or_set, get_cache_key, invalidate_cache_key
import hashlib
import json

from .models import Movement, MovementType, MovementStatus
from .serializers import MovementSerializer, MovementListSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@extend_schema_view(
    list=extend_schema(
        tags=['Inventory - Movements'],
        summary="List all movements",
        description="Get a paginated list of all inventory movements",
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=MovementType.values,
                description="Filter by movement type"
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=MovementStatus.values,
                description="Filter by movement status"
            ),
            OpenApiParameter(
                name="start_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Start date for filtering (YYYY-MM-DD)"
            ),
            OpenApiParameter(
                name="end_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="End date for filtering (YYYY-MM-DD)"
            )
        ]
    ),
    retrieve=extend_schema(
        tags=['Inventory - Movements'],
        summary="Retrieve movement",
        description="Get detailed information about a specific movement",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="Movement UUID"
            )
        ]
    )
)
class MovementViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MovementSerializer
    lookup_field = 'id'
    
    def get_fresh_data(self, **kwargs):
        """Get fresh data without using cache"""
        queryset = Movement.objects.filter(companie=self.request.user.employeer.companie)
        
        # Filter by movement type
        movement_type = self.request.query_params.get('type')
        if movement_type in MovementType.values:
            queryset = queryset.filter(movement_type=movement_type)
            
        # Filter by status
        status = self.request.query_params.get('status')
        if status in MovementStatus.values:
            queryset = queryset.filter(status=status)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            try:
                queryset = queryset.filter(date__range=[start_date, end_date])
            except ValueError:
                logger.warning("Invalid date format in movement filter")
                
        return queryset.select_related('created_by', 'updated_by')
    
    def list(self, request, *args, **kwargs):
        """List movements with caching"""
        def get_fresh_data():
            queryset = self.get_fresh_data()
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"[MOVEMENT VIEWS] - Movements list retrieved successfully (cache miss)")
            return serializer.data
        
        # Get cache key for list view
        cache_key = get_cache_key(
            key_type='movements',
            id='list'
        )
        
        data = cache_get_or_set(
            key=cache_key,
            default_func=get_fresh_data,
            timeout=300,  # 5 minutes
            cache_alias='default'
        )
        
        logger.info(f"[MOVEMENT VIEWS] - Movements list retrieved successfully (cache hit)")
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve movement with caching"""
        movement_id = kwargs['id']
        
        def get_fresh_data():
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[MOVEMENT VIEWS] - Movement {movement_id} retrieved successfully (cache miss)")
            return serializer.data
        
        # Get cache key for detail view
        cache_key = get_cache_key(
            key_type='movements',
            id=movement_id
        )
        # invalidate_cache_key(cache_key, cache_alias='default')
        
        data = cache_get_or_set(
            key=cache_key,
            default_func=get_fresh_data,
            timeout=300,  # 5 minutes
            cache_alias='default'
        )
        
        logger.info(f"[MOVEMENT VIEWS] - Movement {movement_id} retrieved successfully (cache hit)")
        return Response(data)
    
    def get_queryset(self):
        """Get queryset without caching"""
        return self.get_fresh_data()
    
    def get_object(self):
        """Get single object without caching"""
        return super().get_object()
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return MovementListSerializer
        return MovementSerializer
    
    @extend_schema(
        tags=['Inventory - Movements'],
        summary="Get movements from the last 7 days",
        responses={200: MovementListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get movements from the last 7 days"""
        cache_key = f'movements:recent:GET:/api/v1/movements/recent/'
        
        def get_fresh_data():
            end_date = timezone.now()
            start_date = end_date - timedelta(days=7)
            
            movements = self.get_fresh_data().filter(
                date__range=[start_date, end_date]
            )
            
            serializer = MovementListSerializer(movements, many=True)
            logger.info(f"[MOVEMENT VIEWS] - Recent movements retrieved successfully (cache miss)")
            return serializer.data
        
        data = cache_get_or_set(
            key=cache_key,
            default_func=get_fresh_data,
            timeout=300,
            cache_alias='default'
        )
        
        logger.info(f"[MOVEMENT VIEWS] - Recent movements retrieved successfully (cache hit)")
        return Response(data)
    
    @extend_schema(
        tags=['Inventory - Movements'],
        summary="Get movement statistics",
        responses={200: OpenApiTypes.OBJECT}
    )    
    @action(detail=False, methods=['get'])
    def statistics(self, request) -> object:
        """Get movement statistics"""
        cache_key = f'movements:statistics:GET:/api/v1/movements/statistics/'
        
        def get_fresh_data():
            queryset = self.get_fresh_data()
            
            # Count by type
            type_counts = {
                type: queryset.filter(type=type).count()
                for type in MovementType.values
            }
            
            # Count by status
            status_counts = {
                status: queryset.filter(status=status).count()
                for status in MovementStatus.values
            }
            
            # Recent activity
            recent_movements = queryset.filter(
                date__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            logger.info(f"[MOVEMENT VIEWS] - Movement statistics retrieved successfully (cache miss)")
            return {
                'by_type': type_counts,
                'by_status': status_counts,
                'recent_count': recent_movements
            }
        
        data = cache_get_or_set(
            key=cache_key,
            default_func=get_fresh_data,
            timeout=300,
            cache_alias='default'
        )
        
        logger.info(f"[MOVEMENT VIEWS] - Movement statistics retrieved successfully (cache hit)")
        return Response(data)
