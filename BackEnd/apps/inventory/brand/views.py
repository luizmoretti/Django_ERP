from typing import override
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
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
            employeer = user.employeer
            return Brand.objects.select_related(
                'created_by', 'companie'
            ).filter(companie=employeer.companie)
        except Brand.DoesNotExist:
            return Brand.objects.none()
    
    
@extend_schema_view(
    get=extend_schema(
        tags=["Inventory - Brands"],
        operation_id="list_brands",
        description="List all brands",
        request=BrandSerializer,
        responses={HTTP_200_OK: BrandSerializer(many=True)}
    )
)
class BrandListView(BaseBrandView, ListAPIView):
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"[BRAND VIEWS] - Brands list retrieved successfully")
        return Response(serializer.data)
    

@extend_schema_view(
    post=extend_schema(
        tags=["Inventory - Brands"],
        operation_id="create_brand",
        description="Create a new brand",
        request=BrandSerializer,
        responses={HTTP_200_OK: BrandSerializer}
    )
)
class BrandCreateView(BaseBrandView, CreateAPIView):
    def has_permission(self, request, view):
        try:
            if request.user.has_perm('add_brand'):
                return True
            return PermissionDenied
        except Exception as e:
            logger.error(f"[BRAND VIEWS] - Error checking permission: {str(e)}")
            return False
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"[BRAND VIEWS] - Brand created successfully: {serializer.data}")
        return Response(serializer.data, status=HTTP_200_OK)
    
@extend_schema_view(
    get=extend_schema(
        tags=["Inventory - Brands"],
        operation_id="retrieve_brand",
        description="Retrieve a specific brand by ID",
        parameters=[
            OpenApiParameter(
                name="id",
                description="ID of the brand to retrieve",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ],
        request=BrandSerializer,
        responses={HTTP_200_OK: BrandSerializer}
    )
)
class BrandRetrieveView(BaseBrandView, RetrieveAPIView):
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(f"[BRAND VIEWS] - Brand retrieved successfully: {serializer.data}")
        return Response(serializer.data)
    
@extend_schema_view(
    put=extend_schema(
        tags=["Inventory - Brands"],
        operation_id="update_brand",
        description="Update a specific brand by ID",
        parameters=[
            OpenApiParameter(
                name="id",
                description="ID of the brand to update",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ],
        request=BrandSerializer,
        responses={HTTP_200_OK: BrandSerializer}
    ),
    patch=extend_schema(
        tags=["Inventory - Brands"],
        operation_id="partial_update_brand",
        description="Partial update a specific brand by ID",
        parameters=[
            OpenApiParameter(
                name="id",
                description="ID of the brand to update",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ],
        request=BrandSerializer,
        responses={HTTP_200_OK: BrandSerializer}
    )
)
class BrandUpdateView(BaseBrandView, UpdateAPIView):
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        logger.info(f"[BRAND VIEWS] - Brand updated successfully: {serializer.data}")
        return Response(serializer.data)
    
    
@extend_schema_view(
    delete=extend_schema(
        tags=["Inventory - Brands"],
        operation_id="delete_brand",
        description="Delete a specific brand by ID",
        parameters=[
            OpenApiParameter(
                name="id",
                description="ID of the brand to delete",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ],
        request=BrandSerializer,
        responses={HTTP_204_NO_CONTENT: BrandSerializer}
    )
)
class BrandDeleteView(BaseBrandView, DestroyAPIView):
    lookup_field = 'pk'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        logger.info(f"[BRAND VIEWS] - Brand deleted successfully: {instance.name}")
        return Response(status=HTTP_204_NO_CONTENT)
    
    

    
    
