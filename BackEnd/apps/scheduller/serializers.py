from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Scheduller, JobsTypeSchedullerRegister


class JobsTypeSchedullerRegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    
    class Meta:
        model = JobsTypeSchedullerRegister
        fields = ['id', 'name']
        read_only_fields = ['id']
        
    def validate(self, attrs):
        name = attrs.get('name')
        if not name:
            raise ValidationError('Name is required')
        elif JobsTypeSchedullerRegister.objects.filter(name=name).exists():
            raise ValidationError('Name already exists')
        return attrs
        
    