"""
Tests for Profile notifications
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from ..models import Profile
from apps.companies.models import Companie
from apps.companies.employeers.models import Employeer
from apps.accounts.models import User
from ..notifications.handlers import ProfileNotificationHandler
from unittest.mock import patch, call

User = get_user_model()

class ProfileNotificationTest(TestCase):
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
        
    def setUp(self):
        """Set up data for each test method"""
        self.notification_handler = ProfileNotificationHandler()
        self.profile = Profile.objects.create(
            user=self.employee,
            companie=self.company,
            bio='Test bio',
            position='Developer'
        )
        
    @patch('apps.notifications.base.send_notification')
    def test_profile_created_notification(self, mock_send):
        """Test profile created notification"""
        self.notification_handler.notify_profile_created(self.profile)
        self.assertTrue(mock_send.called)
        args = mock_send.call_args[1]  # Get kwargs
        self.assertEqual(args['notification_type'], 'info')
        self.assertEqual(args['title'], 'New Profile Created')
        
    @patch('apps.notifications.base.send_notification')
    def test_profile_updated_notification(self, mock_send):
        """Test profile updated notification"""
        self.notification_handler.notify_profile_updated(self.profile)
        self.assertTrue(mock_send.called)
        args = mock_send.call_args[1]  # Get kwargs
        self.assertEqual(args['notification_type'], 'info')
        self.assertEqual(args['title'], 'Profile Updated')
        
    @patch('apps.notifications.base.send_notification')
    def test_profile_deleted_notification(self, mock_send):
        """Test profile deleted notification"""
        self.notification_handler.notify_profile_deleted(self.profile)
        self.assertTrue(mock_send.called)
        args = mock_send.call_args[1]  # Get kwargs
        self.assertEqual(args['notification_type'], 'warning')
        self.assertEqual(args['title'], 'Profile Deleted')
        
    @patch('apps.notifications.base.send_notification')
    def test_avatar_updated_notification(self, mock_send):
        """Test avatar updated notification"""
        self.notification_handler.notify_avatar_updated(self.profile)
        self.assertTrue(mock_send.called)
        args = mock_send.call_args[1]  # Get kwargs
        self.assertEqual(args['notification_type'], 'info')
        self.assertEqual(args['title'], 'Profile Avatar Updated')
        
    @patch('apps.notifications.base.send_notification')
    def test_bulk_notifications(self, mock_send):
        """Test sending multiple notifications"""
        self.notification_handler.notify_profile_created(self.profile)
        self.notification_handler.notify_profile_updated(self.profile)
        self.notification_handler.notify_avatar_updated(self.profile)
        self.assertEqual(mock_send.call_count, 3)
        
    @patch('apps.notifications.base.send_notification')
    def test_notification_with_error(self, mock_send):
        """Test notification with error handling"""
        mock_send.side_effect = Exception('Test error')
        try:
            self.notification_handler.notify_profile_created(self.profile)
        except:
            pass  # We expect the error to be handled gracefully
        else:
            self.fail('Notification handler should handle errors gracefully')