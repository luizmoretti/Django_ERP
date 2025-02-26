from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime
from .models import DeliveryLocationUpdate, DeliveryStatusUpdate, DeliveryRoute
from apps.deliveries.models import Delivery
import googlemaps
from django.conf import settings
from .signals_utils import get_formatted_address, calculate_distance, get_destination_coordinates, calculate_eta_with_google_maps, calculate_eta_with_speed
from django.contrib.gis.geos import LineString, Point
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=DeliveryLocationUpdate)
def update_delivery_eta(sender, instance, created, **kwargs):
    """
    Updates the estimated delivery time when a new location update is received.
    Uses Google Maps API or speed-based calculation to estimate arrival time.
    """
    if created:
        try:
            delivery = instance.delivery
            
            # Get the coordinates of the destination
            destination_coords = get_destination_coordinates(delivery)
            
            if not destination_coords:
                logger.warning(f"Could not determine destination coordinates for delivery {delivery.number}")
                return
                
            # Check if we have a route associated with the delivery
            has_route = hasattr(delivery, 'route') and delivery.route
            
            # Calculate ETA using Google Maps API (more accurate)
            current_coords = (instance.location.y, instance.location.x)  # (latitude, longitude)
            duration_seconds, distance_meters = calculate_eta_with_google_maps(current_coords, destination_coords)
            
            if duration_seconds:
                # Calculate the new ETA
                new_eta = timezone.now() + timezone.timedelta(seconds=duration_seconds)
                
                # Update the delivery
                delivery.estimated_delivery_time = new_eta
                
                # If we have a route, update the route information
                if has_route:
                    route = delivery.route
                    route.estimated_duration = timezone.timedelta(seconds=duration_seconds)
                    route.estimated_distance = distance_meters / 1000.0  # Converter for km
                    route.estimated_arrival = new_eta
                    route.save(update_fields=['estimated_duration', 'estimated_distance', 'estimated_arrival', 'updated_at'])
                
                delivery.save(update_fields=['estimated_delivery_time', 'updated_at'])
                logger.info(f"Updated ETA for delivery {delivery.number} using Google Maps API")
            
            # If we couldn't calculate with Google Maps and have speed information, use the alternative method
            elif instance.speed and instance.speed > 0:
                # Calculate ETA with base on the current speed
                duration_seconds = calculate_eta_with_speed(instance.location, destination_coords, instance.speed)
                
                if duration_seconds:
                    # Calculate the new ETA
                    new_eta = timezone.now() + timezone.timedelta(seconds=duration_seconds)
                    
                    # Update the delivery
                    delivery.estimated_delivery_time = new_eta
                    delivery.save(update_fields=['estimated_delivery_time', 'updated_at'])
                    
                    # If we have a route, update the route information
                    if has_route:
                        # Calculate approximate distance
                        current_coords = (instance.location.y, instance.location.x)
                        distance_km = calculate_distance(current_coords, destination_coords)
                        
                        route = delivery.route
                        route.estimated_duration = timezone.timedelta(seconds=duration_seconds)
                        route.estimated_distance = distance_km
                        route.estimated_arrival = new_eta
                        route.save(update_fields=['estimated_duration', 'estimated_distance', 'estimated_arrival', 'updated_at'])
                    
                    logger.info(f"Updated ETA for delivery {delivery.number} using speed-based calculation")
                else:
                    logger.warning(f"Could not calculate ETA for delivery {delivery.number}")
            else:
                logger.warning(f"Insufficient data to update ETA for delivery {delivery.number}")
                
            # Notify if the ETA changed significantly (more than 15 minutes)
            if 'new_eta' in locals() and delivery.estimated_delivery_time:
                from django.db.models import F
                from django.db.models.functions import Abs
                
                # Verify if the difference is greater than 15 minutes
                time_diff = abs((new_eta - delivery.estimated_delivery_time).total_seconds())
                if time_diff > 900:  # 15 minutes in seconds
                    # add code here to send notifications
                    # about significant ETA changes to the customer if needed
                    pass
                
        except Exception as e:
            logger.error(f"Error updating delivery ETA: {str(e)}")

@receiver(post_save, sender=DeliveryStatusUpdate)
def handle_status_change(sender, instance, created, **kwargs):
    """
    Handles various actions when a delivery status changes.
    """
    if created:
        try:
            delivery = instance.delivery
            status = instance.status
            
            # Handle different status changes
            if status == 'in_transit' and not delivery.actual_start_time:
                # If the delivery has started, record the start time
                delivery.actual_start_time = timezone.now()
                delivery.save(update_fields=['actual_start_time', 'updated_at'])
                logger.info(f"Recorded start time for delivery {delivery.number}")
                
            elif status == 'delivered' and not delivery.actual_delivery_time:
                # If the delivery is complete, record the delivery time
                delivery.actual_delivery_time = timezone.now()
                delivery.save(update_fields=['actual_delivery_time', 'updated_at'])
                logger.info(f"Recorded delivery time for delivery {delivery.number}")
                
        except Exception as e:
            logger.error(f"Error handling status change: {str(e)}")
            
            
@receiver(post_save, sender=Delivery)
def initialize_delivery_status(sender, instance, created, **kwargs):
    """
    Initialize the delivery status when a new delivery is created.
    """
    if created and not instance.status:
        instance.status = 'pending'  # Use 'pending' for consistency with tracking
        instance.save(update_fields=['status'])
        logger.info(f"Initialized status for delivery {instance.number}")
        

@receiver(post_save, sender=Delivery)
def create_initial_status_update(sender, instance, created, **kwargs):
    """
    Create an initial status update record when a new delivery is created.
    """
    if created:
        # Avoid infinite recursion by verifying if a status update already exists
        if not instance.status_updates.exists():
            DeliveryStatusUpdate.objects.create(
                delivery=instance,
                status='pending',  # Use lowercase for consistency with tracking
                notes='Initial status created automatically'
            )
            

@receiver(post_save, sender=Delivery)
def create_delivery_route(sender, instance, created, **kwargs):
    """
    Create a delivery route when a new delivery is created with origin and destination.
    Uses Google Maps Directions API to calculate route information.
    """
    if created and instance.origin and instance.destiny:
        # Verify if a route already exists to avoid duplication
        if not hasattr(instance, 'route'):
            try:
                # Initialize the Google Maps client with your API key
                gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                
                # Get the coordinates of origin (warehouse) and destination (customer)
                # or complete addresses that can be geocoded
                
                # Method 1: If you already have coordinates
                if hasattr(instance.origin, 'latitude') and hasattr(instance.origin, 'longitude') and \
                   hasattr(instance.destiny, 'latitude') and hasattr(instance.destiny, 'longitude'):
                    origin = f"{instance.origin.latitude},{instance.origin.longitude}"
                    destination = f"{instance.destiny.latitude},{instance.destiny.longitude}"
                # Method 2: If have complete addresses
                else:
                    # Format addresses
                    origin_address = get_formatted_address(instance.origin)
                    destination_address = get_formatted_address(instance.destiny)
                    
                    origin = origin_address
                    destination = destination_address
                
                # Make a request to the directions API
                directions_result = gmaps.directions(
                    origin,
                    destination,
                    mode="driving",  # It can be "driving", "walking", "bicycling" or "transit"
                    departure_time=timezone.now()  # Consider traffic
                )
                
                if directions_result:
                    # Extract route information
                    route = directions_result[0]
                    leg = route['legs'][0]
                    
                    # Distance in meters, converted to km
                    distance_meters = leg['distance']['value']
                    distance_km = distance_meters / 1000.0
                    
                    # Duration in seconds, converted to timedelta
                    duration_seconds = leg['duration']['value']
                    duration = datetime.timedelta(seconds=duration_seconds)
                    
                    # Estimated arrival time
                    estimated_arrival = timezone.now() + duration
                    
                    # Extract the route geometry (polyline)
                    polyline = route['overview_polyline']['points']
                    
                    # Decodificar o polyline para obter os pontos da rota
                    from googlemaps.convert import decode_polyline
                    points = decode_polyline(polyline)
                    
                    # Create a LineString with the route points
                    # Note: the Google Maps returns points as (lat, lng), but the GeoDjango expects (lng, lat)
                    route_points = [(point['lng'], point['lat']) for point in points]
                    route_geometry = LineString(route_points)
                    
                    # Additional route data
                    route_data = {
                        'steps': leg['steps'],
                        'start_address': leg['start_address'],
                        'end_address': leg['end_address'],
                        'distance_text': leg['distance']['text'],
                        'duration_text': leg['duration']['text'],
                        'polyline': polyline
                    }
                    
                    # Criar o objeto DeliveryRoute
                    DeliveryRoute.objects.create(
                        delivery=instance,
                        estimated_distance=distance_km,
                        estimated_duration=duration,
                        estimated_arrival=estimated_arrival,
                        route_geometry=route_geometry,
                        route_data=route_data
                    )
                    
                    logger.info(f"Created route for delivery {instance.number} using Google Maps API")
                else:
                    logger.warning(f"No route found for delivery {instance.number}")
                    
            except Exception as e:
                logger.error(f"Error creating delivery route with Google Maps: {str(e)}")
                
                # Fallback to dummy values in case of error
                estimated_duration = datetime.timedelta(hours=2)
                estimated_arrival = timezone.now() + estimated_duration
                
                DeliveryRoute.objects.create(
                    delivery=instance,
                    estimated_distance=50.0,  # km (example)
                    estimated_duration=estimated_duration,
                    estimated_arrival=estimated_arrival
                )
                logger.info(f"Created fallback route for delivery {instance.number}")