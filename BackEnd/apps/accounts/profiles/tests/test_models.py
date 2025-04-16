"""
Tests for Profile models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Profile
from apps.accounts.models import User
from apps.companies.models import Companie
from apps.companies.employeers.models import Employeer

User = get_user_model()

class ProfileModelTest(TestCase):
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
            user_type='Stock_Controller'
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
        stock_group = Group.objects.get(name='Stock_Controller')
        employee_group = Group.objects.get(name='Employee')
        
        cls.admin_user.groups.add(admin_group)
        cls.stock_user.groups.add(stock_group)
        cls.employee.groups.add(employee_group)
        
    def test_profile_creation(self):
        """Test profile creation with valid data"""
        profile = Profile.objects.create(
            user=self.employee,
            companie=self.company,
            bio='Test bio',
            position='Developer',
            department='IT',
            phone='1234567890',
            email='test@example.com',
            address='Test Address',
            city='Test City',
            state='TS',
            country='Test Country'
        )
        self.assertEqual(profile.user.email, 'employee@example.com')
        self.assertEqual(profile.companie.name, 'Test Company')
        self.assertEqual(profile.position, 'Developer')
        self.assertTrue(profile.is_active)
        
    def test_profile_str_representation(self):
        """Test profile string representation"""
        profile = Profile.objects.create(
            user=self.employee,
            companie=self.company
        )
        expected_str = f'Profile of {self.employee.get_full_name()}'
        self.assertEqual(str(profile), expected_str)
        
    def test_profile_avatar_upload(self):
        """Test profile avatar upload"""
        profile = Profile.objects.create(
            user=self.employee,
            companie=self.company
        )
        avatar = SimpleUploadedFile(
            "test_avatar.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        profile.avatar = avatar
        profile.save()
        
        self.assertTrue(profile.avatar)
        self.assertTrue(profile.avatar.name.endswith('.jpg'))
        
    def test_profile_full_name(self):
        """Test profile full name method"""
        profile = Profile.objects.create(
            user=self.employee,
            companie=self.company
        )
        expected_name = f'{self.employee.first_name} {self.employee.last_name}'
        self.assertEqual(profile.get_full_name(), expected_name)
        
    def test_profile_social_links(self):
        """Test profile social links"""
        social_links = {
            'linkedin': 'https://linkedin.com/test',
            'github': 'https://github.com/test'
        }
        profile = Profile.objects.create(
            user=self.employee,
            companie=self.company,
            social_links=social_links
        )
        self.assertEqual(profile.social_links, social_links)
        
    def test_profile_preferences(self):
        """Test profile preferences"""
        preferences = {
            'theme': 'dark',
            'notifications': True
        }
        profile = Profile.objects.create(
            user=self.employee,
            companie=self.company,
            preferences=preferences
        )
        self.assertEqual(profile.preferences, preferences)