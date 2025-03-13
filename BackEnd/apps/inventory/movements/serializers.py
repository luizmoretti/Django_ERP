from rest_framework import serializers


class MovementSerializer(serializers.Serializer):
    """Base serializer for movements"""
    id = serializers.UUIDField()
    date = serializers.DateTimeField()
    type = serializers.CharField()
    origin = serializers.CharField()
    destination = serializers.CharField()
    status = serializers.CharField()
    total_items = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    data = serializers.JSONField()

class MovementListSerializer(serializers.Serializer):
    """Simplified serializer for movement listings"""
    id = serializers.UUIDField()
    date = serializers.DateTimeField()
    type = serializers.CharField()
    origin = serializers.CharField()
    destination = serializers.CharField()
    status = serializers.CharField()
    total_items = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=10, decimal_places=2)