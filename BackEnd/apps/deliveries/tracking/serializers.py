from rest_framework import serializers
from .models import DeliveryLocationUpdate, DeliveryRoute, DeliveryStatusUpdate

class DeliveryLocationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for delivery location updates.
    """
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryLocationUpdate
        fields = [
            'id', 'delivery', 'vehicle', 'latitude', 'longitude',
            'accuracy', 'speed', 'heading', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_latitude(self, obj):
        """Returns the latitude of the geographic point."""
        if obj.location:
            return obj.location.y
        return None
    
    def get_longitude(self, obj):
        """Returns the longitude of the geographic point."""
        if obj.location:
            return obj.location.x
        return None

class DeliveryRouteSerializer(serializers.ModelSerializer):
    """
    Serializer for delivery routes.
    """
    class Meta:
        model = DeliveryRoute
        fields = [
            'id', 'delivery', 'estimated_distance', 'estimated_duration',
            'estimated_arrival', 'route_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class DeliveryStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for delivery status updates.
    """
    class Meta:
        model = DeliveryStatusUpdate
        fields = [
            'id', 'delivery', 'status', 'location_update',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']