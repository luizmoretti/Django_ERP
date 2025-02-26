from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.contrib.gis.geos import Point
from .models import DeliveryLocationUpdate, DeliveryRoute, DeliveryStatusUpdate
from .serializers import (
    DeliveryLocationUpdateSerializer,
    DeliveryRouteSerializer,
    DeliveryStatusUpdateSerializer
)
from apps.deliveries.models import Delivery
import logging

logger = logging.getLogger(__name__)

class DeliveryTrackingViewSet(viewsets.ViewSet):
    """
    ViewSet for delivery tracking.
    Provides endpoints to update and query tracking information.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns the queryset of deliveries filtered by the user's company.
        """
        user = self.request.user
        employeer = user.employeer
        return Delivery.objects.filter(companie=employeer.companie)
    
    @action(detail=True, methods=['get'])
    def current_location(self, request, pk=None):
        """
        Returns the current location of a delivery.
        """
        try:
            delivery = self.get_queryset().get(pk=pk)
            location = DeliveryLocationUpdate.objects.filter(
                delivery=delivery
            ).order_by('-created_at').first()
            
            if not location:
                return Response(
                    {"detail": "No location available for this delivery."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = DeliveryLocationUpdateSerializer(location)
            return Response(serializer.data)
        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting current location: {str(e)}")
            return Response(
                {"detail": f"Error getting location: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def location_history(self, request, pk=None):
        """
        Returns the location history of a delivery.
        """
        try:
            delivery = self.get_queryset().get(pk=pk)
            
            # Filtering parameters
            start_time = request.query_params.get('start_time')
            end_time = request.query_params.get('end_time')
            limit = int(request.query_params.get('limit', 100))
            
            # Filter locations
            locations = DeliveryLocationUpdate.objects.filter(delivery=delivery)
            
            if start_time:
                locations = locations.filter(created_at__gte=start_time)
            if end_time:
                locations = locations.filter(created_at__lte=end_time)
            
            # Limit results and sort
            locations = locations.order_by('-created_at')[:limit]
            
            serializer = DeliveryLocationUpdateSerializer(locations, many=True)
            return Response(serializer.data)
        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting location history: {str(e)}")
            return Response(
                {"detail": f"Error getting history: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """
        Updates the location of a delivery.
        """
        try:
            delivery = self.get_queryset().get(pk=pk)
            
            # Extract data from request
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            accuracy = request.data.get('accuracy')
            speed = request.data.get('speed')
            heading = request.data.get('heading')
            
            # Validate data
            if latitude is None or longitude is None:
                return Response(
                    {"detail": "Latitude and longitude are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create geographic point
            location = Point(float(longitude), float(latitude))
            
            # Create location update
            location_update = DeliveryLocationUpdate.objects.create(
                delivery=delivery,
                vehicle=delivery.driver,
                location=location,
                accuracy=accuracy,
                speed=speed,
                heading=heading
            )
            
            serializer = DeliveryLocationUpdateSerializer(location_update)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating location: {str(e)}")
            return Response(
                {"detail": f"Error updating location: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Updates the status of a delivery.
        """
        try:
            delivery = self.get_queryset().get(pk=pk)
            
            # Extract data from request
            status_value = request.data.get('status')
            notes = request.data.get('notes')
            
            # Validate data
            if not status_value:
                return Response(
                    {"detail": "Status is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get current location, if available
            location_update = DeliveryLocationUpdate.objects.filter(
                delivery=delivery
            ).order_by('-created_at').first()
            
            # Update delivery status
            delivery.status = status_value
            delivery.save(update_fields=['status', 'updated_at'])
            
            # Create status update
            status_update = DeliveryStatusUpdate.objects.create(
                delivery=delivery,
                status=status_value,
                location_update=location_update,
                notes=notes
            )
            
            serializer = DeliveryStatusUpdateSerializer(status_update)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            return Response(
                {"detail": f"Error updating status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def route(self, request, pk=None):
        """
        Returns the planned route for a delivery.
        """
        try:
            delivery = self.get_queryset().get(pk=pk)
            
            try:
                route = DeliveryRoute.objects.get(delivery=delivery)
                serializer = DeliveryRouteSerializer(route)
                return Response(serializer.data)
            except DeliveryRoute.DoesNotExist:
                return Response(
                    {"detail": "No route available for this delivery."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Delivery.DoesNotExist:
            return Response(
                {"detail": "Delivery not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting route: {str(e)}")
            return Response(
                {"detail": f"Error getting route: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )