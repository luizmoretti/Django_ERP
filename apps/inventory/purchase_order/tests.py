from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from apps.accounts.models import NormalUser
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from apps.inventory.product.models import Product
from apps.inventory.supplier.models import Supplier
from .models import PurchaseOrder, PurchaseOrderItem
from .services import PurchaseOrderService, PurchaseOrderItemService
from .serializers import PurchaseOrderSerializer, PurchaseOrderItemSerializer
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderModelTests(TestCase):
    """Testes para o modelo PurchaseOrder"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Configurar grupos e permissões
        call_command('setup_permission_groups')
        
        # Criar usuários com diferentes tipos
        self.admin_user = NormalUser.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = NormalUser.objects.create_user(
            username='stock',
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stock_Controller'
        )
        
        self.employee = NormalUser.objects.create_user(
            username='employee',
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Criar empresa
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Obter os funcionários criados automaticamente
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associar funcionários à empresa
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Recarregar usuários para atualizar o cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Adicionar usuários aos grupos apropriados
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stock_Controller')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Criar fornecedor
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Criar produto
        self.product = Product.objects.create(
            name='Test Product'
        )
        
        # Criar pedido
        self.order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associando o pedido à empresa
        )

    def test_order_number_generation(self):
        """Testa a geração automática do número do pedido"""
        self.assertIsNotNone(self.order.order_number)
        self.assertEqual(len(self.order.order_number), 5)
        
        # Criar outro pedido e verificar incremento
        order2 = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associando o pedido à empresa
        )
        self.assertEqual(int(order2.order_number), int(self.order.order_number) + 1)
    
    def test_calculate_total(self):
        """Testa o cálculo do total do pedido"""
        # Criar itens
        item1 = PurchaseOrderItem.objects.create(
            purchase_order=self.order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('10.00')
        )
        item2 = PurchaseOrderItem.objects.create(
            purchase_order=self.order,
            product=self.product,
            quantity=3,
            unit_price=Decimal('15.00')
        )
        
        expected_total = (2 * Decimal('10.00')) + (3 * Decimal('15.00'))
        self.assertEqual(self.order.total, expected_total)

class PurchaseOrderServiceTests(TestCase):
    """Testes para os serviços de PurchaseOrder"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Configurar grupos e permissões
        call_command('setup_permission_groups')
        
        # Criar usuários com diferentes tipos
        self.admin_user = NormalUser.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = NormalUser.objects.create_user(
            username='stock',
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stock_Controller'
        )
        
        self.employee = NormalUser.objects.create_user(
            username='employee',
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Criar empresa
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Obter os funcionários criados automaticamente
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associar funcionários à empresa
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Recarregar usuários para atualizar o cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Adicionar usuários aos grupos apropriados
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stock_Controller')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Criar fornecedor
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Criar pedido
        self.order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='pending',
            companie=self.company  # Associando o pedido à empresa
        )

    def test_user_permissions(self):
        """Testa as permissões de diferentes tipos de usuários"""
        # Admin deve ter todas as permissões
        expected_admin_perms = [
            'can_approve_order',
            'can_reject_order',
            'can_cancel_order',
            'can_add_item',
            'can_update_item',
            'can_remove_item'
        ]
        
        for perm in expected_admin_perms:
            self.assertTrue(
                self.admin_user.has_perm(f'purchase_order.{perm}'),
                f"Admin should have {perm} permission"
            )
        
        # Stock_Controller deve ter permissões básicas
        basic_perms = ['can_add_item', 'can_update_item', 'can_remove_item']
        for perm in basic_perms:
            self.assertTrue(
                self.stock_controller.has_perm(f'purchase_order.{perm}'),
                f"Stock Controller should have {perm} permission"
            )
        
        # Stock_Controller não deve ter permissões de aprovação
        approval_perms = ['can_approve_order', 'can_reject_order', 'can_cancel_order']
        for perm in approval_perms:
            self.assertFalse(
                self.stock_controller.has_perm(f'purchase_order.{perm}'),
                f"Stock Controller should not have {perm} permission"
            )
        
        # Employee deve ter apenas permissão de visualização
        for perm in expected_admin_perms:
            self.assertFalse(
                self.employee.has_perm(f'purchase_order.{perm}'),
                f"Employee should not have {perm} permission"
            )

    def test_approve_order(self):
        """Testa a aprovação de pedido"""
        # Admin deve poder aprovar pedido
        updated_order = PurchaseOrderService.approve_order(
            self.order,
            self.admin_user
        )
        self.assertEqual(updated_order.status, 'approved')
        self.assertEqual(updated_order.updated_by.user, self.admin_user)
        
        # Stock_Controller não deve poder aprovar pedido
        with self.assertRaises(Exception):
            PurchaseOrderService.approve_order(
                self.order,
                self.stock_controller
            )
        
        # Employee não deve poder aprovar pedido
        with self.assertRaises(Exception):
            PurchaseOrderService.approve_order(
                self.order,
                self.employee
            )

    def test_reject_order(self):
        """Testa a rejeição de pedido"""
        # Rejeitar pedido
        reason = "Preços muito altos"
        updated_order = PurchaseOrderService.reject_order(
            self.order.id,
            self.admin_user,
            reason
        )
        
        self.assertEqual(updated_order.status, 'rejected')
        self.assertEqual(updated_order.updated_by.user, self.admin_user)
        self.assertEqual(updated_order.notes, reason)

class PurchaseOrderAPITests(APITestCase):
    """Testes para as APIs de PurchaseOrder"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Configurar logger
        logging.basicConfig(level=logging.INFO)
        
        # Configurar grupos e permissões
        call_command('setup_permission_groups')
        
        self.client = APIClient()
        
        # Criar usuários com diferentes tipos
        self.admin_user = NormalUser.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = NormalUser.objects.create_user(
            username='stock',
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stock_Controller'
        )
        
        self.employee = NormalUser.objects.create_user(
            username='employee',
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Criar empresa
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Obter os funcionários criados automaticamente
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associar funcionários à empresa
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Recarregar usuários para atualizar o cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Adicionar usuários aos grupos apropriados
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stock_Controller')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Criar fornecedor
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Criar produto
        self.product = Product.objects.create(
            name='Test Product'
        )
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.admin_user)
    
    def test_create_order(self):
        """Testa a criação de pedido via API"""
        url = reverse('purchase_order:create')
        data = {
            'supplier': str(self.supplier.id),
            'expected_delivery': timezone.now().date().isoformat(),
            'status': 'draft',
            'companie': str(self.company.id),
            'items_data': [
                {
                    'product': str(self.product.id),
                    'quantity': 2,
                    'unit_price': '10.00'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        self.assertEqual(PurchaseOrderItem.objects.count(), 1)
    
    def test_list_orders(self):
        """Testa a listagem de pedidos via API"""
        # Criar alguns pedidos
        PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associando o pedido à empresa
        )
        PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='pending',
            companie=self.company  # Associando o pedido à empresa
        )
        
        url = reverse('purchase_order:list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_approve_order_api(self):
        """Testa a aprovação de pedido via API"""
        # Criar pedido
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='pending',
            companie=self.company  # Associando o pedido à empresa
        )
        
        # Adicionar item ao pedido
        PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('10.00')
        )
        
        url = reverse('purchase_order:approve', kwargs={'pk': order.id})
        logger.info(f"User permissions: {self.admin_user.get_all_permissions()}")
        logger.info(f"User groups: {self.admin_user.groups.all()}")
        logger.info(f"User type: {self.admin_user.user_type}")
        logger.info(f"Order status: {order.status}")
        logger.info(f"Order company: {order.companie}")
        logger.info(f"User company: {self.admin_user.employeer_user.companie}")
        logger.info(f"User employeer: {self.admin_user.employeer_user}")
        
        response = self.client.post(url)
        
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Response data: {response.data}")
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'approved')

class NotificationTests(TestCase):
    """Testes para o sistema de notificações"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Configurar grupos e permissões
        call_command('setup_permission_groups')
        
        # Criar usuários com diferentes tipos
        self.admin_user = NormalUser.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = NormalUser.objects.create_user(
            username='stock',
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stock_Controller'
        )
        
        self.employee = NormalUser.objects.create_user(
            username='employee',
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Criar empresa
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Obter os funcionários criados automaticamente
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associar funcionários à empresa
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Recarregar usuários para atualizar o cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Adicionar usuários aos grupos apropriados
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stock_Controller')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Criar fornecedor
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Criar produto
        self.product = Product.objects.create(
            name='Test Product'
        )
    
    def test_order_creation_notification(self):
        """Testa notificação de criação de pedido"""
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associando o pedido à empresa
        )
        
        # TODO: Implementar verificação de notificações
        # Por enquanto, apenas verifica se o pedido foi criado
        self.assertTrue(PurchaseOrder.objects.filter(id=order.id).exists())
    
    def test_item_addition_notification(self):
        """Testa notificação de adição de item"""
        # Criar pedido
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associando o pedido à empresa
        )
        
        # Adicionar item
        item = PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('10.00')
        )
        
        # TODO: Implementar verificação de notificações
        # Por enquanto, apenas verifica se o item foi criado
        self.assertTrue(PurchaseOrderItem.objects.filter(id=item.id).exists())
