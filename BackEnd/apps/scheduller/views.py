from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)
from .models import Scheduller, JobsTypeSchedullerRegister
from .serializers import JobsTypeSchedullerRegisterSerializer
import logging

class JobsTypeSchedullerRegisterBaseView:
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        user = self.request.user
        try:
            #Verify if its swagger fake view
            if getattr(self, 'swagger_fake_view', False):
                return JobsTypeSchedullerRegister.objects.none()

            employeer = user.employeer
            return JobsTypeSchedullerRegister.objects.select_related(
                'companie'
            ).filter(companie=employeer.companie)
        except JobsTypeSchedullerRegister.DoesNotExist:
            return JobsTypeSchedullerRegister.objects.none()

class JobsTypeSchedullerRegisterViewSet(JobsTypeSchedullerRegisterBaseView, viewsets.ModelViewSet):
    serializer_class = JobsTypeSchedullerRegisterSerializer
    queryset = JobsTypeSchedullerRegister.objects.all()
    
        
    