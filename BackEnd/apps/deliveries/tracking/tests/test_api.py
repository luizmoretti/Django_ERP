from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.deliveries.models import Delivery
from apps.deliveries.tracking.models import DeliveryLocationUpdate, DeliveryStatusUpdate

User = get_user_model()

class DeliveryTrackingAPITests(TestCase):
    """
    Tests for the delivery tracking API endpoints.
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
            status="pending"
        )
        
        # Create a location update
        self.location = Point(-46.633308, -23.550520)  # São Paulo
        self.location_update = DeliveryLocationUpdate.objects.create(
            delivery=self.delivery,
            vehicle=self.employee,
            location=self.location,
            accuracy=10.0,
            speed=60.0,
            heading=90.0
        )
        
        # Create a status update
        self.status_update = DeliveryStatusUpdate.objects.create(
            delivery=self.delivery,
            status="in_transit",
            location_update=self.location_update,
            notes="Delivery is now in transit"
        )
        
        # Set up the API client
        self.client = APIClient()
        
        # Get a token for the user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        
        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
    
    def test_get_current_location(self):
        """Test getting the current location of a delivery."""
        url = reverse("delivery-tracking-current-location", args=[self.delivery.id])
        response = self.client.get(url)
        
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert that the response contains the correct data
        self.assertEqual(response.data["delivery_id"], str(self.delivery.id))
        self.assertEqual(response.data["latitude"], self.location.y)
        self.assertEqual(response.data["longitude"], self.location.x)
        self.assertEqual(response.data["accuracy"], 10.0)
        self.assertEqual(response.data["speed"], 60.0)
        self.assertEqual(response.data["heading"], 90.0)
    
    def test_get_location_history(self):
        """Test getting the location history of a delivery."""
        # Create additional location updates
        location2 = Point(-46.601465, -23.545634)
        location_update2 = DeliveryLocationUpdate.objects.create(
            delivery=self.delivery,
            vehicle=self.employee,
            location=location2,
            accuracy=8.0,
            speed=65.0,
            heading=95.0
        )
        
        url = reverse("delivery-tracking-location-history", args=[self.delivery.id])
        response = self.client.get(url)
        
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert that the response contains the correct data
        self.assertEqual(len(response.data), 2)  # Two location updates
        
        # Check the most recent location update (should be first in the list)
        self.assertEqual(response.data[0]["delivery_id"], str(self.delivery.id))
        self.assertEqual(response.data[0]["latitude"], location2.y)
        self.assertEqual(response.data[0]["longitude"], location2.x)
    
    def test_create_location_update(self):
        """Test creating a new location update."""
        url = reverse("delivery-tracking-location-update", args=[self.delivery.id])
        data = {
            "latitude": -23.510868,
            "longitude": -46.456413,
            "accuracy": 7.5,
            "speed": 70.0,
            "heading": 100.0
        }
        
        response = self.client.post(url, data)
        
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert that the response contains the correct data
        self.assertEqual(response.data["delivery_id"], str(self.delivery.id))
        self.assertEqual(response.data["latitude"], -23.510868)
        self.assertEqual(response.data["longitude"], -46.456413)
        self.assertEqual(response.data["accuracy"], 7.5)
        self.assertEqual(response.data["speed"], 70.0)
        self.assertEqual(response.data["heading"], 100.0)
        
        # Assert that the location update was saved to the database
        self.assertEqual(DeliveryLocationUpdate.objects.count(), 3)
    
    def test_create_status_update(self):
        """Test creating a new status update."""
        url = reverse("delivery-tracking-status-update", args=[self.delivery.id])
        data = {
            "status": "delivered",
            "notes": "Delivery has been completed"
        }
        
        response = self.client.post(url, data)
        
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert that the response contains the correct data
        self.assertEqual(response.data["delivery_id"], str(self.delivery.id))
        self.assertEqual(response.data["status"], "delivered")
        self.assertEqual(response.data["notes"], "Delivery has been completed")
        
        # Assert that the status update was saved to the database
        self.assertEqual(DeliveryStatusUpdate.objects.count(), 2)
        
        # Assert that the delivery status was updated
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, "delivered")
    
    def test_get_eta(self):
        """Test getting the ETA of a delivery."""
        url = reverse("delivery-tracking-eta", args=[self.delivery.id])
        response = self.client.get(url)
        
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert that the response contains the ETA data
        self.assertIn("eta", response.data)
        
        # The ETA might be None if no route is defined, which is fine for this test
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the API."""
        # Create a new user without permissions
        new_user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="newpassword"
        )
        
        # Get a token for the new user
        refresh = RefreshToken.for_user(new_user)
        token = str(refresh.access_token)
        
        # Create a new client with the new user's token
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        # Try to access the current location
        url = reverse("delivery-tracking-current-location", args=[self.delivery.id])
        response = client.get(url)
        
        # Assert that the response is forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
