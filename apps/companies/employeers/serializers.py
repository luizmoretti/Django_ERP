from rest_framework import serializers
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from apps.accounts.models import NormalUser
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class EmployeerSerializer(serializers.ModelSerializer):
    """
    Serializer centralizado para operações com funcionários.
    
    Este serializador fornece todas as funcionalidades necessárias para:
    - Listagem de funcionários
    - Criação de funcionários
    - Atualização de funcionários
    - Detalhamento de funcionários
    
    Atributos:
        id (UUIDField): Identificador único do funcionário (somente leitura)
        name (CharField): Nome completo do funcionário
        id_number (CharField): Número de identificação do funcionário
        date_of_birth (DateField): Data de nascimento
        age (IntegerField): Idade calculada (somente leitura)
        
        # Informações de Contato
        phone (CharField): Telefone de contato
        email (EmailField): Email de contato
        
        # Informações de Endereço
        address (CharField): Endereço
        city (CharField): Cidade
        state (CharField): Estado
        zip_code (CharField): CEP
        country (CharField): País
        
        # Informações de Usuário
        user (SerializerMethodField): Dados do usuário associado (somente leitura)
        user_id (UUIDField): ID do usuário (somente escrita)
        
        # Informações da Empresa
        companie (SerializerMethodField): Dados da empresa (somente leitura)
        
        # Campos de Auditoria
        created_at (DateTimeField): Data de criação
        updated_at (DateTimeField): Data de última atualização
        created_by_name (SerializerMethodField): Nome de quem criou
        updated_by_name (SerializerMethodField): Nome de quem atualizou por último
    """
    # Campos Básicos
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(required=False)
    id_number = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=True)
    age = serializers.IntegerField(read_only=True)
    
    hire_date = serializers.DateField(required=False)
    termination_date = serializers.DateField(required=False)
    payroll_schedule = serializers.CharField(required=False)
    payment_type = serializers.CharField(required=False)
    rate = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    
    # Campos de Contato
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    
    # Campos de Endereço
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    
    # Campos de Relacionamento
    user = serializers.PrimaryKeyRelatedField(queryset=NormalUser.objects.all(), required=False, write_only=True)
    _user = serializers.SerializerMethodField(read_only=True)
    
    # Campos de Auditoria
    _created_by = serializers.SerializerMethodField(read_only=True)
    _updated_by = serializers.SerializerMethodField(read_only=True)
    _companie = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employeer
        fields = [
            # Campos Básicos
            'id', 'name', 'id_number', 'date_of_birth', 'age',
            'hire_date', 'termination_date', 'payroll_schedule', 
            'payment_type', 'rate',
            
            # Campos de Contato
            'phone', 'email',
            
            # Campos de Endereço
            'address', 'city', 'state', 'zip_code', 'country',
            
            # Campos de Relacionamento
            'user', '_user',
            
            # Campos de Auditoria
            'created_at', 'updated_at', '_created_by', '_updated_by', '_companie'
        ]
        read_only_fields = [
            'id', 
            'age', 
            '_user',
            'created_at', 
            'updated_at',
            '_created_by',
            '_updated_by',
            '_companie'
        ]

    def get__user(self, obj) -> dict:
        """Retorna informações do usuário associado"""
        if obj.user:
            return {
                'username': obj.user.username,
                'user_type': obj.user.user_type,
                'is_active': obj.user.is_active
            }
        return None

    def get__companie(self, obj) -> str:
        """Retorna informações formatadas da empresa"""
        if obj.companie:
            return f"[{obj.companie.type}] {obj.companie.name}"
        return None

    def get__created_by(self, obj) -> str | None:
        """Retorna o nome de quem criou o registro"""
        if obj.created_by:
            return f"{obj.created_by.name}"
        return None

    def get__updated_by(self, obj) -> str | None:
        """Retorna o nome de quem atualizou o registro"""
        if obj.updated_by:
            return f"{obj.updated_by.name}"
        return None

    def validate_email(self, value):
        """Valida se o email é único"""
        if not value:
            return value
            
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value
            
        if Employeer.objects.filter(email=value).exists():
            raise ValidationError("This email is already in use")
        return value

    def validate_user(self, value):
        """Validates that the user exists and is not associated with another employee"""
        try:
            user = NormalUser.objects.get(id=value, is_active=True)
            
            existing = Employeer.objects.filter(user_id=value)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
                
            if existing.exists():
                raise ValidationError("This user is already associated with another employee")
                
            return value
        except NormalUser.DoesNotExist:
            raise ValidationError("Invalid user")

    
    def create(self, validated_data):
        """Cria um novo funcionário"""
        user_id = validated_data.pop('user')
        instance = self.Meta.model(**validated_data)
        instance.user_id = user_id
        instance.save()
        return instance

    
    def update(self, instance, validated_data):
        """Atualiza um funcionário existente"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance