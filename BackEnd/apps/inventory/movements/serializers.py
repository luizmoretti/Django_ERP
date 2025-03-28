from rest_framework import serializers
from rest_framework.exceptions import APIException
from ..inflows.models import Inflow
from ..outflows.models import Outflow
from ..transfer.models import Transfer
import logging

logger = logging.getLogger(__name__)

class MovementSerializer(serializers.Serializer):
    """ Serializer for movements """
    id = serializers.UUIDField()
    date = serializers.DateTimeField(source="created_at", format="%d/%m/%Y")
    type = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        fields = [
            'id',
            'date',
            'type',
            'status',
            'origin',
            'destination',
        ]
        read_only_fields = fields
        
    def get_type(self, obj) -> str | None:
        if isinstance(obj, Inflow):
            return f'{obj.type}'
        elif isinstance(obj, Outflow):
            return f'{obj.type}'
        elif isinstance(obj, Transfer):
            return f'{obj.type}'
        return None
        
    def get_status(self, obj) -> str | None:
        if isinstance(obj, Inflow):
            return f'{obj.status}'
        elif isinstance(obj, Outflow):
            return f'{obj.status}'
        elif isinstance(obj, Transfer):
            return f'{obj.status}'
        return None
        
    def get_origin(self, obj) -> str | None:
        if isinstance(obj, Inflow):
            return f'{obj.origin.name}'
        elif isinstance(obj, Outflow):
            return f'{obj.origin.name}'
        elif isinstance(obj, Transfer):
            return f'{obj.origin.name}'
        return None
    
    def get_destination(self, obj) -> str | None:
        try:
            if isinstance(obj, Inflow):
                return f'{obj.destiny.name}' if hasattr(obj.destiny, 'name') else str(obj.destiny)
            elif isinstance(obj, Outflow):
                # Check that destiny exists and has the full_name attribute
                if hasattr(obj, 'destiny') and obj.destiny:
                    return f'{obj.destiny}' if hasattr(obj.destiny, 'full_name') else str(obj.destiny)
                return None
            elif isinstance(obj, Transfer):
                return f'{obj.destiny.name}' if hasattr(obj.destiny, 'name') else str(obj.destiny)
            return None
        except Exception as e:
            logger.error(f"[MOVEMENTS SERIALIZER] Error in get_destination: {str(e)}")
            return "Error retrieving destination"
    

