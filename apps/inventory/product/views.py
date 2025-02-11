from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
import logging

from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)

class ProductBaseView:
    """Base view for product operations
    
    Provides:
        - Common queryset filtering by company
        - Default permission class requiring authentication
        - Logging setup for product operations
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset filtered by user's company"""
        user = self.request.user
        try:
            employeer = user.employeer_user
            return self.queryset.select_related(
                'companie',
                'created_by',
                'updated_by',
                'brand',
                'category'
            ).prefetch_related(
                'skus'
            ).filter(companie=employeer.companie)
        except Product.DoesNotExist:
            return self.queryset.none()

@extend_schema_view(
    get=extend_schema(
        summary='List all products',
        description='Returns a list of all products with their SKUs',
        tags=['Inventory - Products']
    )
)
class ProductListView(ProductBaseView, generics.ListAPIView):
    """List all products"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@extend_schema_view(
    post=extend_schema(
        summary='Create a new product',
        description='Create a new product with the provided data',
        tags=['Inventory - Products']
    )
)
class ProductCreateView(ProductBaseView, generics.CreateAPIView):
    """Create a new product"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        product = serializer.save()
        logger.info(f"[PRODUCT VIEWS] - Product {product.id} created successfully by {self.request.user}")

@extend_schema_view(
    get=extend_schema(
        summary='Retrieve a product',
        description='Get details of a specific product including SKUs',
        tags=['Inventory - Products']
    )
)
class ProductRetrieveView(ProductBaseView, generics.RetrieveAPIView):
    """Retrieve a product"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@extend_schema_view(
    put=extend_schema(
        summary='Update a product',
        description='Update all fields of a specific product',
        tags=['Inventory - Products']
    ),
    patch=extend_schema(
        summary='Partially update a product',
        description='Update specific fields of a product',
        tags=['Inventory - Products']
    )
)
class ProductUpdateView(ProductBaseView, generics.UpdateAPIView):
    """Update a product"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_update(self, serializer):
        product = serializer.save()
        logger.info(f"[PRODUCT VIEWS] - Product {product.id} updated successfully by {self.request.user}")

@extend_schema_view(
    delete=extend_schema(
        summary='Delete a product',
        description='Delete a specific product',
        tags=['Inventory - Products']
    )
)
class ProductDestroyView(ProductBaseView, generics.DestroyAPIView):
    """Delete a product"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_destroy(self, instance):
        logger.info(f"[PRODUCT VIEWS] - Product {instance.id} deleted successfully by {self.request.user}")
        instance.delete()
