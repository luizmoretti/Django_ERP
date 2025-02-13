from django_rest_framework import serializers
from .models import Brand
from apps.companies.models import Companie
from apps.companies.employeers.models import Employeer


class BrandSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    companie = serializers.PrimaryKeyRelatedField(queryset=Companie.objects.all(), required=False)
    name = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_by = serializers.PrimaryKeyRelatedField(queryset=Employeer.objects.all(), required=False)
    updated_by = serializers.PrimaryKeyRelatedField(queryset=Employeer.objects.all(), required=False)
    class Meta:
        model = Brand
        fields = [
            'id',
            'companie',
            'name',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by'
        ]
        read_only_fields = ['id', 'companie', 'created_at', 'updated_at', 'created_by', 'updated_by']