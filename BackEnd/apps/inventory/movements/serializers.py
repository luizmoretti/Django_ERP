from rest_framework import serializers
from .models import Movement

class MovementSerializer(serializers.ModelSerializer):
    """Base serializer for movements"""
    
    class Meta:
        model = Movement
        fields = [
            'id',
            'date',
            'type',
            'origin',
            'destination',
            'status',
            'total_items',
            'total_value',
            'data'
        ]

class MovementListSerializer(serializers.ModelSerializer):
    """Simplified serializer for movement listings"""
    
    class Meta:
        model = Movement
        fields = [
            'id',
            'date',
            'type',
            'origin',
            'destination',
            'status',
            'total_items',
            'total_value'
        ]