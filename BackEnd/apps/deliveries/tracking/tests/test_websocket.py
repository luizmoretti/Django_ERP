from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken
import json
import pytest

from apps.deliveries.models import Delivery
from apps.deliveries.tracking.models import DeliveryLocationUpdate, DeliveryStatusUpdate
from apps.deliveries.tracking.routing import websocket_urlpatterns
from apps.deliveries.tracking.middleware import DeliveryTokenAuthMiddlewareStack

User = get_user_model()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class DeliveryTrackingWebsocketTests(TestCase):
    """
    Tests for the delivery tracking WebSocket functionality.
    """
    
    async def test_connect_with_valid_token(self):
        """
        Test connecting to the WebSocket with a valid token.
        """
        # Create a user
        user = await self.create_user()
        
        # Create a delivery
        delivery = await self.create_delivery(user)
        
        # Get a valid token
        token = await self.get_token(user)
        
        # Create a communicator with the token
        application = DeliveryTokenAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
        communicator = WebsocketCommunicator(
            application,
            f"/ws/delivery/tracking/{delivery.id}/",
            headers=[(b"authorization", f"Bearer {token}".encode())]
        )
        
        # Connect
        connected, _ = await communicator.connect()
        
        # Assert that the connection was successful
        self.assertTrue(connected)
        
        # Disconnect
        await communicator.disconnect()
    
    async def test_connect_with_invalid_token(self):
        """
        Test connecting to the WebSocket with an invalid token.
        """
        # Create a user
        user = await self.create_user()
        
        # Create a delivery
        delivery = await self.create_delivery(user)
        
        # Use an invalid token
        token = "invalid_token"
        
        # Create a communicator with the token
        application = DeliveryTokenAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
        communicator = WebsocketCommunicator(
            application,
            f"/ws/delivery/tracking/{delivery.id}/",
            headers=[(b"authorization", f"Bearer {token}".encode())]
        )
        
        # Connect
        connected, _ = await communicator.connect()
        
        # Assert that the connection was rejected
        self.assertFalse(connected)
    
    async def test_location_update(self):
        """
        Test sending a location update through the WebSocket.
        """
        # Create a user
        user = await self.create_user()
        
        # Create a delivery
        delivery = await self.create_delivery(user)
        
        # Get a valid token
        token = await self.get_token(user)
        
        # Create a communicator with the token
        application = DeliveryTokenAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
        communicator = WebsocketCommunicator(
            application,
            f"/ws/delivery/tracking/{delivery.id}/",
            headers=[(b"authorization", f"Bearer {token}".encode())]
        )
        
        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send a location update
        await communicator.send_json_to({
            'type': 'location_update',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'accuracy': 10.0,
            'speed': 20.0,
            'heading': 90.0
        })
        
        # Receive the response
        response = await communicator.receive_json_from()
        
        # Assert that the response is correct
        self.assertEqual(response['type'], 'location_update')
        self.assertEqual(response['delivery_id'], str(delivery.id))
        self.assertEqual(response['latitude'], 40.7128)
        self.assertEqual(response['longitude'], -74.0060)
        
        # Disconnect
        await communicator.disconnect()
        
        # Verify that the location was saved to the database
        location_update = await self.get_latest_location_update(delivery)
        self.assertIsNotNone(location_update)
        self.assertEqual(location_update.location.y, 40.7128)
        self.assertEqual(location_update.location.x, -74.0060)
    
    @database_sync_to_async
    def create_user(self):
        """Create a test user."""
        from apps.companies.models import Companie
        from apps.accounts.models import Employeer
        
        # Create a company
        company = Companie.objects.create(
            name="Test Company",
            cnpj="12345678901234",
            email="test@company.com"
        )
        
        # Create a user
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create an employee
        Employeer.objects.create(
            user=user,
            companie=company,
            name="Test Employee",
            email="test@example.com"
        )
        
        return user
    
    @database_sync_to_async
    def create_delivery(self, user):
        """Create a test delivery."""
        from apps.companies.customers.models import Customer
        
        # Get the company
        company = user.employeer.companie
        
        # Create a customer
        customer = Customer.objects.create(
            companie=company,
            name="Test Customer",
            email="customer@example.com"
        )
        
        # Create a delivery
        delivery = Delivery.objects.create(
            companie=company,
            customer=customer,
            driver=user.employeer,
            origin="Test Origin",
            destiny="Test Destination",
            status="pending"
        )
        
        return delivery
    
    @database_sync_to_async
    def get_token(self, user):
        """Get a JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    @database_sync_to_async
    def get_latest_location_update(self, delivery):
        """Get the latest location update for a delivery."""
        return DeliveryLocationUpdate.objects.filter(
            delivery=delivery
        ).order_by('-created_at').first()
