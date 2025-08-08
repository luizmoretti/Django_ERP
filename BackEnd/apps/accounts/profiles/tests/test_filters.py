"""
Tests for Profile filters
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Profile
from apps.companies.models import Companie
from ..services.filters import ProfileFilter
from apps.accounts.models import User
from datetime import timedelta, datetime

User = get_user_model()

class ProfileFilterTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass123',
            first_name='John',
            last_name='Doe'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass123',
            first_name='Jane',
            last_name='Smith'
        )
        self.companie = Companie.objects.create(name='Test Company')
        
        # Create profiles with different dates
        self.yesterday = datetime.now() - timedelta(days=1)
        self.today = datetime.now()
        
        # Nova: Recupere perfis auto-criados em vez de criar novos
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        
        # Atualize datas para testar filtros (sem criar novos registros)
        self.profile1.created_at = self.yesterday
        self.profile1.save(update_fields=['created_at'])
        
        self.profile2.created_at = self.today
        self.profile2.save(update_fields=['created_at'])
        
    def test_search_filter(self):
        """Test search filter"""
        # Test first name search
        queryset = Profile.objects.all()
        f = ProfileFilter({'search': 'John'}, queryset=queryset)
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0], self.profile1)
        
        # Test email search
        f = ProfileFilter({'search': 'user2'}, queryset=queryset)
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0], self.profile2)
        
    def test_created_at_filter(self):
        """Test created_at filter"""
        queryset = Profile.objects.all()
        
        # Create profiles with a time difference
        self.profile1.delete()
        self.profile2.delete()
        
        profile1 = Profile.objects.create(
            user=self.user1,
            companie=self.companie
        )
        
        profile2 = Profile.objects.create(
            user=self.user2,
            companie=self.companie
        )
        
        # Get the actual created_at values from the database
        profile1_created = Profile.objects.get(id=profile1.id).created_at
        profile2_created = Profile.objects.get(id=profile2.id).created_at
        
        # Test created_at_after filter using the actual timestamp
        f = ProfileFilter(
            {'created_at_after': profile1_created},
            queryset=queryset
        )
        self.assertEqual(len(f.qs), 2)  # Both profiles because created_at_after uses gte (greater than or equal)
        self.assertIn(profile1, f.qs)
        self.assertIn(profile2, f.qs)
        
        # Test created_at_before filter using the actual timestamp
        f = ProfileFilter(
            {'created_at_before': profile2_created},
            queryset=queryset
        )
        self.assertEqual(len(f.qs), 2)  # Both profiles because created_at_before uses lte (less than or equal)
        self.assertIn(profile1, f.qs)
        self.assertIn(profile2, f.qs)
        
    def test_is_active_filter(self):
        """Test is_active filter"""
        self.profile1.is_active = False
        self.profile1.save()
        
        queryset = Profile.objects.all()
        f = ProfileFilter({'is_active': True}, queryset=queryset)
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0], self.profile2)