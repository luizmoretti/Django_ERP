from django.shortcuts import render
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from .models import Brand
from .serializers import BrandSerializer
import logging

logger = logging.getLogger(__name__)

class BaseBrandView:
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employeer = user.employeer_user
            return Brand.objects.select_related(
                'created_by', 'companie'
            ).filter(is_active=True, companie=employeer.companie)
        except Brand.DoesNotExist:
            return Brand.objects.none()
    
    
