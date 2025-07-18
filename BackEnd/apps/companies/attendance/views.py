from django.shortcuts import render
from .serializers import (
    AttendanceSerializer, 
    AttendanceClockInRequestSerializer, 
    AttendanceClockInOutResponseSerializer,
    PayrollPaymentInputSerializer,
    PayrollPaymentResponseSerializer
)
from django.db import transaction
from rest_framework.generics import (
    ListAPIView, CreateAPIView, 
    RetrieveAPIView, UpdateAPIView, 
    DestroyAPIView, GenericAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services.handlers import AttendanceService, PayrollService
from .services.validators import AttendanceBusinessValidator
from rest_framework.exceptions import ValidationError
import logging
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from .models import AttendanceRegister


logger = logging.getLogger(__name__)

class AttendanceBase:
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            if hasattr(user, 'employeer'):
                employeer = user.employeer
                base_queryset = super().get_queryset()
                return base_queryset.select_related(
                    'employee', 'employee__companie'
                ).filter(employee__companie=employeer.companie)
            return AttendanceRegister.objects.none()
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error getting queryset: {str(e)}")
            return AttendanceRegister.objects.none()

@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Attendance"],
        summary="Get a list of attendance registers",
        description="Retrieve a list of attendance registers for the authenticated user's company.",
        responses={
            200: AttendanceSerializer(many=True)
        }
    )
)
class AttendanceRegisterListView(AttendanceBase, ListAPIView):
    serializer_class = AttendanceSerializer
    queryset = AttendanceRegister.objects.all()
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.info("[ATTENDANCE VIEWS] - Attendance registers list retrieved successfully")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error listing attendance registers: {str(e)}")
            return Response(
                {"detail": "Error retrieving attendance registers"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
@extend_schema_view(
    post=extend_schema(
        tags=["Companies - Attendance"],
        summary="Create an attendance register",
        description="""Create a new attendance register for the authenticated user's company.
        
For employees with payment type "Hour":
```json
{
    "employee": "550e8400-e29b-41d4-a716-446655440000",
    "work_data": [
        {
            "clock_in": "2025-01-31T07:00:00",
            "clock_out": "2025-01-31T17:00:00"
        },
        {
            "clock_in": "2025-01-30T07:00:00",
            "clock_out": "2025-01-30T17:00:00"
        }
    ]
}
```

For employees with payment type "Day":
```json
{
    "employee": "550e8400-e29b-41d4-a716-446655440000",
    "work_data": [
        {
            "date": "2025-01-31",
            "clock_in": "07:00:00",
            "clock_out": "17:00:00"
        },
        {
            "date": "2025-01-30",
            "clock_in": "07:00:00",
            "clock_out": "17:00:00"
        }
    ]
}
```""",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "employee": {
                        "type": "string",
                        "format": "uuid",
                        "description": "UUID of the employee"
                    },
                    "work_data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "title": "Hourly Payment",
                                    "description": "Data structure for hourly-paid employees",
                                    "properties": {
                                        "clock_in": {
                                            "type": "string",
                                            "format": "date-time",
                                            "description": "Clock in date and time (ISO format)"
                                        },
                                        "clock_out": {
                                            "type": "string",
                                            "format": "date-time",
                                            "description": "Clock out date and time (ISO format)"
                                        }
                                    },
                                    "required": ["clock_in", "clock_out"]
                                },
                                {
                                    "title": "Daily Payment",
                                    "description": "Data structure for daily-paid employees",
                                    "properties": {
                                        "date": {
                                            "type": "string",
                                            "format": "date",
                                            "description": "Work date (YYYY-MM-DD)"
                                        },
                                        "clock_in": {
                                            "type": "string",
                                            "format": "time",
                                            "description": "Clock in time (HH:MM:SS)"
                                        },
                                        "clock_out": {
                                            "type": "string",
                                            "format": "time",
                                            "description": "Clock out time (HH:MM:SS)"
                                        }
                                    },
                                    "required": ["date", "clock_in", "clock_out"]
                                }
                            ]
                        },
                        "description": "List of work entries. Structure depends on employee payment type"
                    }
                },
                "required": ["employee", "work_data"]
            }
        },
        responses={
            201: AttendanceSerializer,
            400: {
                "description": "Bad Request",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Error creating attendance register"
                    }
                }
            }
        }
    )
)
class AttendanceRegisterCreateView(CreateAPIView, AttendanceBase):
    serializer_class = AttendanceSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"[ATTENDANCE VIEWS] - Attendance register {serializer.data['id']} created successfully")
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error creating attendance register: {str(e)}")
            return Response(
                {"detail": "Error creating attendance register"},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        tags=["Companies - Attendance"],
        summary="Get an attendance register",
        description="Retrieve an attendance register for the authenticated user's company.",
        responses={
            200: AttendanceSerializer,
            404: {
                "description": "Not Found",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Attendance register not found"
                    }
                }
            },
            500: {
                "description": "Internal Server Error",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Error retrieving attendance register"
                    }
                }
            }
        }
    )
)
class AttendanceRegisterRetrieveView(RetrieveAPIView, AttendanceBase):
    serializer_class = AttendanceSerializer
    queryset = AttendanceRegister.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[ATTENDANCE VIEWS] - Attendance register {instance.id} retrieved successfully")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error retrieving attendance register: {str(e)}")
            return Response(
                {"detail": "Error retrieving attendance register"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    put=extend_schema(
        tags=["Companies - Attendance"],
        summary="Update an attendance register",
        description="Update an attendance register for the authenticated user's company.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "employee": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "work_data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "clock_in": {
                                    "type": "string",
                                    "format": "date-time"
                                },
                                "clock_out": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            }
                        }
                    }
                }
            }
        },
        responses={
            200: AttendanceSerializer,
            400: {
                "description": "Bad Request",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Error updating attendance register"
                    }
                }
            }
        }
    ),
    patch=extend_schema(
        tags=["Companies - Attendance"],
        summary="Partial update an attendance register",
        description="Partial update an attendance register for the authenticated user's company.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "employee": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "work_data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "clock_in": {
                                    "type": "string",
                                    "format": "date-time"
                                },
                                "clock_out": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            }
                        }
                    }
                }
            }
        },
        responses={
            200: AttendanceSerializer,
            400: {
                "description": "Bad Request",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Error updating attendance register"
                    }
                }
            }
        }
    )
)
class AttendanceRegisterUpdateView(UpdateAPIView, AttendanceBase):
    serializer_class = AttendanceSerializer
    queryset = AttendanceRegister.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f"[ATTENDANCE VIEWS] - Attendance register {instance.id} updated successfully")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error updating attendance register: {str(e)}")
            return Response(
                {"detail": "Error updating attendance register"},
                status=status.HTTP_400_BAD_REQUEST
            )
            


@extend_schema_view(
    delete=extend_schema(
        tags=["Companies - Attendance"],
        summary="Delete an attendance register",
        description="Delete an attendance register for the authenticated user's company.",
        responses={
            200: {
                "description": "Attendance register deleted successfully",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Attendance register deleted successfully"
                    }
                }
            },
            400: {
                "description": "Bad Request",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Error deleting attendance register"
                    }
                }
            },
            500: {
                "description": "Server Error",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Error deleting attendance register"
                    }
                }
            }
        }
    )
)
class AttendanceRegisterDestroyView(DestroyAPIView, AttendanceBase):
    serializer_class = AttendanceSerializer
    queryset = AttendanceRegister.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            logger.info(f"[ATTENDANCE VIEWS] - Attendance register deleted successfully")
            return Response(
                {"detail": "Attendance register deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error deleting attendance register: {str(e)}")
            return Response(
                {"detail": "Error deleting attendance register"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        tags=["Companies - Attendance"],
        operation_id="attendance_clock_inout",
        summary="Record clock in/out using access code",
        description="""
        Register clock in or clock out for an employee using their access code.
        The system will automatically determine whether to register clock in or clock out
        based on the employee's current status.
        """,
        request=AttendanceClockInRequestSerializer,
        responses={
            200: AttendanceClockInOutResponseSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': 'Invalid access code'
                    }
                }
            }
        }
    )
)
class AttendanceClockInOutView(GenericAPIView, AttendanceBase):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceClockInRequestSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            access_code = serializer.validated_data['access_code']
            
            attendance_service = AttendanceService()
            result = attendance_service.clock_inout_with_code(access_code)
            
            # Validar a resposta com o serializer de resposta
            response_serializer = AttendanceClockInOutResponseSerializer(data=result)
            if response_serializer.is_valid():
                logger.info(f"[ATTENDANCE VIEWS] - Clock in/out processed successfully via API")
                return Response(response_serializer.data)
            else:
                logger.error(f"[ATTENDANCE VIEWS] - Invalid response format: {response_serializer.errors}")
                return Response(
                    {"detail": "Error formatting response data"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except ValidationError as e:
            logger.error(f"[ATTENDANCE VIEWS] - Validation error in clock in/out: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error processing clock in/out: {str(e)}")
            return Response(
                {"detail": "Error processing clock in/out request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    post=extend_schema(
        tags=["Companies - Attendance"],
        summary="Process payroll payment",
        description="Process payment for a pending payroll",
        request=PayrollPaymentInputSerializer,
        responses={
            200: PayrollPaymentResponseSerializer,
            400: {
                "description": "Bad Request",
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Erro ao processar o pagamento"
                    }
                }
            }
        }
    )
)
class PayrollPaymentView(GenericAPIView, AttendanceBase):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollPaymentInputSerializer
    
    def post(self, request, payroll_id):
        try:
            # Validar dados de entrada
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            
            # Processar pagamento
            payroll_service = PayrollService()
            result = payroll_service.process_payment(
                payroll_id, 
                validated_data,
                request.user
            )
            
            # Formatar resposta
            response_data = {
                'success': True,
                'payment_details': result['payment_details']
            }
            
            logger.info(f"[ATTENDANCE VIEWS] - Payroll payment processed successfully", 
                       extra={'payroll_id': payroll_id})
            
            return Response(
                response_data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            logger.warning(f"[ATTENDANCE VIEWS] - Validation error processing payment: {str(e)}", 
                          extra={'payroll_id': payroll_id})
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"[ATTENDANCE VIEWS] - Error processing payment: {str(e)}", 
                        exc_info=True, extra={'payroll_id': payroll_id})
            return Response(
                {'detail': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )