from django.test import TestCase
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken
import pytest

from apps.deliveries.models import Delivery
from apps.deliveries.tracking.middleware import DeliveryTokenAuthMiddleware, get_user, get_delivery_permissions

User = get_user_model()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class DeliveryTokenAuthMiddlewareTests(TestCase):
    """
    Tests for the delivery tracking authentication middleware.
    """
    
    async def test_get_user_with_valid_id(self):
        """
        Test getting a user with a valid ID.
        """
        # Create a user
        user = await self.create_user()
        
        # Get the user using the middleware function
        retrieved_user = await get_user(user.id)
        
        # Assert that the user was retrieved correctly
        self.assertEqual(retrieved_user.id, user.id)
        self.assertEqual(retrieved_user.email, user.email)
    
    async def test_get_user_with_invalid_id(self):
        """
        Test getting a user with an invalid ID.
        """
        # Get a user with an invalid ID
        retrieved_user = await get_user("invalid-id")
        
        # Assert that an AnonymousUser was returned
        self.assertFalse(retrieved_user.is_authenticated)
    
    async def test_get_delivery_permissions_with_valid_user_and_delivery(self):
        """
        Test checking delivery permissions with a valid user and delivery.
        """
        # Create a user
        user = await self.create_user()
        
        # Create a delivery
        delivery = await self.create_delivery(user)
        
        # Check permissions
        has_permission = await get_delivery_permissions(user, delivery.id)
        
        # Assert that the user has permission
        self.assertTrue(has_permission)
    
    async def test_get_delivery_permissions_with_invalid_delivery(self):
        """
        Test checking delivery permissions with an invalid delivery.
        """
        # Create a user
        user = await self.create_user()
        
        # Check permissions for an invalid delivery
        has_permission = await get_delivery_permissions(user, "invalid-id")
        
        # Assert that the user does not have permission
        self.assertFalse(has_permission)
    
    async def test_get_delivery_permissions_with_anonymous_user(self):
        """
        Test checking delivery permissions with an anonymous user.
        """
        # Create a user and delivery
        user = await self.create_user()
        delivery = await self.create_delivery(user)
        
        # Create an anonymous user
        from django.contrib.auth.models import AnonymousUser
        anonymous_user = AnonymousUser()
        
        # Check permissions
        has_permission = await get_delivery_permissions(anonymous_user, delivery.id)
        
        # Assert that the anonymous user does not have permission
        self.assertFalse(has_permission)
    
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
