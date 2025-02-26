from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point, LineString
from django.utils import timezone
import datetime

from apps.deliveries.models import Delivery
from apps.deliveries.tracking.models import DeliveryLocationUpdate, DeliveryRoute, DeliveryStatusUpdate

User = get_user_model()

class DeliveryTrackingModelsTests(TestCase):
    """
    Tests for the delivery tracking models.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create a company
        from apps.companies.models import Companie
        self.company = Companie.objects.create(
            name="Test Company",
            cnpj="12345678901234",
            email="test@company.com"
        )
        
        # Create a user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create an employee
        from apps.accounts.models import Employeer
        self.employee = Employeer.objects.create(
            user=self.user,
            companie=self.company,
            name="Test Employee",
            email="test@example.com"
        )
        
        # Create a customer
        from apps.companies.customers.models import Customer
        self.customer = Customer.objects.create(
            companie=self.company,
            name="Test Customer",
            email="customer@example.com"
        )
        
        # Create a delivery
        self.delivery = Delivery.objects.create(
            companie=self.company,
            customer=self.customer,
            driver=self.employee,
            origin="Test Origin",
            destiny="Test Destination",
            status="pending",
            estimated_delivery_time=timezone.now() + datetime.timedelta(hours=2)
        )
    
    def test_delivery_location_update(self):
        """Test creating a delivery location update."""
        # Create a location update
        location = Point(-46.633308, -23.550520)  # São Paulo
        location_update = DeliveryLocationUpdate.objects.create(
            delivery=self.delivery,
            vehicle=self.employee,
            location=location,
            accuracy=10.0,
            speed=60.0,
            heading=90.0
        )
        
        # Assert that the location update was created correctly
        self.assertEqual(location_update.delivery, self.delivery)
        self.assertEqual(location_update.vehicle, self.employee)
        self.assertEqual(location_update.location, location)
        self.assertEqual(location_update.accuracy, 10.0)
        self.assertEqual(location_update.speed, 60.0)
        self.assertEqual(location_update.heading, 90.0)
    
    def test_delivery_route(self):
        """Test creating a delivery route."""
        # Create route points
        points = [
            Point(-46.633308, -23.550520),  # São Paulo
            Point(-46.601465, -23.545634),
            Point(-46.456413, -23.510868),
            Point(-46.208878, -23.367068),
            Point(-43.174591, -22.911615)   # Rio de Janeiro
        ]
        
        # Create a LineString from the points
        route_geometry = LineString(points)
        
        # Create a route
        route = DeliveryRoute.objects.create(
            delivery=self.delivery,
            route_geometry=route_geometry,
            estimated_distance=500000,  # 500 km
            estimated_duration=21600,   # 6 hours
            estimated_arrival=timezone.now() + datetime.timedelta(hours=6),
            route_data={
                "waypoints": [
                    {"location": "São Paulo, SP"},
                    {"location": "Rio de Janeiro, RJ"}
                ],
                "mode": "driving"
            }
        )
        
        # Assert that the route was created correctly
        self.assertEqual(route.delivery, self.delivery)
        self.assertEqual(route.route_geometry, route_geometry)
        self.assertEqual(route.estimated_distance, 500000)
        self.assertEqual(route.estimated_duration, 21600)
        self.assertEqual(route.route_data["mode"], "driving")
    
    def test_delivery_status_update(self):
        """Test creating a delivery status update."""
        # Create a location update
        location = Point(-46.633308, -23.550520)  # São Paulo
        location_update = DeliveryLocationUpdate.objects.create(
            delivery=self.delivery,
            vehicle=self.employee,
            location=location,
            accuracy=10.0,
            speed=60.0,
            heading=90.0
        )
        
        # Create a status update
        status_update = DeliveryStatusUpdate.objects.create(
            delivery=self.delivery,
            status="in_transit",
            location_update=location_update,
            notes="Delivery is now in transit"
        )
        
        # Assert that the status update was created correctly
        self.assertEqual(status_update.delivery, self.delivery)
        self.assertEqual(status_update.status, "in_transit")
        self.assertEqual(status_update.location_update, location_update)
        self.assertEqual(status_update.notes, "Delivery is now in transit")
    
    def test_get_current_location(self):
        """Test the get_current_location method."""
        # Create multiple location updates
        location1 = Point(-46.633308, -23.550520)  # São Paulo
        location_update1 = DeliveryLocationUpdate.objects.create(
            delivery=self.delivery,
            vehicle=self.employee,
            location=location1,
            accuracy=10.0,
            speed=60.0,
            heading=90.0
        )
        
        # Create a second location update (more recent)
        location2 = Point(-46.601465, -23.545634)
        location_update2 = DeliveryLocationUpdate.objects.create(
            delivery=self.delivery,
            vehicle=self.employee,
            location=location2,
            accuracy=8.0,
            speed=65.0,
            heading=95.0
        )
        
        # Get the current location
        current_location = self.delivery.get_current_location()
        
        # Assert that the most recent location was returned
        self.assertEqual(current_location, location_update2)
    
    def test_get_current_status(self):
        """Test the get_current_status method."""
        # Create multiple status updates
        status_update1 = DeliveryStatusUpdate.objects.create(
            delivery=self.delivery,
            status="pending",
            notes="Delivery is pending"
        )
        
        # Create a second status update (more recent)
        status_update2 = DeliveryStatusUpdate.objects.create(
            delivery=self.delivery,
            status="in_transit",
            notes="Delivery is now in transit"
        )
        
        # Get the current status
        current_status = self.delivery.get_current_status()
        
        # Assert that the most recent status was returned
        self.assertEqual(current_status, status_update2)
    
    def test_get_eta(self):
        """Test the get_eta method."""
        # Create route points
        points = [
            Point(-46.633308, -23.550520),  # São Paulo
            Point(-46.601465, -23.545634),
            Point(-46.456413, -23.510868),
            Point(-46.208878, -23.367068),
            Point(-43.174591, -22.911615)   # Rio de Janeiro
        ]
        
        # Create a LineString from the points
        route_geometry = LineString(points)
        
        # Create a route
        estimated_arrival = timezone.now() + datetime.timedelta(hours=6)
        route = DeliveryRoute.objects.create(
            delivery=self.delivery,
            route_geometry=route_geometry,
            estimated_distance=500000,  # 500 km
            estimated_duration=21600,   # 6 hours
            estimated_arrival=estimated_arrival,
            route_data={
                "waypoints": [
                    {"location": "São Paulo, SP"},
                    {"location": "Rio de Janeiro, RJ"}
                ],
                "mode": "driving"
            }
        )
        
        # Create a location update at the start of the route
        location = Point(-46.633308, -23.550520)  # São Paulo
        DeliveryLocationUpdate.objects.create(
            delivery=self.delivery,
            vehicle=self.employee,
            location=location,
            accuracy=10.0,
            speed=60.0,  # 60 km/h
            heading=90.0
        )
        
        # Get the ETA
        eta = self.delivery.get_eta()
        
        # Assert that the ETA is the estimated arrival time from the route
        self.assertIsNotNone(eta)
        # The ETA should be close to the estimated arrival time
        # (we can't check exact equality due to calculation differences)
        self.assertTrue(abs((eta - estimated_arrival).total_seconds()) < 3600)  # Within 1 hour
