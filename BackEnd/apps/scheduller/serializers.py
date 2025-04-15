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
    
    def create(self, validated_data) -> JobsTypeSchedullerRegister:
        return JobsTypeSchedullerRegister.objects.create(**validated_data)
    
    def update(self, instance, validated_data) -> JobsTypeSchedullerRegister:
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
        
    