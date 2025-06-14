from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.hashers import make_password
from .models import User
from core.constants.choices import USER_TYPE_CHOICES

class BaseUserSerializer(serializers.ModelSerializer):
    """
    Base serializer for user operations with common fields and validations.
    
    This serializer provides the foundation for user-related operations,
    implementing common fields and basic validation rules. Most fields
    are read-only to ensure data integrity.
    
    Attributes:
        id (UUIDField): Read-only user identifier
        username (CharField): Read-only, automatically set to email
        email (EmailField): User's email address for authentication
        first_name (CharField): User's first name
        last_name (CharField): User's last name
        type (CharField): Read-only user role classification
        date_joined (DateTimeField): Read-only timestamp of account creation
        is_active (BooleanField): Read-only account status
        last_login (DateTimeField): Read-only timestamp of last login
        img (ImageField): Optional profile picture
        ip (IPAddressField): Read-only last known IP address
    
    Note:
        This serializer should be inherited by other user-specific serializers
        that need to implement additional functionality.
    """
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    user_type = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    is_active = serializers.BooleanField(required=False, read_only=True, default=True)
    last_login = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    ip = serializers.IPAddressField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'user_type', 'date_joined', 'is_active', 'last_login','ip'
        ]


class UserSerializer(BaseUserSerializer):
    """
    Complete user serializer for CRUD operations with extended functionality.
    
    This serializer extends BaseUserSerializer to provide full user management
    capabilities, including password handling, group management, and enhanced
    validation rules.
    
    Attributes:
        All fields from BaseUserSerializer plus:
        password (CharField): Write-only field for user password
        groups (SerializerMethodField): User group memberships
        user_permissions (SerializerMethodField): User-specific permissions
        is_staff (BooleanField): Read-only admin access status
        is_superuser (BooleanField): Read-only superuser status
        user_type (CharField): Write-only field for user role classification
        
    Validation Rules:
        Password must:
        - Be at least 8 characters long
        - Contain at least one number
        - Contain at least one letter
        - Contain at least one uppercase letter
    
    Methods:
        create: Creates new user with encrypted password
        update: Updates user data, handling password separately
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )
    groups = serializers.SerializerMethodField()
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES,
        required=True
    )
    user_permissions = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True, default=False)
    is_superuser = serializers.BooleanField(read_only=True, default=False)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + [
            'password', 'groups', 'user_permissions', 'is_staff', 'user_type', 'is_superuser'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_groups(self, obj) -> list:
        """
        Retrieves and formats user's group memberships.
        
        Args:
            obj: User instance being serialized
            
        Returns:
            list: List of dictionaries containing group id and name
        """
        return [
            {'id': group.id, 'name': group.name} 
            for group in obj.groups.select_related().all()
        ]
    
    def get_user_permissions(self, obj) -> list:
        """
        Retrieves and formats user's specific permissions.
        
        Args:
            obj: User instance being serialized
            
        Returns:
            list: List of dictionaries containing permission id and name
        """
        return [
            {'id': permission.id, 'name': permission.name} 
            for permission in obj.user_permissions.select_related().all()
        ]

    def validate_password(self, value):
        """
        Validates password against security requirements.
        
        Args:
            value: Password string to validate
            
        Returns:
            str: Validated password
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if value:
            if len(value) < 8:
                raise ValidationError("The password must be at least 8 characters long.")
            if not any(char.isdigit() for char in value):
                raise ValidationError("The password must contain at least one number.")
            if not any(char.isalpha() for char in value):
                raise ValidationError("The password must contain at least one letter.")
            if not any(char.isupper() for char in value):
                raise ValidationError("The password must contain at least one uppercase letter.")
        return value

    def create(self, validated_data):
        """
        Creates a new user instance with encrypted password.
        
        Args:
            validated_data: Dictionary of validated user data
            
        Returns:
            NormalUser: Created user instance
        """
        password = validated_data.pop('password', None)
        if password:
            user = self.Meta.model.objects.create_user(
                email=validated_data.pop('email'),
                password=password,
                **validated_data
            )
        else:
            user = self.Meta.model.objects.create_user(
                email=validated_data.pop('email'),
                **validated_data
            )
            
        return user

    def update(self, instance, validated_data):
        """
        Updates existing user instance, handling password separately.
        
        Args:
            instance: Existing user instance to update
            validated_data: Dictionary of validated update data
            
        Returns:
            NormalUser: Updated user instance
        """
        
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class ListAllUsersSerializer(BaseUserSerializer):
    """
    Simplified serializer for user listing operations.
    
    This serializer inherits from BaseUserSerializer and is specifically
    designed for list views where detailed user information is not needed.
    It maintains the same field structure but omits sensitive operations.
    
    Note:
        Uses all fields from BaseUserSerializer without modifications
    """
    pass




class LoginSerializer(serializers.Serializer):
    """
    Serializer for the login endpoint.
    
    Attributes:
        email: User's email address
        password: User's password (write-only)
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password is required'
        }
    )

    def validate(self, attrs):
        """
        Validate the login data.
        
        Args:
            attrs: Dictionary of field values
            
        Returns:
            dict: Validated data
        """
        return attrs

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    
    Validates that:
    - Password meets minimum requirements
    - Password confirmation matches
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        error_messages={
            'required': 'New password is required',
            'min_length': 'Password must be at least 8 characters long'
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password confirmation is required'
        }
    )

    def validate_password(self, value):
        """
        Validate password strength.
        """
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('Password must contain at least one number')
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise serializers.ValidationError('Password must contain at least one lowercase letter')
        if not any(not char.isalnum() for char in value):
            raise serializers.ValidationError('Password must contain at least one special character')
        return value

    def validate(self, attrs):
        """
        Validate that passwords match.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError('Passwords do not match')
        return attrs