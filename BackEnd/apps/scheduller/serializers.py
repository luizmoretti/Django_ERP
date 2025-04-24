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
    
    
class SchedullerSerializer(serializers.ModelSerializer):
    jobs = JobsTypeSchedullerRegisterSerializer(many=True, read_only=True)
    jobs_data = serializers.PrimaryKeyRelatedField(
        queryset=JobsTypeSchedullerRegister.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    companie = serializers.SerializerMethodField()
    
    class Meta:
        model = Scheduller
        fields = [
            'id', 'start_time', 'end_time', 'date', 'location',
            'jobs', 'jobs_data', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'companie'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'companie']
        
    def get_created_by(self, obj):
        if obj.created_by:
            return obj.created_by.name
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            return obj.updated_by.name
        return None
    
    def get_companie(self, obj):
        if obj.companie:
            return obj.companie.name
        return None
    
    def validate(self, attrs):
        # Validate time consistency if both are provided
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError('End time must be after start time')
        
        return attrs
    
    def create(self, validated_data):
        jobs_data = validated_data.pop('jobs_data', None)
        
        scheduller = Scheduller.objects.create(**validated_data)
        
        if jobs_data:
            scheduller.jobs.set(jobs_data)
            
        return scheduller
    
    def update(self, instance, validated_data):
        jobs_data = validated_data.pop('jobs_data', None)
        
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.date = validated_data.get('date', instance.date)
        instance.location = validated_data.get('location', instance.location)
        
        instance.save()
        
        if jobs_data is not None:
            instance.jobs.set(jobs_data)
            
        return instance
        
    