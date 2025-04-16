from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .service.product_services import ProductServices
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
import logging

from .models import Product
from .serializers import ProductSerializer, HomeDepotActionResultSerializer

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
            employeer = user.employeer
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
        
@extend_schema_view(
    post=extend_schema(
        tags=['Inventory - Products'],
        summary='Execute Home Depot actions',
        description='Execute Home Depot actions (search or update) for a product',
        parameters=[
            OpenApiParameter(
                name="action",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Action to execute: 'search' to find and save Home Depot Product in Store ID, 'update' to update product info",
                enum=['search', 'update']
            )
        ],
        responses={
            200: HomeDepotActionResultSerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        }
    )
)
class HomeDepotActionsView(APIView):
    """View for Home Depot related actions"""
    permission_classes = [IsAuthenticated]
    serializer_class = HomeDepotActionResultSerializer
    
    def post(self, request, action, pk=None):
        """Execute Home Depot actions
        
        Args:
            request: Request object
            action: Action to execute (search or update)
            pk: Product ID (optional, if not provided will execute for all products)
            
        Returns:
            Response with action results
        """
        try:
            if action not in ['search', 'update']:
                return Response(
                    {"error": "Invalid action. Must be 'search' or 'update'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # If no ID, run for all company products
            if not pk:
                products = ProductServices.get_all_products()
            else:
                products = [{"id": pk}]
                
            results = []
            for product in products:
                if action == 'search':
                    result = ProductServices.search_and_save_home_depot_id(product['id'])
                else:  # update
                    result = ProductServices.update_product_from_home_depot(product['id'])
                    
                results.append({
                    "product_id": product['id'],
                    **result
                })
                
            # Counting successes and errors
            success_count = sum(1 for r in results if r['status'] == 'success')
            error_count = sum(1 for r in results if r['status'] == 'error')
            
            response_data = {
                "success_count": success_count,
                "error_count": error_count,
                "results": results
            }
            serializer = self.serializer_class(response_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error executing Home Depot action: {str(e)}")
            return Response(
                {"error": f"Error executing action: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
