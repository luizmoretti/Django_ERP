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
    
    Handles serialization of delivery checkpoints which track location,
    status, and other details of a delivery at specific points in time.
    """
    id = serializers.UUIDField(read_only=True)
    
    companie = serializers.PrimaryKeyRelatedField(queryset=Companie.objects.all(), required=True, write_only=True)
    companie_name = serializers.SerializerMethodField(read_only=True)

    full_address = serializers.SerializerMethodField(read_only=False)

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
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_companie_name(self, obj):
        """Returns the human-readable companie name."""
        return obj.companie.name if obj.companie else None
    
    def get_full_address(self, obj):
        """Returns the full address of the companie."""
        return obj.get_full_address() if obj.get_full_address() else None
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new PickUpCompanieAddress instance.
        
        This method handles the creation of a new PickUpCompanieAddress instance
        and ensures that the full address is generated correctly.
        """
        try:
            companie = validated_data.pop('companie')
            full_address = validated_data.get('full_address')
            
            # Create the PickUpCompanieAddress instance
            pick_up_address = PickUpCompanieAddress.objects.create(companie=companie)
            
            # Set the full address
            pick_up_address.save()
            
            return pick_up_address
        except Exception as e:
            logger.error(f"Error creating PickUpCompanieAddress: {e}")
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

    create_by = serializers.PrimaryKeyRelatedField(queryset=Employeer.objects.all(), required=True, write_only=True)
    create_by_name = serializers.SerializerMethodField(read_only=True)

    update_by = serializers.PrimaryKeyRelatedField(queryset=Employeer.objects.all(), required=True, write_only=True)
    update_by_name = serializers.SerializerMethodField(read_only=True)

    pickup_address = PickUpCompanieAddressSerializer(many=True, required=False, read_only=True)
    
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
        ]
        read_only_fields = ['id', 'pickup_address', 'created_at', 'updated_at']

    def get_create_by_name(self, obj):
        """Returns the human-readable create_by name."""
        return obj.create_by.display_name() if obj.create_by else None
    
    def get_update_by_name(self, obj):
        """Returns the human-readable update_by name."""
        return obj.update_by.display_name() if obj.update_by else None
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new PickUpCompanieAddress instance.
        
        This method handles the creation of a new PickUpCompanieAddress instance
        and ensures that the full address is generated correctly.
        """
        try:
            
            # Create the PickUpCompanieAddress instance
            companie = Companie.objects.create(**validated_data)
            
            # Set the full address
            companie.save()
            
            return companie
        except Exception as e:
            logger.error(f"Error creating PickUpCompanieAddress: {e}")
            raise ValidationError("An error occurred while creating the address.")
        
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update an existing PickUpCompanieAddress instance.
        
        This method handles the update of an existing PickUpCompanieAddress instance
        and ensures that the full address is generated correctly.
        """
        try:
            # Update the PickUpCompanieAddress instance
            return super().update(instance, validated_data)
        except Exception as e:
            logger.error(f"Error updating PickUpCompanieAddress: {e}")
            raise ValidationError("An error occurred while updating the address.")