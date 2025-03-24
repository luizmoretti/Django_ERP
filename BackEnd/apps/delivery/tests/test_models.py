import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.delivery.models import Delivery, DeliveryCheckpoint
from apps.companies.customers.models import Customer
from apps.companies.employeers.models import Employeer
from apps.vehicle.models import Vehicle
from apps.inventory.load_order.models import LoadOrder
from core.constants.choices import DELIVERY_STATUS_CHOICES
from apps.companies.models import Companie

User = get_user_model()

class DeliveryModelTest(TestCase):
    """Testes para o modelo Delivery"""
    
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
    
    def test_create_delivery(self):
        """Testa a criação de uma entrega com campos obrigatórios"""
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
        
        self.assertIsInstance(delivery, Delivery)
        self.assertIsInstance(delivery.id, uuid.UUID)
        self.assertEqual(delivery.status, 'pending')
        self.assertEqual(delivery.customer, self.customer)
        self.assertEqual(delivery.driver, self.driver)
        self.assertEqual(delivery.vehicle, self.vehicle)
        self.assertEqual(delivery.load.count(), 1)
        
    def test_delivery_str_representation(self):
        """Testa a representação string do modelo Delivery"""
        delivery = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        expected_str = f'{self.customer.full_name} - {self.vehicle.nickname} - pending'
        self.assertEqual(str(delivery), expected_str)
    
    def test_delivery_ordering(self):
        """Testa a ordenação do modelo Delivery"""
        # Criar duas entregas com datas diferentes
        delivery1 = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Garantir que a segunda entrega tenha uma data posterior
        delivery2 = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Verificar se a ordenação está correta (-created_at)
        deliveries = Delivery.objects.all()
        self.assertEqual(deliveries[0], delivery2)
        self.assertEqual(deliveries[1], delivery1)


class DeliveryCheckpointModelTest(TestCase):
    """Testes para o modelo DeliveryCheckpoint"""
    
    def setUp(self):
        # Configuração similar ao DeliveryModelTest
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
        
        self.companie.created_by = self.manager
        self.companie.updated_by = self.manager
        self.companie.save()
        
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
        
        self.delivery = Delivery.objects.create(
            customer=self.customer,
            driver=self.driver,
            vehicle=self.vehicle,
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
    
    def test_create_checkpoint(self):
        """Testa a criação de um checkpoint"""
        checkpoint = DeliveryCheckpoint.objects.create(
            delivery=self.delivery,
            location={'latitude': 10.0, 'longitude': 20.0},
            status='pending',
            notes="Checkpoint inicial",
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        self.assertIsInstance(checkpoint, DeliveryCheckpoint)
        self.assertIsInstance(checkpoint.id, uuid.UUID)
        self.assertEqual(checkpoint.delivery, self.delivery)
        self.assertEqual(checkpoint.status, 'pending')
        self.assertEqual(checkpoint.notes, "Checkpoint inicial")
        self.assertEqual(checkpoint.location['latitude'], 10.0)
        self.assertEqual(checkpoint.location['longitude'], 20.0)
    
    def test_checkpoint_ordering(self):
        """Testa a ordenação do modelo DeliveryCheckpoint"""
        # Criar dois checkpoints
        checkpoint1 = DeliveryCheckpoint.objects.create(
            delivery=self.delivery,
            location={'latitude': 10.0, 'longitude': 20.0},
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        checkpoint2 = DeliveryCheckpoint.objects.create(
            delivery=self.delivery,
            location={'latitude': 15.0, 'longitude': 25.0},
            status='in_transit',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        # Verificar se a ordenação está correta (-created_at)
        checkpoints = DeliveryCheckpoint.objects.all()
        self.assertEqual(checkpoints[0], checkpoint2)
        self.assertEqual(checkpoints[1], checkpoint1)
