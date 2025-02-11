from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
import logging

from .models import Supplier
from .serializers import SupplierSerializer

logger = logging.getLogger(__name__)

class SupplierBaseView:
    """Base view for supplier operations
    
    Provides:
        - Common queryset filtering by company
        - Default permission class requiring authentication
        - Logging setup for supplier operations
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset filtered by user's company"""
        user = self.request.user
        try:
            employeer = user.employeer_user
            return self.queryset.select_related(
                'companie',
                'created_by'
            ).prefetch_related(
                'product_prices__product'
            ).filter(companie=employeer.companie)
        except Supplier.DoesNotExist:
            return self.queryset.none()

@extend_schema_view(
    get=extend_schema(
        summary='List all suppliers',
        description='Returns a list of all suppliers with their product prices',
        tags=['Inventory - Suppliers']
    )
)
class SupplierListView(SupplierBaseView, generics.ListAPIView):
    """List all suppliers"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

@extend_schema_view(
    post=extend_schema(
        summary='Create a new supplier',
        description='Create a new supplier with the provided data',
        tags=['Inventory - Suppliers']
    )
)
class SupplierCreateView(SupplierBaseView, generics.CreateAPIView):
    """Create a new supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def perform_create(self, serializer):
        supplier = serializer.save()
        logger.info(f"[SUPPLIER VIEWS] - Supplier {supplier.id} created successfully by {self.request.user}")

@extend_schema_view(
    get=extend_schema(
        summary='Retrieve a supplier',
        description='Get details of a specific supplier including product prices',
        tags=['Inventory - Suppliers']
    )
)
class SupplierRetrieveView(SupplierBaseView, generics.RetrieveAPIView):
    """Retrieve a supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

@extend_schema_view(
    put=extend_schema(
        summary='Update a supplier',
        description='Update all fields of a specific supplier',
        tags=['Inventory - Suppliers']
    ),
    patch=extend_schema(
        summary='Partially update a supplier',
        description='Update specific fields of a supplier',
        tags=['Inventory - Suppliers']
    )
)
class SupplierUpdateView(SupplierBaseView, generics.UpdateAPIView):
    """Update a supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def perform_update(self, serializer):
        supplier = serializer.save()
        logger.info(f"[SUPPLIER VIEWS] - Supplier {supplier.id} updated successfully by {self.request.user}")

@extend_schema_view(
    delete=extend_schema(
        summary='Delete a supplier',
        description='Delete a specific supplier',
        tags=['Inventory - Suppliers']
    )
)
class SupplierDestroyView(SupplierBaseView, generics.DestroyAPIView):
    """Delete a supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def perform_destroy(self, instance):
        logger.info(f"[SUPPLIER VIEWS] - Supplier {instance.id} deleted successfully by {self.request.user}")
        instance.delete()
