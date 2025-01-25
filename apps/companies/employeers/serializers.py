from rest_framework import serializers
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from apps.accounts.models import NormalUser
from rest_framework.exceptions import ValidationError


class BaseEmployeerSerializer(serializers.ModelSerializer):
    """
    Base serializer for employee operations with common fields.
    
    This serializer provides the foundation for employee-related operations,
    implementing common fields and basic validation rules.
    
    Attributes:
        id (UUIDField): Read-only employee identifier
        first_name (CharField): Employee's first name
        last_name (CharField): Employee's last name
        age (IntegerField): Optional calculated age
        date_of_birth (DateField): Optional birth date
        email (EmailField): Required unique email
        phone (CharField): Optional contact phone
        address (CharField): Optional physical address
        city (CharField): Optional city location
        zip_code (CharField): Optional postal code
        is_active (BooleanField): Optional status flag
        created_at (DateTimeField): Read-only timestamp of creation
        updated_at (DateTimeField): Read-only timestamp of last update
    """
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    age = serializers.IntegerField(required=False, read_only=True)
    date_of_birth = serializers.DateField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Employeer
        fields = [
            'id', 'first_name', 'last_name', 'age', 'date_of_birth',
            'email', 'phone', 'address', 'city', 'zip_code', 'is_active',
            'created_at', 'updated_at'
        ]


class EmployeerSerializer(BaseEmployeerSerializer):
    """
    Complete employee serializer for CRUD operations.
    
    This serializer extends BaseEmployeerSerializer to provide full employee
    management capabilities, including user and company relationships.
    
    Attributes:
        All fields from BaseEmployeerSerializer plus:
        user (SerializerMethodField): Associated user information
        user_id (UUIDField): Write-only user identifier
        companie (SerializerMethodField): Associated company information
        companie_id (UUIDField): Write-only company identifier
        created_by (SerializerMethodField): Creator's full name
        created_by_id (UUIDField): Write-only creator identifier
        updated_by (SerializerMethodField): Last updater's full name
        updated_by_id (UUIDField): Write-only updater identifier
    
    Validation Rules:
        - Email must be unique
        - User ID must reference an active user
        - Company ID must reference an active company
        - Created_by and updated_by must be valid users
    """
    user = serializers.SerializerMethodField()
    user_id = serializers.UUIDField(write_only=True, required=True)
    companie = serializers.SerializerMethodField()
    companie_id = serializers.UUIDField(write_only=True, required=False)
    created_by = serializers.SerializerMethodField()
    created_by_id = serializers.UUIDField(write_only=True, required=False)
    updated_by = serializers.SerializerMethodField()
    updated_by_id = serializers.UUIDField(write_only=True, required=False)

    class Meta(BaseEmployeerSerializer.Meta):
        fields = BaseEmployeerSerializer.Meta.fields + [
            'user', 'user_id',
            'companie', 'companie_id',
            'created_by', 'created_by_id',
            'updated_by', 'updated_by_id'
        ]
    
    def validate_email(self, value):
        """
        Validates email uniqueness.
        
        Args:
            value: Email to validate
            
        Returns:
            str: Validated email
            
        Raises:
            ValidationError: If email is already in use
        """
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value
            
        if Employeer.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value
    
    def validate_user_id(self, value):
        """
        Validates that the user exists, is active, and is not associated with another employee.
        
        Args:
            value: UUID of the user to validate
            
        Returns:
            UUID: Validated user ID
            
        Raises:
            ValidationError: If user doesn't exist, is inactive, or is already an employee
        """
        try:
            user = NormalUser.objects.get(id=value, is_active=True)
            
            # Check if this user is already an employee (excluding current instance if updating)
            existing_employee = Employeer.objects.filter(user_id=value)
            if self.instance:
                existing_employee = existing_employee.exclude(id=self.instance.id)
                
            if existing_employee.exists():
                raise ValidationError("This user is already associated with another employee")
                
            return value
        except NormalUser.DoesNotExist:
            raise ValidationError("Invalid or inactive user ID")
    
    def validate_companie_id(self, value):
        """
        Validates that the company exists and is active.
        
        Args:
            value: UUID of the company to validate
            
        Returns:
            UUID: Validated company ID
            
        Raises:
            ValidationError: If company doesn't exist or is inactive
        """
        try:
            companie = Companie.objects.get(id=value, is_active=True)
            return value
        except Companie.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive company ID")
    
    def get_user(self, obj) -> dict:
        """
        Retrieves associated user information.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            dict: User information including username and email
        """
        if obj.user:
            return {
                'username': obj.user.username,
                'email': obj.user.email,
                'is_active': obj.user.is_active
            }
        return None
    
    def get_companie(self, obj) -> str:
        """
        Retrieves formatted company information.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            str: Company name and type, or None if no company
        """
        if obj.companie:
            return f"{obj.companie.name} - {obj.companie.type}"
        return None

    def get_created_by(self, obj) -> str:
        """
        Retrieves the full name of the user who created the record.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            str: Creator's full name, or None if not available
        """
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def get_updated_by(self, obj) -> str:
        """
        Retrieves the full name of the user who last updated the record.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            str: Updater's full name, or None if not available
        """
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}"
        return None

    def create(self, validated_data):
        """
        Creates a new employee instance with relationships.
        
        Args:
            validated_data: Dictionary of validated employee data
            
        Returns:
            Employeer: Created employee instance
        """
        user_id = validated_data.pop('user_id')
        companie_id = validated_data.pop('companie_id')
        created_by_id = validated_data.pop('created_by_id', None)
        updated_by_id = validated_data.pop('updated_by_id', None)

        instance = self.Meta.model(**validated_data)
        
        instance.user_id = user_id
        instance.companie_id = companie_id
        if created_by_id:
            instance.created_by_id = created_by_id
        if updated_by_id:
            instance.updated_by_id = updated_by_id

        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Updates existing employee instance.
        
        Args:
            instance: Existing employee instance to update
            validated_data: Dictionary of validated update data
            
        Returns:
            Employeer: Updated employee instance
        """
        user_id = validated_data.pop('user_id', None)
        companie_id = validated_data.pop('companie_id', None)
        updated_by_id = validated_data.pop('updated_by_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if user_id:
            instance.user_id = user_id
        if companie_id:
            instance.companie_id = companie_id
        if updated_by_id:
            instance.updated_by_id = updated_by_id

        instance.save()
        return instance


class ListAllEmployeersSerializer(BaseEmployeerSerializer):
    """
    Simplified serializer for employee listing operations.
    
    This serializer inherits from BaseEmployeerSerializer and adds only
    the necessary relationship fields for list views. All fields are
    read-only to ensure data integrity in list operations.
    
    Attributes:
        All fields from BaseEmployeerSerializer plus:
        user (SerializerMethodField): Basic user information
        companie (SerializerMethodField): Company name and type
        created_by (SerializerMethodField): Creator's full name
        updated_by (SerializerMethodField): Last updater's full name
    """
    user = serializers.SerializerMethodField()
    companie = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta(BaseEmployeerSerializer.Meta):
        fields = BaseEmployeerSerializer.Meta.fields + [
            'user',
            'companie',
            'created_by',
            'updated_by'
        ]
        read_only_fields = fields
    
    def get_user(self, obj) -> dict:
        """
        Retrieves basic user information for list view.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            dict: Basic user information
        """
        if obj.user:
            return {
                'username': obj.user.username,
                'is_active': obj.user.is_active
            }
        return None
    
    def get_companie(self, obj) -> str:
        """
        Retrieves formatted company information for list view.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            str: Company name and type, or None if no company
        """
        if obj.companie:
            return f"{obj.companie.name} - {obj.companie.type}"
        return None

    def get_created_by(self, obj) -> str:
        """
        Retrieves creator's name for list view.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            str: Creator's full name, or None if not available
        """
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def get_updated_by(self, obj) -> str:
        """
        Retrieves updater's name for list view.
        
        Args:
            obj: Employee instance being serialized
            
        Returns:
            str: Updater's full name, or None if not available
        """
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}"
        return None