import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIRequestFactory
from django.utils import timezone

from apps.delivery.models import Delivery, DeliveryCheckpoint
from apps.delivery.serializers import DeliverySerializer, DeliveryCheckpointSerializer
from apps.companies.customers.models import Customer
from apps.companies.employeers.models import Employeer
from apps.vehicle.models import Vehicle
from apps.inventory.load_order.models import LoadOrder
from apps.companies.models import Companie

User = get_user_model()

class DeliverySerializerTest(TestCase):
    """Testes para o serializador DeliverySerializer"""
    
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
        
        # Criar mock para driver_details
        self.driver.driver_details = type('', (), {'has_valid_license': True})()
        
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
        
        # Criar checkpoint
        self.checkpoint = DeliveryCheckpoint.objects.create(
            delivery=self.delivery,
            location={'latitude': 10.0, 'longitude': 20.0},
            status='pending',
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
        
        self.factory = APIRequestFactory()
    
    def test_delivery_serializer_contains_expected_fields(self):
        """Verifica se o serializador contém os campos esperados"""
        serializer = DeliverySerializer(instance=self.delivery)
        data = serializer.data
        
        expected_fields = [
            'id', 'customer_name', 'driver_name', 'vehicle_info',
            'load_info', 'status', 'status_display', 'current_location',
            'estimated_arrival', 'actual_arrival', 'checkpoints',
            'companie', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_delivery_serializer_create(self):
        """Testa a criação de uma entrega através do serializador"""
        data = {
            'customer': str(self.customer.id),
            'driver': str(self.driver.id),
            'vehicle': str(self.vehicle.id),
            'load': [str(self.load_order.id)],
            'status': 'pending',
        }
        
        request = self.factory.post('/deliveries/')
        request.user = self.manager_user
        
        serializer = DeliverySerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        delivery = serializer.save()
        self.assertIsInstance(delivery, Delivery)
        self.assertEqual(delivery.customer, self.customer)
        self.assertEqual(delivery.driver, self.driver)
        self.assertEqual(delivery.vehicle, self.vehicle)
        self.assertEqual(delivery.status, 'pending')
        self.assertEqual(delivery.load.count(), 1)
    
    def test_delivery_serializer_update(self):
        """Testa a atualização de uma entrega através do serializador"""
        data = {
            'customer': str(self.customer.id),
            'driver': str(self.driver.id),
            'vehicle': str(self.vehicle.id),
            'load': [str(self.load_order.id)],
            'status': 'pickup_in_progress',
            'current_location': {'latitude': 15.0, 'longitude': 25.0}
        }
        
        request = self.factory.put(f'/deliveries/{self.delivery.id}/')
        request.user = self.manager_user
        
        serializer = DeliverySerializer(instance=self.delivery, data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_delivery = serializer.save()
        self.assertEqual(updated_delivery.status, 'pickup_in_progress')
        self.assertEqual(updated_delivery.current_location['latitude'], 15.0)
        self.assertEqual(updated_delivery.current_location['longitude'], 25.0)


class DeliveryCheckpointSerializerTest(TestCase):
    """Testes para o serializador DeliveryCheckpointSerializer"""
    
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
        
        # Criar mock para driver_details
        self.driver.driver_details = type('', (), {'has_valid_license': True})()
        
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
        
        # Criar checkpoint
        self.checkpoint = DeliveryCheckpoint.objects.create(
            delivery=self.delivery,
            location={'latitude': 10.0, 'longitude': 20.0},
            status='pending',
            notes="Checkpoint inicial",
            companie=self.companie,
            created_by=self.manager,
            updated_by=self.manager
        )
    
    def test_checkpoint_serializer_contains_expected_fields(self):
        """Verifica se o serializador contém os campos esperados"""
        serializer = DeliveryCheckpointSerializer(instance=self.checkpoint)
        data = serializer.data
        
        expected_fields = [
            'id', 'location', 'timestamp', 'status', 
            'status_display', 'notes', 'photo'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_checkpoint_serializer_data(self):
        """Testa se os dados serializados são corretos"""
        serializer = DeliveryCheckpointSerializer(instance=self.checkpoint)
        data = serializer.data
        
        self.assertEqual(str(self.checkpoint.id), data['id'])
        self.assertEqual(self.checkpoint.location, data['location'])
        self.assertEqual(self.checkpoint.status, data['status'])
        self.assertEqual(self.checkpoint.notes, data['notes'])
        self.assertIn('status_display', data)
