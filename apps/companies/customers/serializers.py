from rest_framework import serializers
from apps.companies.customers.models import Customer
from apps.companies.models import Companie


class BaseCustomerSerializer(serializers.ModelSerializer):
    """
    Base serializer for customer operations with common fields.
    
    This serializer provides the foundation for customer-related operations,
    implementing common fields and basic validation rules.
    
    Attributes:
        id (UUIDField): Read-only customer identifier
        first_name (CharField): Required customer first name
        last_name (CharField): Required customer last name
        address (CharField): Optional physical address
        city (CharField): Optional city location
        zip_code (CharField): Optional postal/ZIP code
        country (CharField): Optional country, defaults to 'USA'
        phone (CharField): Optional contact phone
        email (EmailField): Optional contact email
        created_at (DateTimeField): Read-only timestamp of creation
        updated_at (DateTimeField): Read-only timestamp of last update
        is_active (BooleanField): Optional field to indicate if the customer is active
    """
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'address', 'city', 'zip_code',
            'country', 'phone', 'email', 'created_at', 'updated_at', 'is_active'
        ]


class CustomerSerializer(BaseCustomerSerializer):
    """
    Complete customer serializer for CRUD operations.
    
    This serializer extends BaseCustomerSerializer to provide full customer
    management capabilities, including company and employee relationships.
    
    Attributes:
        All fields from BaseCustomerSerializer plus:
        companie (SerializerMethodField): Formatted company information
        companie_id (UUIDField): Write-only company identifier
        created_by (SerializerMethodField): Creator's full name
        created_by_id (UUIDField): Write-only creator identifier
        updated_by (SerializerMethodField): Last updater's full name
        updated_by_id (UUIDField): Write-only updater identifier
    
    Validation Rules:
        - Company ID must reference an active company
        - Created_by and updated_by must be valid employees
    """
    companie = serializers.SerializerMethodField()
    companie_id = serializers.UUIDField(write_only=True, required=False)
    created_by = serializers.SerializerMethodField()
    created_by_id = serializers.UUIDField(write_only=True, required=False)
    updated_by = serializers.SerializerMethodField()
    updated_by_id = serializers.UUIDField(write_only=True, required=False)

    class Meta(BaseCustomerSerializer.Meta):
        fields = BaseCustomerSerializer.Meta.fields + [
            'companie', 'companie_id',
            'created_by', 'created_by_id',
            'updated_by', 'updated_by_id'
        ]
    
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
            raise serializers.ValidationError("Invalid or inactive companie ID")
    
    def get_companie(self, obj) -> str:
        """
        Retrieves formatted company information.
        
        Args:
            obj: Customer instance being serialized
            
        Returns:
            str: Company name and type, or None if no company
        """
        if obj.companie:
            return f"{obj.companie.name} - {obj.companie.type}"
        return None

    def get_created_by(self, obj) -> str:
        """
        Retrieves the full name of the employee who created the record.
        
        Args:
            obj: Customer instance being serialized
            
        Returns:
            str: Creator's full name, or None if not available
        """
        if obj.created_by and obj.created_by.user:
            return f"{obj.created_by.user.first_name} {obj.created_by.user.last_name}"
        return None

    def get_updated_by(self, obj) -> str:
        """
        Retrieves the full name of the employee who last updated the record.
        
        Args:
            obj: Customer instance being serialized
            
        Returns:
            str: Updater's full name, or None if not available
        """
        if obj.updated_by and obj.updated_by.user:
            return f"{obj.updated_by.user.first_name} {obj.updated_by.user.last_name}"
        return None

    def create(self, validated_data):
        """
        Creates a new customer instance with relationships.
        
        Args:
            validated_data: Dictionary of validated customer data
            
        Returns:
            Customer: Created customer instance
        """
        companie_id = validated_data.pop('companie_id', None)
        created_by_id = validated_data.pop('created_by_id', None)
        updated_by_id = validated_data.pop('updated_by_id', None)

        instance = self.Meta.model(**validated_data)
        
        if companie_id:
            instance.companie_id = companie_id
        if created_by_id:
            instance.created_by_id = created_by_id
        if updated_by_id:
            instance.updated_by_id = updated_by_id

        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Updates existing customer instance.
        
        Args:
            instance: Existing customer instance to update
            validated_data: Dictionary of validated update data
            
        Returns:
            Customer: Updated customer instance
        """
        companie_id = validated_data.pop('companie_id', None)
        updated_by_id = validated_data.pop('updated_by_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if companie_id:
            instance.companie_id = companie_id
        if updated_by_id:
            instance.updated_by_id = updated_by_id

        instance.save()
        return instance


class ListAllCustomersSerializer(BaseCustomerSerializer):
    """
    Simplified serializer for customer listing operations.
    
    This serializer inherits from BaseCustomerSerializer and adds only
    the necessary relationship fields for list views. All fields are
    read-only to ensure data integrity in list operations.
    
    Attributes:
        All fields from BaseCustomerSerializer plus:
        companie (SerializerMethodField): Formatted company information
        created_by (SerializerMethodField): Creator's full name
        updated_by (SerializerMethodField): Last updater's full name
    """
    companie = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta(BaseCustomerSerializer.Meta):
        fields = BaseCustomerSerializer.Meta.fields + [
            'companie',
            'created_by',
            'updated_by',
        ]
        
        read_only_fields = [
            'created_by',
            'updated_by',
        ]

    def get_companie(self, obj) -> str:
        """
        Retrieves formatted company information for list view.
        
        Args:
            obj: Customer instance being serialized
            
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
            obj: Customer instance being serialized
            
        Returns:
            str: Creator's full name, or None if not available
        """
        return f"{obj.created_by.first_name} {obj.created_by.last_name}" if obj.created_by else None
    
    def get_updated_by(self, obj) -> str:
        """
        Retrieves last updater's name for list view.
        
        Args:
            obj: Customer instance being serialized
            
        Returns:
            str: Last updater's full name, or None if not available
        """
        return f"{obj.updated_by.first_name} {obj.updated_by.last_name}" if obj.updated_by else None
    