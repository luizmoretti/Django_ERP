"""Profile service handlers"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.models import Permission
from ..models import Profile
from ..notifications.handlers import ProfileNotificationHandler
from ..services.filters import ProfileFilter
import re

class ProfileService:
    """Service class for Profile operations"""
    
    @staticmethod
    def get_profile_detail(profile_id):
        """Get profile details with caching"""
        return Profile.objects.select_related(
            'user',
            'companie'
        ).get(id=profile_id)
    
    @staticmethod
    def update_profile(profile_id, data, user):
        """Update profile if user has permission"""
        if not user.has_perm('profiles.change_profile'):
            raise ValidationError(_('You do not have permission to update profiles'))
            
        profile = Profile.objects.select_for_update().get(pk=profile_id)
        
        for field, value in data.items():
            setattr(profile, field, value)
            
        profile.save()
        
        return profile
        
    @staticmethod
    def handle_avatar_upload(profile_id, avatar_file, user):
        """Handle avatar upload for profile"""
        if not user.has_perm('profiles.change_profile'):
            raise ValidationError(_('You do not have permission to update profile avatar'))
            
        profile = Profile.objects.get(pk=profile_id)
        
        # Delete old avatar if exists
        if profile.avatar:
            default_storage.delete(profile.avatar.name)
            
        # Save new avatar
        file_name = f'avatars/{profile_id}/{avatar_file.name}'
        profile.avatar = default_storage.save(
            file_name,
            ContentFile(avatar_file.read())
        )
        profile.save()
        
        return profile
        
    @staticmethod
    def delete_profile(profile_id, user):
        """Soft delete profile if user has permission"""
        if not user.has_perm('profiles.delete_profile'):
            raise ValidationError(_('You do not have permission to delete profiles'))
            
        profile = Profile.objects.get(pk=profile_id)
        profile.is_active = False
        profile.save()
        
        return profile

    @staticmethod
    def filter_profiles(filters):
        """Filter profiles based on given criteria"""
        queryset = Profile.objects.select_related('user', 'companie').all()
        profile_filter = ProfileFilter(filters, queryset=queryset)
        return profile_filter.qs

    @staticmethod
    def validate_profile_data(data):
        """Validate profile data before saving"""
        errors = {}
        
        # Validate phone number (if provided)
        if 'phone' in data:
            phone = data['phone']
            if not re.match(r'^\d+$', phone):
                errors['phone'] = _('Phone number must contain only digits')
                
        # Validate bio length (if provided)
        if 'bio' in data:
            bio = data['bio']
            if len(bio) > 500:  # Example max length
                errors['bio'] = _('Bio must not exceed 500 characters')
                
        # Validate position (if provided)
        if 'position' in data:
            position = data['position']
            from core.constants.choices import PROFILE_POSITION_CHOICES
            valid_positions = [choice[0] for choice in PROFILE_POSITION_CHOICES]
            if position not in valid_positions:
                errors['position'] = _('Invalid position choice')
                
        # Validate department (if provided)
        if 'department' in data:
            department = data['department']
            from core.constants.choices import PROFILE_DEPARTMENT_CHOICES
            valid_departments = [choice[0] for choice in PROFILE_DEPARTMENT_CHOICES]
            if department not in valid_departments:
                errors['department'] = _('Invalid department choice')
                
        if errors:
            raise ValidationError(errors)
            
        return data