from rest_framework import serializers
from apps.companies.customers.models import Customer, CustomerBillingAddress, CustomerProjectAddress, CustomerLeads
from rest_framework.exceptions import ValidationError

class CustomerBillingAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerBillingAddress model.
    """
    class Meta:
        model = CustomerBillingAddress
        fields = [
            'address', 'city', 'state', 'zip_code',
            'country', 'phone', 'email'
        ]

class CustomerProjectAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerProjectAddress model.
    """
    class Meta:
        model = CustomerProjectAddress
        fields = [
            'address', 'city', 'state', 'zip_code',
            'country', 'phone', 'email'
        ]

class CustomerSerializer(serializers.ModelSerializer):
    """
    Unified serializer for all customer operations.
    
    This serializer handles all customer-related operations including:
    - Create with optional custom addresses
    - Update with address management
    - List view with company and user information
    - Detailed view with full address data
    
    Attributes:
        id (UUIDField): Read-only customer identifier
        first_name (CharField): Required customer first name
        last_name (CharField): Required customer last name
        address (CharField): Required physical address
        city (CharField): Required city location
        state (CharField): Required state location
        zip_code (CharField): Required postal/ZIP code
        country (CharField): Optional country, defaults to 'USA'
        phone (CharField): Optional contact phone
        email (EmailField): Optional contact email
        another_billing_address (BooleanField): Flag for custom billing address
        another_shipping_address (BooleanField): Flag for custom shipping address
        is_active (BooleanField): Indicates if customer is active
        billing_address_data (CustomerBillingAddressSerializer): Nested billing address data
        shipping_address_data (CustomerProjectAddressSerializer): Nested shipping address data
        companie (SerializerMethodField): Company information
        created_by (SerializerMethodField): Creator's full name
        updated_by (SerializerMethodField): Last updater's full name
        created_at (DateTimeField): Creation timestamp
        updated_at (DateTimeField): Last update timestamp
    """
    # Basic fields
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    zip_code = serializers.CharField(required=True)
    country = serializers.CharField(required=False, default='USA')
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    another_billing_address = serializers.BooleanField(required=False, default=False)
    another_shipping_address = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)
    
    # Nested address serializers
    billing_address_data = CustomerBillingAddressSerializer(
        source='billing_address.first',
        read_only=True  # Read-only serialization
    )
    _billing_address_data = serializers.JSONField(
        write_only=True, # Write-only for creation and update
        required=False
    )
    shipping_address_data = CustomerProjectAddressSerializer(
        source='project_address.first',
        read_only=True  # Read-only serialization
    )
    _shipping_address_data = serializers.JSONField(
        write_only=True, # Write-only for creation and update
        required=False
    )
    
    # Additional fields
    companie = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Customer
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'address', 
            'city', 
            'state', 
            'zip_code',
            'country', 
            'phone', 
            'email', 
            
            # Other Addresses Fields
            'another_billing_address', 
            'billing_address_data',
            '_billing_address_data',
            'another_shipping_address',
            'shipping_address_data',
            '_shipping_address_data',
            
            'is_active',
            'companie',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'billing_address_data',
            'shipping_address_data',
            'companie',
            'created_by',
            'created_at',
            'updated_by',
            'updated_at'
        ]
    def validate(self, data):
        """
        Validate the data before create/update operations.
        
        Ensures that address data is provided when custom addresses are enabled.
        
        Args:
            data: Dictionary of input data
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        # Map write-only fields to their public names
        if '_billing_address_data' in data:
            data['billing_address_data'] = data.pop('_billing_address_data')
        if '_shipping_address_data' in data:
            data['shipping_address_data'] = data.pop('_shipping_address_data')
            
        # Validate billing address data
        if data.get('another_billing_address'):
            billing_data = data.get('billing_address_data')
            if not billing_data:
                raise serializers.ValidationError({
                    'billing_address_data': 'This field is required when another_billing_address is True.'
                })
                
        # Validate shipping address data
        if data.get('another_shipping_address'):
            shipping_data = data.get('shipping_address_data')
            if not shipping_data:
                raise serializers.ValidationError({
                    'shipping_address_data': 'This field is required when another_shipping_address is True.'
                })
                
        return data
    
    
    def get_companie(self, obj) -> str:
        """
        Retrieves formatted company information.
        
        Args:
            obj: Customer instance being serialized
            
        Returns:
            str: Company name and type, or None if no company
        """
        if obj.companie:
            return f"[{obj.companie.type}] {obj.companie.name}"
        return None
    
    def get_created_by(self, obj) -> str:
        """
        Retrieves creator's name.
        
        Args:
            obj: Customer instance being serialized
            
        Returns:
            str: Creator's full name, or None if not available
        """
        return f"{obj.created_by.name}" if obj.created_by else None
    
    def get_updated_by(self, obj) -> str:
        """
        Retrieves last updater's name.
        
        Args:
            obj: Customer instance being serialized
            
        Returns:
            str: Last updater's full name, or None if not available
        """
        return f"{obj.updated_by.name}" if obj.updated_by else None

    def create(self, validated_data):
        """
        Creates a new customer with associated addresses.
        
        Args:
            validated_data: Dictionary of validated customer data
            
        Returns:
            Customer: Created customer instance
            
        Raises:
            ValidationError: If validation fails
        """
        billing_data = validated_data.pop('billing_address_data', {})
        shipping_data = validated_data.pop('shipping_address_data', {})
        
        try:
            customer = Customer.objects.create(**validated_data)
            
            CustomerBillingAddress.objects.create(
                customer=customer,
                **billing_data if customer.another_billing_address else {}
            )
            
            CustomerProjectAddress.objects.create(
                customer=customer,
                **shipping_data if customer.another_shipping_address else {}
            )
            
            return customer
            
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        """
        Updates customer and associated addresses.
        
        Args:
            instance: Existing customer instance
            validated_data: Dictionary of validated update data
            
        Returns:
            Customer: Updated customer instance
        """
        billing_data = validated_data.pop('billing_address_data', {})
        shipping_data = validated_data.pop('shipping_address_data', {})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if instance.another_billing_address:
            billing_addr = instance.billing_address.first()
            if billing_addr and billing_data:
                for attr, value in billing_data.items():
                    setattr(billing_addr, attr, value)
                billing_addr.save()
                
        if instance.another_shipping_address:
            shipping_addr = instance.project_address.first()
            if shipping_addr and shipping_data:
                for attr, value in shipping_data.items():
                    setattr(shipping_addr, attr, value)
                shipping_addr.save()
        
        return instance
    
class CustomerLeadsSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerLeads model.
    
    This serializer handles operations related to business leads gathered from 
    external sources such as Google Local Search. It manages both the display
    of lead information and the creation/updating of lead records.
    
    Attributes:
        id (UUIDField): Read-only lead identifier
        name (CharField): Required business name
        address (CharField): Business address
        phone (CharField): Business phone number
        website (CharField): Business website URL
        hours (CharField): Business operating hours
        rating (CharField): Business rating 
        reviews (CharField): Number of reviews
        category (CharField): Business category or type
        place_id (CharField): Google Maps place ID
        notes (CharField): Additional notes or observations
        status (CharField): Lead status (choices from LEAD_STATUS_CHOICES)
        created_by (SerializerMethodField): Creator's name
        updated_by (SerializerMethodField): Last updater's name
        companie (SerializerMethodField): Company name
        created_at (DateTimeField): Creation timestamp
        updated_at (DateTimeField): Last update timestamp
    """
    # Basic fields are handled by ModelSerializer
    
    # Audit fields
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    companie = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = CustomerLeads
        fields = [
            'id',
            'name',
            'address',
            'phone',
            'website',
            'hours',
            'rating',
            'reviews',
            'category',
            'place_id',
            'notes',
            'status',
            'created_by',
            'updated_by',
            'companie',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_by',
            'updated_by',
            'companie',
            'created_at',
            'updated_at'
        ]
    
    def get_created_by(self, obj) -> str:
        """Returns the human-readable created_by name."""
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return "Created by system"
    
    def get_updated_by(self, obj) -> str:
        """Returns the human-readable updated_by name."""
        if obj.updated_by:
            return obj.updated_by.user.get_full_name()
        return "Created by system"
    
    def get_companie(self, obj):
        """
        Returns the name of the company the lead belongs to.
        
        Args:
            obj: The CustomerLeads instance
            
        Returns:
            str: Company name or None if not available
        """
        if obj.companie:
            return f"[{obj.companie.type}] {obj.companie.name}"
        return None
    
    def validate_status(self, value):
        """
        Validates the status value against allowed choices.
        
        Args:
            value: The status value to validate
            
        Returns:
            str: The validated status value
            
        Raises:
            ValidationError: If status is invalid
        """
        from django.apps import apps
        model = apps.get_model('customers', 'CustomerLeads')
        valid_choices = [choice[0] for choice in model._meta.get_field('status').choices]
        
        if value not in valid_choices:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_choices)}")
        
        return value
    
    def validate(self, data):
        """
        Performs complete validation of the lead data.
        
        Args:
            data: The data to validate
            
        Returns:
            dict: The validated data
            
        Raises:
            ValidationError: If validation fails
        """
        # Name is required
        if not data.get('name'):
            raise ValidationError({'name': 'Business name is required'})
            
        # Additional validations can be added here
        
        return data