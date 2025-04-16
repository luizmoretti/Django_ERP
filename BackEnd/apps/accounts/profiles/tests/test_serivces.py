"""
Tests for Profile services
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import override_settings
from ..models import Profile
from apps.companies.models import Companie
from apps.companies.employeers.models import Employeer
from ..services.handlers import ProfileService
from apps.accounts.models import User
import tempfile
import shutil
import os

User = get_user_model()

class ProfileServiceTest(TestCase):
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
        
    def setUp(self):
        """Set up data for each test method"""
        # Create temp media directory
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        # Create test profile
        self.profile = Profile.objects.create(
            user=self.employee,
            companie=self.company,
            bio='Test bio',
            position='Developer'
        )
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_get_profile_detail(self):
        """Test getting profile details"""
        profile = ProfileService.get_profile_detail(self.profile.id)
        self.assertEqual(profile.id, self.profile.id)
        self.assertEqual(profile.user.email, self.employee.email)
        
    def test_update_profile(self):
        """Test updating profile"""
        data = {
            'bio': 'Updated bio',
            'position': 'Senior Developer'
        }
        updated_profile = ProfileService.update_profile(
            self.profile.id,
            data,
            self.admin_user
        )
        self.assertEqual(updated_profile.bio, 'Updated bio')
        self.assertEqual(updated_profile.position, 'Senior Developer')
        
    def test_delete_profile(self):
        """Test soft deleting profile"""
        deleted_profile = ProfileService.delete_profile(
            self.profile.id,
            self.admin_user
        )
        self.assertFalse(deleted_profile.is_active)
        
    def test_handle_avatar_upload(self):
        """Test avatar upload handling"""
        avatar = SimpleUploadedFile(
            "test_avatar.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        updated_profile = ProfileService.handle_avatar_upload(
            self.profile.id,
            avatar,
            self.admin_user
        )
        self.assertTrue(updated_profile.avatar)
        
    def test_filter_profiles(self):
        """Test profile filtering"""
        filters = {'search': 'Regular'}
        profiles = ProfileService.filter_profiles(filters)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].id, self.profile.id)
        
    def test_validate_profile_data(self):
        """Test profile data validation"""
        # Valid data
        data = {
            'bio': 'Valid bio',
            'position': 'Owner',  # Uma posição válida do PROFILE_POSITION_CHOICES
            'phone': '1234567890'
        }
        validated_data = ProfileService.validate_profile_data(data)
        self.assertEqual(validated_data, data)
        
        # Invalid data
        invalid_data = {
            'bio': 'Valid bio',
            'phone': 'invalid'  # Should be numeric
        }
        with self.assertRaises(ValidationError):
            ProfileService.validate_profile_data(invalid_data)