from rest_framework import serializers

from .models import PickUpCompanieAddress, Companie
from apps.companies.employeers.models import Employeer

from rest_framework.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class PickUpCompanieAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the PickUpCompanieAddress model.
    
    Handles serialization of pickup addresses for companies, maintaining
    consistency with the model structure.
    """
    id = serializers.UUIDField(read_only=True)
    
    companie = serializers.PrimaryKeyRelatedField(queryset=Companie.objects.all(), required=True, write_only=True)
    companie_name = serializers.SerializerMethodField(read_only=True)

    # full_address is read-only because it is calculated automatically in the model
    full_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PickUpCompanieAddress
        fields = [
            'id',
            'companie',
            'companie_name',
            'full_address',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_address']

    def get_companie_name(self, obj):
        """Returns the human-readable companie name."""
        return obj.companie.name if obj.companie else None
    
    def get_full_address(self, obj):
        """Returns the full address of the companie."""
        # Use the model method if available, otherwise try the stored field
        if hasattr(obj, 'get_full_address') and callable(getattr(obj, 'get_full_address')):
            return obj.get_full_address()
        return obj.full_address if obj.full_address else None
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new PickUpCompanieAddress instance.
        
        Args:
            validated_data (dict): Validated data for creating the instance
            
        Returns:
            PickUpCompanieAddress: Created instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            companie = validated_data.get('companie')
            
            # Create the PickUpCompanieAddress instance
            pick_up_address = PickUpCompanieAddress.objects.create(companie=companie)
            
            # The model's save() method will fill the full_address
            
            return pick_up_address
        except Exception as e:
            logger.error(f"[COMPANIES SERIALIZERS] - Error creating PickUpCompanieAddress: {e}")
            raise ValidationError("An error occurred while creating the address.")
     
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update an existing PickUpCompanieAddress instance.
        
        This method handles the update of an existing PickUpCompanieAddress instance
        and ensures that the full address is generated correctly.
        """
        try:
            companie = validated_data.get('companie', instance.companie)
            
            # Update the PickUpCompanieAddress instance
            instance.companie = companie
            instance.save()
            
            return instance
        except Exception as e:
            logger.error(f"Error updating PickUpCompanieAddress: {e}")
            raise ValidationError("An error occurred while updating the address.")
        
class CompanieSerializer(serializers.ModelSerializer):
    """
    Serializer for the Companie model.
    
    Handles serialization of companie details including name, type, address,
    and other related information.
    """
    id = serializers.UUIDField(read_only=True)

    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)

    # Relationship with pickup addresses
    pickup_address = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Companie
        fields = [
            'id',
            'name',
            'type',
            'address',
            'state',
            'city',
            'zip_code',
            'country',
            'phone',
            'email',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'pickup_address'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

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
    
    def get_pickup_address(self, obj):
        """Returns the pickup addresses associated with this company."""
        addresses = obj.companie_pick_up_address.all()
        if addresses:
            return PickUpCompanieAddressSerializer(addresses, many=True).data
        return "No pickup addresses registered for this company"
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new Companie instance.
        
        Args:
            validated_data (dict): Validated data for creating the instance
            
        Returns:
            Companie: Created company instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Create the Companie instance
            companie = Companie.objects.create(**validated_data)
            
            return companie
        except Exception as e:
            logger.error(f"[COMPANIES SERIALIZERS] - Error creating Companie: {e}")
            raise ValidationError("An error occurred while creating the company.")
        
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update an existing Companie instance.
        
        Args:
            instance (Companie): Existing company instance
            validated_data (dict): Validated data for updating the instance
            
        Returns:
            Companie: Updated company instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Update the Companie instance
            return super().update(instance, validated_data)
        except Exception as e:
            logger.error(f"[COMPANIES SERIALIZERS] - Error updating Companie: {e}")
            raise ValidationError("An error occurred while updating the company.")