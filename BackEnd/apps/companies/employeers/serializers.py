from rest_framework import serializers
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from apps.accounts.models import User
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class EmployeerSerializer(serializers.ModelSerializer):
    """
    Centralized serializer for employee operations.

    This serializer provides all the necessary functionality for:
    - Listing employees
    - Creating employees
    - Updating employees
    - Detailing employees
    
    Attributes:
        id (UUIDField): Unique identifier for the employee (read-only)
        name (CharField): Full name of the employee
        id_number (CharField): Employee identification number
        
        # Contact Information
        phone (CharField): Phone number
        email (EmailField): Email address
        
        # Address Information
        address (CharField): Address
        city (CharField): City
        state (CharField): State
        zip_code (CharField): ZIP code
        country (CharField): Country
        
        # User Information
        user (PrimaryKeyRelatedField): User (write-only)
        _user (SerializerMethodField): Associated user data (read-only)
        
        # Company Information
        company (SerializerMethodField): Company data (read-only)

        # Audit fields
        created_at (DateTimeField): Creation date
        updated_at (DateTimeField): Last updated date
        created_by_name (SerializerMethodField): Name of creator
        updated_by_name (SerializerMethodField): Last updated name
    """
    # Basic Fields
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(required=False)
    id_number = serializers.CharField(required=False)
    
    hire_date = serializers.DateField(required=False)
    termination_date = serializers.DateField(required=False)
    payroll_schedule = serializers.CharField(required=False)
    payment_type = serializers.CharField(required=False)
    rate = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    
    # Contact Information
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    
    # Address Information
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    
    # User Information
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, write_only=True)
    _user = serializers.SerializerMethodField(read_only=True)
    
    # Audit fields
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    companie = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employeer
        fields = [
            # Basic Fields
            'id', 'name', 'id_number', 'hire_date', 
            'termination_date', 'payroll_schedule', 
            'payment_type', 'rate',
            
            # Contact Information
            'phone', 'email',
            
            # Address Information
            'address', 'city', 'state', 'zip_code', 'country',
            
            # User Information
            'user', '_user',
            
            # Audit fields
            'created_at', 'updated_at', 'created_by', 'updated_by', 'companie'
        ]
        read_only_fields = [
            'id', 
            'age', 
            '_user',
            'created_at', 
            'updated_at',
            'created_by',
            'updated_by',
            'companie'
        ]

    def get__user(self, obj) -> dict:
        """Retorna informações do usuário associado"""
        if obj.user:
            return {
                'email': obj.user.email,
                'user_type': obj.user.user_type,
                'is_active': obj.user.is_active
            }
        return None

    def get_companie(self, obj) -> str:
        """Returns formatted company information"""
        if obj.companie:
            return f"[{obj.companie.type}] {obj.companie.name}"
        return None

    def get_created_by(self, obj) -> str | None:
        """Returns the name of the person who created the record"""
        if obj.created_by:
            return f"{obj.created_by.name}"
        return None

    def get_updated_by(self, obj) -> str | None:
        """Returns the name of the person who updated the record"""
        if obj.updated_by:
            return f"{obj.updated_by.name}"
        return None

    def validate_email(self, value):
        """Validates if the email is unique"""
        if not value:
            return value
            
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value
            
        if Employeer.objects.filter(email=value).exists():
            raise ValidationError("This email is already in use")
        return value

    def validate_user(self, value):
        """Validates that the user exists and is not associated with another employee"""
        try:
            user = User.objects.get(id=value, is_active=True)
            
            existing = Employeer.objects.filter(user_id=value)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
                
            if existing.exists():
                raise ValidationError("This user is already associated with another employee")
                
            return value
        except User.DoesNotExist:
            raise ValidationError("Invalid user")

    
    def create(self, validated_data):
        """Create a new employee"""
        user_id = validated_data.pop('user')
        instance = self.Meta.model(**validated_data)
        instance.user_id = user_id
        instance.save()
        return instance

    
    def update(self, instance, validated_data):
        """Updates an existing employee"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance