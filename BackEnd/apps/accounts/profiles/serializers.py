from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.accounts.profiles.models import Profile
from apps.accounts.serializers import UserSerializer
from django.utils.translation import gettext


class ProfileBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Profile model.
    
    Provides essential profile information for list views and
    nested representations.
    """
    name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'avatar',
            'name',
            'age',
            'position',
            'department',
        ]
        read_only_fields = ['id']


class ProfileDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Profile model.
    
    Provides complete profile information including user details,
    contact information, and preferences.
    """
    # user = UserSerializer(read_only=True)
    name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    social_links = serializers.JSONField(required=False)
    preferences = serializers.JSONField(required=False)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            # 'user',
            'name',
            'bio',
            'birth_date',
            'position',
            'department',
            'avatar',
            'age',
            'social_links',
            'preferences',
            'phone',
            'email',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
            'companie',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Profile information.
    
    Allows updating of profile fields while maintaining
    data validation and security.
    """
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    companie = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'user',
            'companie',
            'bio',
            'birth_date',
            'position',
            'department',
            'avatar',
            'social_links',
            'preferences',
            'phone',
            'email',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
        ]
        
    def validate_social_links(self, value):
        """Validate social links format and URLs."""
        if not isinstance(value, dict):
            raise ValidationError(
                gettext("Social links must be a dictionary of platform-URL pairs")
            )
        
        for platform, url in value.items():
            if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                raise ValidationError(
                    gettext("Invalid URL format for platform: {platform}")
                )
        return value
    
    def validate_preferences(self, value):
        """Validate user preferences format."""
        if not isinstance(value, dict):
            raise ValidationError(
                gettext("Preferences must be a dictionary")
            )
        return value
        
    def create(self, validated_data):
        """Create a new profile."""
        user = self.context['request'].user
        try:
            from apps.companies.employeers.models import Employeer
            employeer = Employeer.objects.get(user=user)
            validated_data['user'] = user
            validated_data['companie'] = employeer.companie
            return super().create(validated_data)
        except Employeer.DoesNotExist:
            raise ValidationError(gettext("User is not associated with an employee"))


class ProfileAvatarSerializer(serializers.ModelSerializer):
    """
    Serializer for handling profile avatar updates.
    
    Specialized serializer for avatar-only updates to handle
    file uploads efficiently.
    """
    class Meta:
        model = Profile
        fields = ['avatar']
        
    def validate_avatar(self, value):
        """Validate avatar file size and format."""
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError(
                    gettext("Avatar file size cannot exceed 5MB")
                )
            if not value.content_type.startswith('image/'):
                raise ValidationError(
                    gettext("Only image files are allowed for avatar")
                )
        return value