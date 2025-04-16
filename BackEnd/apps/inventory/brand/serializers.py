from rest_framework import serializers
from .models import Brand


class BrandSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(required=True)
    companie = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    
    def get_companie(self, obj) -> str | None:
        if obj.companie:
            return f'[{obj.companie.type}] {obj.companie.name}'
        return None
    
    def get_created_by(self, obj) -> str | None:
        if obj.created_by:
            return obj.created_by.name
        return None
    
    def get_updated_by(self, obj) -> str | None:
        if obj.updated_by:
            return obj.updated_by.name
        return None
    
    class Meta:
        model = Brand
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'companie',
        ]
        read_only_fields = ['id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by']
        
        
    def create(self, validated_data) -> Brand:
        return Brand.objects.create(**validated_data)
    
    def update(self, instance, validated_data) -> Brand:
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance