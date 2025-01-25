from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .services import HRService
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import logging
from .models import HR
from .serializers import HRSerializer
from .services import PaymentService

logger = logging.getLogger(__name__)

class BaseHRView:
    """
    Base view class with common configurations for HR views.
    
    Provides:
        - Common queryset with optimized related field loading
        - Default permission class requiring authentication
        - Logging setup for HR operations
        - Company-based filtering
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employeer = user.employeer_user
            return HR.objects.select_related(
                'employeer', 'made_by'
            ).filter(employeer__companie=employeer.companie)
        except:
            return HR.objects.none()


# HR Views
@extend_schema(
    description=_("List all HR records"),
    tags=["HR - Human Resources"],
    responses={200: HRSerializer(many=True)}
)
class HRListView(BaseHRView, generics.ListAPIView):
    """
    API endpoint for listing HR records.
    
    Authentication:
    - Requires valid authentication token
    
    Permissions:
    - User must be authenticated
    
    Note:
    - Only shows records from the user's company
    """
    serializer_class = HRSerializer


@extend_schema(
    description=_("Create a new HR record"),
    tags=["HR - Human Resources"],
    request=HRSerializer,
    responses={
        201: HRSerializer,
        400: {"description": _("Invalid data provided")}
    },
    examples=[
        OpenApiExample(
            "Create HR Example - Hourly Payment",
            value={
                "employeer": "uuid",
                "payd_by_hour": True,
                "hourly_salary": 50.00,
                "payment_interval": "weekly",
                "payment_business_day": 2,
                "worked_hours": [
                    {
                        "date": "2025-01-21",
                        "start_time": "08:00:00",
                        "end_time": "17:00:00"
                    }
                ]
            },
            description=_("Example of creating an HR record for hourly payment with worked hours")
        ),
        OpenApiExample(
            "Create HR Example - Daily Payment",
            value={
                "employeer": "uuid",
                "payd_by_day": True,
                "daily_salary": 150.00,
                "payment_interval": "biweekly",
                "payment_business_day": 2,
                "worked_days": ["2025-01-21", "2025-01-20"]
            },
            description=_("Example of creating an HR record for daily payment with worked days")
        )
    ]
)
class HRCreateView(BaseHRView, generics.CreateAPIView):
    """
    API endpoint for creating HR records.
    
    Authentication:
    - Requires valid authentication token
    
    Permissions:
    - User must be authenticated
    
    Note:
    - Record will be associated with user's company
    """
    serializer_class = HRSerializer

    def perform_create(self, serializer):
        """
        Override perform_create to set the made_by field.
        
        The company validation and assignment is handled by the serializer.
        """
        try:
            serializer.save(made_by=self.request.user)
        except Exception as e:
            logger.error(f"[VIEW] - Error creating HR record: {str(e)}")
            raise


@extend_schema(
    description=_("Retrieve a specific HR record"),
    tags=["HR - Human Resources"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description=_("HR record unique identifier")
        )
    ],
    responses={
        200: HRSerializer,
        404: {"description": _("HR record not found")}
    }
)
class HRRetrieveView(BaseHRView, generics.RetrieveAPIView):
    """
    API endpoint for retrieving HR records.
    
    Authentication:
    - Requires valid authentication token
    
    Permissions:
    - User must be authenticated
    
    Note:
    - Only retrieves records from user's company
    """
    serializer_class = HRSerializer
    


@extend_schema(
    description=_("Update a specific HR record"),
    tags=["HR - Human Resources"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description=_("HR record unique identifier")
        )
    ],
    request=HRSerializer,
    responses={
        200: HRSerializer,
        400: {"description": _("Invalid data provided")},
        404: {"description": _("HR record not found")}
    },
    examples=[
        OpenApiExample(
            "Update HR Example",
            value={
                "payd_by_hour": True,
                "hourly_salary": 50.00,
                "payment_interval": "weekly",
                "payment_business_day": 2,
                "worked_hours": [
                    {
                        "date": "2025-01-21",
                        "start_time": "08:00:00",
                        "end_time": "17:00:00"
                    }
                ]
            },
            description=_("Example of updating an HR record with new worked hours")
        )
    ]
)
class HRUpdateView(BaseHRView, generics.UpdateAPIView):
    """
    API endpoint for updating HR records.
    
    Authentication:
    - Requires valid authentication token
    
    Permissions:
    - User must be authenticated
    
    Note:
    - Only updates records from user's company
    """
    serializer_class = HRSerializer


@extend_schema(
    description=_("Delete a specific HR record"),
    tags=["HR - Human Resources"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description=_("HR record unique identifier")
        )
    ],
    responses={
        204: {"description": _("HR record deleted successfully")},
        404: {"description": _("HR record not found")}
    }
)
class HRDestroyView(BaseHRView, generics.DestroyAPIView):
    """
    API endpoint for deleting HR records.
    
    Authentication:
    - Requires valid authentication token
    
    Permissions:
    - User must be authenticated
    
    Note:
    - Only deletes records from user's company
    """
    serializer_class = HRSerializer
    
@extend_schema(
    description=_("Process payment for a specific HR record"),
    tags=["HR - Human Resources"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description=_("HR record unique identifier")
        )
    ],
    responses={
        200: {"description": _("Payment processed successfully")},
        404: {"description": _("HR record not found")}
    }
)
class HRProcessPaymentView(BaseHRView, generics.GenericAPIView):
    """
    API endpoint for processing payments for HR records.
    
    Authentication:
    - Requires valid authentication token
    
    Permissions:
    - User must be authenticated
    
    Note:
    - Only processes payments for records from user's company
    - Processes payments based on selected PK
    """
    serializer_class = HRSerializer
    lookup_url_kwarg = 'pk'
    
    def get_object(self):
        """
        Retrieve the HR instance to process payment.
        """
        queryset = self.get_queryset()
        pk = self.kwargs.get(self.lookup_url_kwarg)
        
        try:
            hr = queryset.get(pk=pk)
            self.check_object_permissions(self.request, hr)
            return hr
        except HR.DoesNotExist:
            raise NotFound(_("HR record not found"))
    
    def post(self, request, *args, **kwargs):
        try:
            hr = self.get_object()
            PaymentService.process_payment(hr)
            return Response(
                {"message": _("Payment processed successfully")},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"[VIEW] - Error processing payment for HR record: {str(e)}")
            raise