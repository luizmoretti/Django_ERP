from django.shortcuts import render
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from core.cache import cache_response, cache_get_or_set, get_cache_key, invalidate_cache_key
import hashlib
import json
import logging

from ..inflows.models import Inflow
from ..outflows.models import Outflow
from ..transfer.models import Transfer
from .serializers import MovementSerializer, MovementListSerializer
from .models import MovementType, MovementStatus

logger = logging.getLogger(__name__)

# Classe base com métodos comuns
class MovementBaseView:
    permission_classes = [IsAuthenticated]
    
    def get_cache_key(self, user, params=None):
        """Generate a unique cache key based on user and request parameters"""
        if params is None:
            params = {}
        
        # Create a string representation of the parameters
        param_str = json.dumps(params, sort_keys=True)
        
        # Create a hash of the parameters
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        
        return f'movements_list_{user.id}_{param_hash}'
    
    def _get_fresh_data(self, companie, movement_type=None, status=None, start_date=None, end_date=None):
        """Get fresh data from all movement sources"""
        logger.debug(f"[MOVEMENTS VIEW] Fetching fresh data with filters: type={movement_type}, status={status}")
        
        # Base queries with select_related for optimization
        inflows_query = (Inflow.objects
                        .filter(companie=companie)
                        .select_related('origin', 'destiny', 'created_by', 'updated_by'))
                        
        outflows_query = (Outflow.objects
                         .filter(companie=companie)
                         .select_related('origin', 'destiny', 'created_by', 'updated_by'))
                         
        transfers_query = (Transfer.objects
                          .filter(companie=companie)
                          .select_related('origin', 'destiny', 'created_by', 'updated_by'))
        
        # Apply status filter if provided
        if status:
            inflows_query = inflows_query.filter(status=status)
            outflows_query = outflows_query.filter(status=status)
            transfers_query = transfers_query.filter(status=status)
        
        # Apply date range filter if provided
        if start_date and end_date:
            try:
                date_filter = Q(created_at__range=[start_date, end_date])
                inflows_query = inflows_query.filter(date_filter)
                outflows_query = outflows_query.filter(date_filter)
                transfers_query = transfers_query.filter(date_filter)
            except ValueError:
                logger.warning("[MOVEMENTS VIEW] Invalid date format in movement filter")
        
        # Apply type filter if provided
        if movement_type:
            if movement_type == MovementType.INFLOW:
                outflows_query = outflows_query.none()
                transfers_query = transfers_query.none()
            elif movement_type == MovementType.OUTFLOW:
                inflows_query = inflows_query.none()
                transfers_query = transfers_query.none()
            elif movement_type == MovementType.TRANSFER:
                inflows_query = inflows_query.none()
                outflows_query = outflows_query.none()
        
        # Convert to movement objects
        movements = []
        
        # Process inflows
        for inflow in inflows_query:
            movement_data = {
                'id': inflow.id,
                'date': inflow.created_at,
                'type': MovementType.INFLOW,
                'origin': inflow.origin.name if inflow.origin else 'N/A',
                'destination': inflow.destiny.name if inflow.destiny else 'N/A',
                'status': inflow.status,
                'total_items': sum(item.quantity for item in inflow.items.all()),
                'total_value': sum(item.quantity * item.product.price for item in inflow.items.all()),
                'data': {
                    'inflow_id': str(inflow.id),
                    'items': [
                        {
                            'product': item.product.name,
                            'quantity': item.quantity,
                            'price': float(item.product.price)
                        } for item in inflow.items.all()
                    ]
                }
            }
            movements.append(movement_data)
        
        # Process outflows
        for outflow in outflows_query:
            movement_data = {
                'id': outflow.id,
                'date': outflow.created_at,
                'type': MovementType.OUTFLOW,
                'origin': outflow.origin.name if outflow.origin else 'N/A',
                'destination': outflow.destiny.full_name if outflow.destiny else 'N/A',
                'status': outflow.status,
                'total_items': sum(item.quantity for item in outflow.items.all()),
                'total_value': sum(item.quantity * item.product.price for item in outflow.items.all()),
                'data': {
                    'outflow_id': str(outflow.id),
                    'items': [
                        {
                            'product': item.product.name,
                            'quantity': item.quantity,
                            'price': float(item.product.price)
                        } for item in outflow.items.all()
                    ]
                }
            }
            movements.append(movement_data)
        
        # Process transfers
        for transfer in transfers_query:
            movement_data = {
                'id': transfer.id,
                'date': transfer.created_at,
                'type': MovementType.TRANSFER,
                'origin': transfer.origin.name if transfer.origin else 'N/A',
                'destination': transfer.destiny.name if transfer.destiny else 'N/A',
                'status': transfer.status,
                'total_items': sum(item.quantity for item in transfer.items.all()),
                'total_value': sum(item.quantity * item.product.price for item in transfer.items.all()),
                'data': {
                    'transfer_id': str(transfer.id),
                    'items': [
                        {
                            'product': item.product.name,
                            'quantity': item.quantity,
                            'price': float(item.product.price)
                        } for item in transfer.items.all()
                    ]
                }
            }
            movements.append(movement_data)
        
        # Sort by date, newest first
        movements.sort(key=lambda x: x['date'], reverse=True)
        
        logger.debug(f"[MOVEMENTS VIEW] Total movements: {len(movements)}")
        return movements


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Movements'],
        summary="List all movements",
        description="Get a paginated list of all inventory movements (inflows, outflows, transfers)",
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=['entry', 'exit', 'transfer'],
                description="Filter by movement type"
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=['pending', 'approved', 'rejected', 'cancelled', 'completed'],
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
    )
)
class MovementListView(ListAPIView, MovementBaseView):
    serializer_class = MovementListSerializer
    
    def get_queryset(self):
        """Get combined queryset from all movement types"""
        user = self.request.user
        logger.info(f"[MOVEMENTS VIEW] Fetching movements for user {user.id}")
        
        try:
            # Ensure user has an employeer
            if not hasattr(user, 'employeer'):
                logger.warning(f"[MOVEMENTS VIEW] User {user.id} has no employeer")
                return []
                
            employeer = user.employeer
            companie = employeer.companie
            
            # Get request parameters
            movement_type = self.request.query_params.get('type')
            status = self.request.query_params.get('status')
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            
            # Create cache key
            cache_key = self.get_cache_key(user, {
                'type': movement_type,
                'status': status,
                'start_date': start_date,
                'end_date': end_date
            })
            
            # Try to get from cache
            cached_result = cache_get_or_set(
                key=cache_key,
                default_func=lambda: self._get_fresh_data(
                    companie, movement_type, status, start_date, end_date
                ),
                timeout=300,  # 5 minutes
                cache_alias='default'
            )
            
            return cached_result
            
        except Exception as e:
            logger.error(f"[MOVEMENTS VIEW] Error fetching movements: {str(e)}", exc_info=True)
            return []


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Movements'],
        summary="Get movements from the last 7 days",
        responses={200: MovementListSerializer(many=True)}
    )
)
class MovementRecentView(GenericAPIView, MovementBaseView):
    serializer_class = MovementListSerializer
    
    def get(self, request):
        """Get movements from the last 7 days"""
        user = request.user
        
        if not hasattr(user, 'employeer'):
            return Response([], status=status.HTTP_200_OK)
        
        if getattr(self, 'swagger_fake_view', False):
            return Response([], status=status.HTTP_200_OK)
            
        companie = user.employeer.companie
        
        cache_key = f'movements:recent:{user.id}'
        
        def get_fresh_data():
            end_date = timezone.now()
            start_date = end_date - timedelta(days=7)
            
            return self._get_fresh_data(
                companie=companie,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
        
        movements = cache_get_or_set(
            key=cache_key,
            default_func=get_fresh_data,
            timeout=300,
            cache_alias='default'
        )
        
        serializer = MovementListSerializer(movements, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Movements'],
        summary="Get movement statistics",
        responses={200: OpenApiTypes.OBJECT}
    )
)
class MovementStatisticsView(GenericAPIView, MovementBaseView):
    def get(self, request):
        """Get movement statistics"""
        user = request.user
        
        if not hasattr(user, 'employeer'):
            return Response({
                'by_type': {},
                'by_status': {},
                'recent_count': 0
            }, status=status.HTTP_200_OK)
            
        companie = user.employeer.companie
        
        cache_key = f'movements:statistics:{user.id}'
        
        def get_fresh_data():
            movements = self._get_fresh_data(companie=companie)
            
            # Count by type
            type_counts = {
                MovementType.INFLOW: 0,
                MovementType.OUTFLOW: 0,
                MovementType.TRANSFER: 0
            }
            
            # Count by status
            status_counts = {status: 0 for status in MovementStatus.values}
            
            for movement in movements:
                type_counts[movement['type']] += 1
                status_counts[movement['status']] += 1
            
            # Recent activity
            recent_movements = len([
                m for m in movements 
                if m['date'] >= timezone.now() - timedelta(days=7)
            ])
            
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
        
        return Response(data)