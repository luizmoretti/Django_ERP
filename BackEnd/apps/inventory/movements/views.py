from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.companies.employeers.models import Employeer
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from core.cache import cache_response, cache_get_or_set, get_cache_key, invalidate_cache_key
import hashlib
import json
import logging
from .serializers import MovementSerializer

from ..inflows.models import Inflow
from ..inflows.serializers import InflowSerializer
from ..outflows.models import Outflow
from ..outflows.serializers import OutflowSerializer
from ..transfer.models import Transfer
from ..transfer.serializers import TransferSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory - Movements'],
        summary="List all movements",
        description="List all movements.",
        responses={200: MovementSerializer(many=True)},
    )
)
class MovementListView(ListAPIView):
    """
    List all movements.
    """
    serializer_class = MovementSerializer
    permission_classes = [IsAuthenticated]
    queryset = Inflow.objects.none()
    
    def get_queryset(self):
        user = self.request.user
        logger.info(f"[MOVEMENTS VIEW] all movements listed successfully")
        
        try:
            base_inflow_query = (
                Inflow.objects.select_related('origin', 'destiny', 'created_by', 'companie')
            )
            
            base_outflow_query = (
                Outflow.objects.select_related('origin', 'destiny', 'created_by', 'companie')
            )
            
            base_transfer_query = (
                Transfer.objects.select_related('origin', 'destiny', 'created_by', 'companie')
            )
            
            logger.debug(f"Total inflows: {base_inflow_query.count()}")
            logger.debug(f"Total outflows: {base_outflow_query.count()}")
            logger.debug(f"Total transfers: {base_transfer_query.count()}")
            
            #Check if user_type is [Manager, Admin, or Owner] if so, return all movements
            if user.user_type in ['Manager', 'Admin', 'Owner']:
                inflow = list(base_inflow_query.all())
                outflow = list(base_outflow_query.all())
                transfer = list(base_transfer_query.all())
                movements = sorted(
                    inflow + outflow + transfer,
                    key=lambda x: x.created_at,
                    reverse=True
                )
                logger.debug(f"[MOVEMENTS VIEW] Total movements: {len(movements)}")
                return movements
            # For regular employees, return only movements they created
            else:
                try:
                    employeer = Employeer.objects.get(user=user)
                    
                    # Filter movements created by this employee
                    inflow = list(base_inflow_query.filter(created_by=employeer, companie=employeer.companie))
                    outflow = list(base_outflow_query.filter(created_by=employeer, companie=employeer.companie))
                    transfer = list(base_transfer_query.filter(created_by=employeer, companie=employeer.companie))
                    
                    logger.debug(f"[MOVEMENTS VIEW] Employee {employeer.name} - Inflows: {len(inflow)}, Outflows: {len(outflow)}, Transfers: {len(transfer)}")
                    
                    # Combine and sort movements
                    movements = sorted(
                        inflow + outflow + transfer,
                        key=lambda x: x.created_at,
                        reverse=True
                    )
                    return movements
                except Employeer.DoesNotExist:
                    logger.warning(f"[MOVEMENTS VIEW] User {user.email} has no employeer profile")
                    return []
                except Exception as e:
                    logger.error(f"[MOVEMENTS VIEW] Error getting movements: {str(e)}")
                    return []
        except Exception as e:
            logger.error(f"[MOVEMENTS VIEW] Error getting movements: {str(e)}")
            return []
