"""
Tests for Profile views
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from ..models import Profile
from apps.accounts.models import User
from apps.companies.models import Companie
from apps.companies.employeers.models import Employeer
from django.core.files.uploadedfile import SimpleUploadedFile
from core.constants.choices import (
    PROFILE_POSITION_CHOICES,
    PROFILE_DEPARTMENT_CHOICES,
    STATE_CHOICES,
    COUNTRY_CHOICES
)
import json

User = get_user_model()

class ProfileViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Set up groups and permissions
        call_command('setup_permission_groups')
        
        # Create users with different types
        cls.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        cls.stock_user = User.objects.create_user(
            email='stock@example.com',
            password='stock123',
            first_name='Stock',
            last_name='Controller',
            user_type='Stocker'
        )
        
        cls.employee = User.objects.create_user(
            email='employee@example.com',
            password='emp123',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Create company
        cls.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Get automatically created employees
        cls.admin_employee = Employeer.objects.get(user=cls.admin_user)
        cls.stock_employee = Employeer.objects.get(user=cls.stock_user)
        cls.regular_employee = Employeer.objects.get(user=cls.employee)
        
        # Associate employees with company
        cls.admin_employee.companie = cls.company
        cls.admin_employee.save()
        cls.stock_employee.companie = cls.company
        cls.stock_employee.save()
        cls.regular_employee.companie = cls.company
        cls.regular_employee.save()
        
        # Add users to appropriate groups
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stocker')
        employee_group = Group.objects.get(name='Employee')
        
        cls.admin_user.groups.add(admin_group)
        cls.stock_user.groups.add(stock_group)
        cls.employee.groups.add(employee_group)
        
        # Sync user permissions
        call_command('setup_permission_groups')
        
    def setUp(self):
        """Set up data for each test method"""
        # Create client
        self.client = APIClient()
        
        # Create profile for testing
        self.profile = Profile.objects.create(
            user=self.employee,
            companie=self.company,
            bio='Initial bio',
            position=PROFILE_POSITION_CHOICES[0][0],  # First position choice
            department=PROFILE_DEPARTMENT_CHOICES[0][0]  # First department choice
        )
        
        # Authenticate as admin by default
        self.client.force_authenticate(user=self.admin_user)
        
    def test_profile_list(self):
        """Test profile list endpoint"""
        url = reverse('profiles:profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_profile_detail(self):
        """Test profile detail endpoint"""
        url = reverse('profiles:profile-detail', kwargs={'pk': self.profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], self.employee.email)
        
    def test_profile_create(self):
        """Test profile creation endpoint"""
        # Create a new user specifically for this test
        new_test_user = User.objects.create_user(
            email='new_test_user@example.com',
            password='test123',
            first_name='Test',
            last_name='User',
            user_type='Employee'
        )
        
        # Important: Delete the profile that was automatically created by the signal
        # This is needed because we want to test the manual creation through the API
        Profile.objects.filter(user=new_test_user).delete()
        
        # Verify the profile was deleted
        self.assertFalse(Profile.objects.filter(user=new_test_user).exists())
        
        # Get initial count of profiles
        initial_count = Profile.objects.count()
        
        # Create profile through API
        url = reverse('profiles:profile-create')
        data = {
            'user': new_test_user.id,
            'companie': self.company.id,
            'bio': 'Test bio',
            'position': PROFILE_POSITION_CHOICES[0][0],
            'department': PROFILE_DEPARTMENT_CHOICES[0][0],
            'phone': '1234567890',
            'email': 'new_test@example.com',
            'address': 'Test Address',
            'city': 'Test City',
            'state': STATE_CHOICES[0][0],
            'country': COUNTRY_CHOICES[0][0]
        }
        
        # Make the API call
        response = self.client.post(url, data, format='json')
        
        # Check that it was successful and that exactly one new profile was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), initial_count + 1)
        
        # Verify the profile was created for the correct user
        self.assertTrue(Profile.objects.filter(user=new_test_user).exists())
        
    def test_profile_update(self):
        """Test profile update endpoint"""
        url = reverse('profiles:profile-update', kwargs={'pk': self.profile.id})
        data = {
            'bio': 'Updated bio',
            'position': PROFILE_POSITION_CHOICES[1][0]  # Second position choice
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
        
    def test_profile_delete(self):
        """Test profile delete endpoint"""
        url = reverse('profiles:profile-delete', kwargs={'pk': self.profile.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_active)
        
    def test_profile_avatar(self):
        """Test profile avatar update endpoint"""
        url = reverse('profiles:profile-avatar', kwargs={'pk': self.profile.id})
        avatar = SimpleUploadedFile(
            "test_avatar.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        response = self.client.put(
            url,
            {'avatar': avatar},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.avatar)
        
    def test_profile_list_filter(self):
        """Test profile list filtering"""
        url = reverse('profiles:profile-list')
        response = self.client.get(url, {'search': 'Regular'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_profile_list_pagination(self):
        """Test profile list pagination"""
        url = reverse('profiles:profile-list')
        response = self.client.get(url, {'page': 1, 'page_size': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_profile_unauthorized(self):
        """Test unauthorized access to profile endpoints"""
        self.client.force_authenticate(user=None)
        url = reverse('profiles:profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_profile_forbidden(self):
        """Test forbidden access to profile endpoints"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('profiles:profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)