from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)
from .models import JobsTypeSchedullerRegister
from .serializers import JobsTypeSchedullerRegisterSerializer
import logging

logger = logging.getLogger(__name__)

class JobsTypeSchedullerRegisterBaseView:
    """Base view for JobsTypeSchedullerRegister operations."""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # Verify if it's swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                return JobsTypeSchedullerRegister.objects.none()

            employeer = user.employeer
            # Optimize query with select_related
            return JobsTypeSchedullerRegister.objects.select_related(
                'companie',
                'created_by',
                'updated_by'
            ).filter(companie=employeer.companie)
        except Exception:
            logger.error(f"[SCHEDULLER VIEWS] - Error retrieving JobsTypeSchedullerRegister queryset")
            return JobsTypeSchedullerRegister.objects.none()


@extend_schema_view(
    get=extend_schema(
        tags=['Scheduller'],
        operation_id='list_jobs_type_scheduller',
        summary='List all job types for scheduller',
        description="""
        Retrieves a list of all job types available for scheduling.
        Results are filtered by the user's company.
        """
    )
)
class JobsTypeSchedullerRegisterListView(JobsTypeSchedullerRegisterBaseView, ListAPIView):
    """View for listing job types for scheduller."""
    serializer_class = JobsTypeSchedullerRegisterSerializer
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        logger.info(f"[SCHEDULLER VIEWS] - JobsTypeSchedullerRegister listed successfully")
        return response


@extend_schema_view(
    post=extend_schema(
        tags=['Scheduller'],
        operation_id='create_jobs_type_scheduller',
        summary='Create a new job type for scheduller',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
                'required': ['name'],
            }
        },
        description="""
        Creates a new job type for scheduling with the provided information.
        """
    )
)
class JobsTypeSchedullerRegisterCreateView(JobsTypeSchedullerRegisterBaseView, CreateAPIView):
    """View for creating new job types for scheduller."""
    serializer_class = JobsTypeSchedullerRegisterSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        logger.info(f"[SCHEDULLER VIEWS] - JobsTypeSchedullerRegister created successfully")
        return response


@extend_schema_view(
    get=extend_schema(
        tags=['Scheduller'],
        operation_id='retrieve_jobs_type_scheduller',
        summary='Retrieve a specific job type',
        description="""
        Retrieves detailed information about a specific job type for scheduling.
        """
    )
)
class JobsTypeSchedullerRegisterRetrieveView(JobsTypeSchedullerRegisterBaseView, RetrieveAPIView):
    """View for retrieving a specific job type."""
    serializer_class = JobsTypeSchedullerRegisterSerializer
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        logger.info(f"[SCHEDULLER VIEWS] - JobsTypeSchedullerRegister retrieved successfully")
        return response


@extend_schema_view(
    put=extend_schema(
        tags=['Scheduller'],
        operation_id='update_jobs_type_scheduller',
        summary='Update a job type',
        description="""
        Updates a job type for scheduling with the provided information.
        """
    ),
    patch=extend_schema(
        tags=['Scheduller'],
        operation_id='partial_update_jobs_type_scheduller',
        summary='Partially update a job type',
        description="""
        Partially updates a job type for scheduling with the provided information.
        """
    )
)
class JobsTypeSchedullerRegisterUpdateView(JobsTypeSchedullerRegisterBaseView, UpdateAPIView):
    """View for updating job types."""
    serializer_class = JobsTypeSchedullerRegisterSerializer
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        logger.info(f"[SCHEDULLER VIEWS] - JobsTypeSchedullerRegister updated successfully")
        return response


@extend_schema_view(
    delete=extend_schema(
        tags=['Scheduller'],
        operation_id='delete_jobs_type_scheduller',
        summary='Delete a job type',
        description="""
        Deletes a job type for scheduling.
        """
    )
)
class JobsTypeSchedullerRegisterDestroyView(JobsTypeSchedullerRegisterBaseView, DestroyAPIView):
    """View for deleting job types."""
    serializer_class = JobsTypeSchedullerRegisterSerializer
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        logger.info(f"[SCHEDULLER VIEWS] - JobsTypeSchedullerRegister deleted successfully")
        return response