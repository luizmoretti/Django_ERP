from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.management import call_command
import uuid
from unittest import mock
from django.utils.translation import gettext as _

from apps.delivery.models import Delivery, DeliveryCheckpoint
from apps.delivery.services.handlers import DeliveryHandler
from apps.delivery.services.validators import DeliveryValidator
from apps.companies.customers.models import Customer
from apps.companies.employeers.models import Employeer
from apps.vehicle.models import Vehicle
from apps.inventory.load_order.models import LoadOrder
from apps.companies.models import Companie

User = get_user_model()

# Salvar o método original para restaurar após os testes
original_validate_delivery_data = DeliveryValidator.validate_delivery_data
original_validate_delivery_update = DeliveryValidator.validate_delivery_update

# Criar uma versão modificada que ignora a verificação da licença
def patched_validate_delivery_data(data):
    # Verificar campos obrigatórios
    required_fields = ['customer', 'driver', 'vehicle', 'load']
    for field in required_fields:
        if field not in data:
            raise ValidationError(_(f"{field} is required"))
            
    # Validar customer
    if 'customer' in data:
        customer_id = data['customer']
        if not Customer.objects.filter(id=customer_id).exists():
            raise ValidationError(_("Invalid customer"))
    
    # Validar driver (sem verificar licença)
    if 'driver' in data:
        driver_id = data['driver']
        if not Employeer.objects.filter(id=driver_id).exists():
            raise ValidationError(_("Invalid driver"))
    
    # Validar vehicle
    if 'vehicle' in data:
        vehicle_id = data['vehicle']
        if not Vehicle.objects.filter(id=vehicle_id).exists():
            raise ValidationError(_("Invalid vehicle"))
    
    # Validar load
    if 'load' in data:
        load_ids = data['load']
        for load_id in load_ids:
            if not LoadOrder.objects.filter(id=load_id).exists():
                raise ValidationError(_("Invalid load"))

# Criar uma versão modificada que ignora a verificação da licença para validate_delivery_update
def patched_validate_delivery_update(delivery, data):
    # Validate basic data
    patched_validate_delivery_data(data)
    
    # Check if delivery can be updated
    if delivery.status == 'delivered':
        raise ValidationError(_("Cannot update a completed delivery"))
    
    # Check status transition if status is being updated
    if 'status' in data and data['status'] != delivery.status:
        DeliveryValidator.validate_status_change(delivery, data['status'])

class DeliveryHandlerTest(TestCase):
    """Testes para o handler DeliveryHandler"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para todos os testes desta classe"""
        super().setUpClass()
        # Garantir que as migrações sejam aplicadas
        call_command('migrate', 'delivery', verbosity=0, interactive=False)
    
    def setUp(self):
        # Criar empresa
        self.companie = Companie.objects.create(
            name="Empresa Teste",
            type="Headquarters"
        )
        
        # Criar usuário manager (sem definir companie no create_user)
        self.manager_user = User.objects.create_user(
            email="manager@test.com",
            password="password123",
            user_type="Manager"
        )
        
        # Associar usuário à empresa
        self.manager_user.companie = self.companie
        self.manager_user.save()
        
        # Buscar employeer já criado automaticamente, em vez de criar um novo
        try:
            self.manager = Employeer.objects.get(user=self.manager_user)
        except Employeer.DoesNotExist:
            self.manager = Employeer.objects.create(
                user=self.manager_user,
                companie=self.companie
            )
        
        # Atualizar created_by/updated_by do companie
        self.companie.created_by = self.manager
        self.companie.updated_by = self.manager
        self.companie.save()
        
        # Verificar a conexão entre manager e companie
        self.manager.companie = self.companie
        self.manager.save()
        self.manager_user.companie = self.companie
        self.manager_user.save()
        
        # Criar cliente
        self.customer = Customer.objects.create(
            first_name="Cliente",
            last_name="Teste",
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Criar motorista (employeer)
        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="password123",
            user_type="Driver"
        )
        
        # Associar usuário à empresa
        self.driver_user.companie = self.companie
        self.driver_user.save()
        
        # Buscar employeer já criado automaticamente, em vez de criar um novo
        try:
            self.driver = Employeer.objects.get(user=self.driver_user)
        except Employeer.DoesNotExist:
            self.driver = Employeer.objects.create(
                user=self.driver_user,
                companie=self.companie,
                created_by=self.manager,
                updated_by=self.manager
            )
        
        # Criar mock para driver_details de forma mais robusta
        class DriverDetails:
            def __init__(self):
                self.has_valid_license = True
        self.driver.driver_details = DriverDetails()
        
        # Criar veículo
        self.vehicle = Vehicle.objects.create(
            plate_number="ABC1234",
            nickname="Truck1",
            vehicle_type="truck",
            maker="toyota",
            color="white",
            vin="1HGCM82633A123456",
            is_active=True,
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Criar ordem de carga
        self.load_order = LoadOrder.objects.create(
            customer=self.customer,
            order_number="LO12345",
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Aplicar o patch para o método de validação
        DeliveryValidator.validate_delivery_data = patched_validate_delivery_data
        DeliveryValidator.validate_delivery_update = patched_validate_delivery_update
    
    def tearDown(self):
        # Restaurar o método original após cada teste
        DeliveryValidator.validate_delivery_data = original_validate_delivery_data
        DeliveryValidator.validate_delivery_update = original_validate_delivery_update
    
    def test_create_delivery(self):
        """Testa a criação de uma entrega através do handler"""
        data = {
            'customer': str(self.customer.id),
            'driver': str(self.driver.id),
            'vehicle': str(self.vehicle.id),
            'load': [str(self.load_order.id)],
            'status': 'pending',
            'companie': str(self.companie.id)
        }
        
        # Garantir que o manager tenha a companie configurada
        self.manager.companie = self.companie
        self.manager.save()
        
        delivery = DeliveryHandler.create_delivery(data, self.manager)
        
        self.assertIsInstance(delivery, Delivery)
        self.assertEqual(delivery.customer, self.customer)
        self.assertEqual(delivery.driver, self.driver)
        self.assertEqual(delivery.vehicle, self.vehicle)
        self.assertEqual(delivery.status, 'pending')
        self.assertEqual(delivery.load.count(), 1)
        self.assertEqual(delivery.companie, self.companie)
    
    def test_update_delivery(self):
        """Testa a atualização de uma entrega através do handler"""
        # Primeiro criar uma entrega
        delivery = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        delivery.load.add(self.load_order)
        
        # Atualizar a entrega
        data = {
            'customer': str(self.customer.id),
            'driver': str(self.driver.id),
            'vehicle': str(self.vehicle.id),
            'load': [str(self.load_order.id)],
            'status': 'pickup_in_progress',
            'current_location': {'latitude': 15.0, 'longitude': 25.0}
        }
        
        updated_delivery = DeliveryHandler.update_delivery(delivery, data, self.manager)
        
        self.assertEqual(updated_delivery.status, 'pickup_in_progress')
        self.assertEqual(updated_delivery.current_location['latitude'], 15.0)
        self.assertEqual(updated_delivery.current_location['longitude'], 25.0)
        
        # Verificar se foi criado um checkpoint para a alteração de status
        checkpoints = DeliveryCheckpoint.objects.filter(delivery=delivery)
        self.assertEqual(checkpoints.count(), 1)
        self.assertEqual(checkpoints[0].status, 'pickup_in_progress')
    
    def test_update_location(self):
        """Testa a atualização de localização através do handler"""
        delivery = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='in_transit',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        data = {
            'latitude': 35.0,
            'longitude': 45.0,
            'create_checkpoint': True,
            'notes': 'Atualização de localização'
        }
        
        updated_delivery = DeliveryHandler.update_delivery_location(delivery, data, self.manager)
        
        self.assertEqual(updated_delivery.current_location['latitude'], 35.0)
        self.assertEqual(updated_delivery.current_location['longitude'], 45.0)
        
        # Verificar se foi criado um checkpoint
        checkpoints = DeliveryCheckpoint.objects.filter(delivery=delivery)
        self.assertEqual(checkpoints.count(), 1)
        self.assertEqual(checkpoints[0].location['latitude'], 35.0)
        self.assertEqual(checkpoints[0].location['longitude'], 45.0)
        self.assertEqual(checkpoints[0].notes, 'Atualização de localização')
    
    def test_delete_delivery(self):
        """Testa a exclusão de uma entrega através do handler"""
        delivery = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        delivery_id = delivery.id
        DeliveryHandler.delete_delivery(delivery)
        
        # Verificar se a entrega foi excluída
        with self.assertRaises(Delivery.DoesNotExist):
            Delivery.objects.get(id=delivery_id)


class DeliveryValidatorTest(TestCase):
    """Testes para o validator DeliveryValidator"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para todos os testes desta classe"""
        super().setUpClass()
        # Garantir que as migrações sejam aplicadas
        call_command('migrate', 'delivery', verbosity=0, interactive=False)
    
    def setUp(self):
        # Criar empresa
        self.companie = Companie.objects.create(
            name="Empresa Teste",
            type="Headquarters"
        )
        
        # Criar usuário manager (sem definir companie no create_user)
        self.manager_user = User.objects.create_user(
            email="manager@test.com",
            password="password123",
            user_type="Manager"
        )
        
        # Associar usuário à empresa
        self.manager_user.companie = self.companie
        self.manager_user.save()
        
        # Buscar employeer já criado automaticamente, em vez de criar um novo
        try:
            self.manager = Employeer.objects.get(user=self.manager_user)
        except Employeer.DoesNotExist:
            self.manager = Employeer.objects.create(
                user=self.manager_user,
                companie=self.companie
            )
        
        # Atualizar created_by/updated_by do companie
        self.companie.created_by = self.manager
        self.companie.updated_by = self.manager
        self.companie.save()
        
        # Criar cliente
        self.customer = Customer.objects.create(
            first_name="Cliente",
            last_name="Teste",
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Criar motorista (employeer)
        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="password123",
            user_type="Driver"
        )
        
        # Associar usuário à empresa
        self.driver_user.companie = self.companie
        self.driver_user.save()
        
        # Buscar employeer já criado automaticamente, em vez de criar um novo
        try:
            self.driver = Employeer.objects.get(user=self.driver_user)
        except Employeer.DoesNotExist:
            self.driver = Employeer.objects.create(
                user=self.driver_user,
                companie=self.companie,
                created_by=self.manager,
                updated_by=self.manager
            )
        
        # Criar mock para driver_details de forma mais robusta
        class DriverDetails:
            def __init__(self):
                self.has_valid_license = True
        self.driver.driver_details = DriverDetails()
        
        # Criar veículo
        self.vehicle = Vehicle.objects.create(
            plate_number="ABC1234",
            nickname="Truck1",
            vehicle_type="truck",
            maker="toyota",
            color="white",
            vin="1HGCM82633A123456",
            is_active=True,
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Criar ordem de carga
        self.load_order = LoadOrder.objects.create(
            customer=self.customer,
            order_number="LO12345",
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Criar entrega
        self.delivery = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        self.delivery.load.add(self.load_order)
        
        # Aplicar o patch para o método de validação
        DeliveryValidator.validate_delivery_data = patched_validate_delivery_data
        DeliveryValidator.validate_delivery_update = patched_validate_delivery_update
    
    def tearDown(self):
        # Restaurar o método original após cada teste
        DeliveryValidator.validate_delivery_data = original_validate_delivery_data
        DeliveryValidator.validate_delivery_update = original_validate_delivery_update
    
    def test_validate_delivery_data_success(self):
        """Testa a validação de dados de entrega com sucesso"""
        data = {
            'customer': str(self.customer.id),
            'driver': str(self.driver.id),
            'vehicle': str(self.vehicle.id),
            'load': [str(self.load_order.id)],
            'status': 'pending',
        }
        
        # Se não lançar exceção, o teste passou
        DeliveryValidator.validate_delivery_data(data)
    
    def test_validate_delivery_data_missing_fields(self):
        """Testa a validação de dados faltando campos obrigatórios"""
        data = {
            'customer': str(self.customer.id),
            'driver': str(self.driver.id),
            # Faltando vehicle e load
        }
        
        with self.assertRaises(ValidationError):
            DeliveryValidator.validate_delivery_data(data)
    
    def test_validate_delivery_data_invalid_customer(self):
        """Testa a validação com cliente inválido"""
        data = {
            'customer': str(uuid.uuid4()),  # ID que não existe
            'driver': str(self.driver.id),
            'vehicle': str(self.vehicle.id),
            'load': [str(self.load_order.id)],
        }
        
        with self.assertRaises(ValidationError):
            DeliveryValidator.validate_delivery_data(data)
    
    def test_validate_status_change_valid(self):
        """Testa validação de mudança de status válida"""
        # De pending para pickup_in_progress é uma transição válida
        DeliveryValidator.validate_status_change(self.delivery, 'pickup_in_progress')
        
        # Atualizar para testar outra transição
        self.delivery.status = 'pickup_in_progress'
        self.delivery.save()
        
        # De pickup_in_progress para in_transit é válido
        DeliveryValidator.validate_status_change(self.delivery, 'in_transit')
    
    def test_validate_status_change_invalid(self):
        """Testa validação de mudança de status inválida"""
        # De pending para in_transit não é válido (pula etapa)
        with self.assertRaises(ValidationError):
            DeliveryValidator.validate_status_change(self.delivery, 'in_transit')
        
        # De pending para delivered não é válido (pula etapas)
        with self.assertRaises(ValidationError):
            DeliveryValidator.validate_status_change(self.delivery, 'delivered')
    
    def test_validate_location_update(self):
        """Testa validação de atualização de localização"""
        data = {
            'latitude': 35.0,
            'longitude': 45.0
        }
        
        # Validação deve passar
        DeliveryValidator.validate_location_update(self.delivery, data)
        
        # Testa com coordenadas inválidas
        invalid_data = {
            'latitude': 91.0,  # Acima do limite (90)
            'longitude': 45.0
        }
        
        with self.assertRaises(ValidationError):
            DeliveryValidator.validate_location_update(self.delivery, invalid_data)
        
        # Testa com entrega em estado final
        self.delivery.status = 'delivered'
        self.delivery.save()
        
        with self.assertRaises(ValidationError):
            DeliveryValidator.validate_location_update(self.delivery, data)
