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
from apps.accounts.models import User
from apps.companies.employeers.models import Employeer
from apps.companies.models import Companie
from apps.inventory.product.models import Product
from apps.inventory.supplier.models import Supplier
from .models import PurchaseOrder, PurchaseOrderItem
from .services.handlers import PurchaseOrderService, PurchaseOrderItemService
from .serializers import PurchaseOrderSerializer, PurchaseOrderItemSerializer
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderModelTests(TestCase):
    """Tests for the PurchaseOrder model"""
    
    def setUp(self):
        """Initial setup for tests"""
        # Set up groups and permissions
        call_command('setup_permission_groups')
        
        # Create users with different types
        self.admin_user = User.objects.create_user(
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = User.objects.create_user(
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stocker'
        )
        
        self.employee = User.objects.create_user(
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Create company
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Get automatically created employees
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associate employees with company
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Reload users to update cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Add users to appropriate groups
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stocker')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Create product
        self.product = Product.objects.create(
            name='Test Product'
        )
        
        # Create order
        self.order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associate order with company
        )

    def test_order_number_generation(self):
        """Test automatic order number generation"""
        self.assertIsNotNone(self.order.order_number)
        self.assertEqual(len(self.order.order_number), 5)
        
        # Create another order and check increment
        order2 = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associate order with company
        )
        self.assertEqual(int(order2.order_number), int(self.order.order_number) + 1)
    
    def test_calculate_total(self):
        """Test order total calculation"""
        # Create items
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
    """Tests for the PurchaseOrder services"""
    
    def setUp(self):
        """Initial setup for tests"""
        # Set up groups and permissions
        call_command('setup_permission_groups')
        
        # Create users with different types
        self.admin_user = User.objects.create_user(
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = User.objects.create_user(
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stocker'
        )
        
        self.employee = User.objects.create_user(
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Create company
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Get automatically created employees
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associate employees with company
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Reload users to update cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Add users to appropriate groups
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stocker')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Create order
        self.order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='pending',
            companie=self.company  # Associate order with company
        )

    def test_user_permissions(self):
        """Test user permissions"""
        # Admin should have all permissions
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
        
        # Stock_Controller should NOT have ANY purchase_order permissions
        all_perms = [
            'can_approve_order', 'can_reject_order', 'can_cancel_order',
            'can_add_item', 'can_update_item', 'can_remove_item',
            'add_purchaseorder', 'change_purchaseorder', 'delete_purchaseorder', 'view_purchaseorder'
        ]
        
        for perm in all_perms:
            self.assertFalse(
                self.stock_controller.has_perm(f'purchase_order.{perm}'),
                f"Stock Controller should not have any purchase_order permissions, including {perm}"
            )
        
        # Employee should have view permission only - no special permissions
        for perm in expected_admin_perms:
            self.assertFalse(
                self.employee.has_perm(f'purchase_order.{perm}'),
                f"Employee should not have {perm} permission"
            )

    def test_approve_order(self):
        """Test order approval"""
        # Adiciona um item ao pedido para satisfazer a validação
        product = Product.objects.create(
            name='Test Product',
            companie=self.company,
            created_by=self.admin_employee,
            updated_by=self.admin_employee
        )
        
        # Cria um item para o pedido
        PurchaseOrderItem.objects.create(
            purchase_order=self.order,
            product=product,
            quantity=10,
            unit_price=Decimal('15.00'),
            companie=self.company,
            created_by=self.admin_employee,
            updated_by=self.admin_employee
        )
        
        # Admin should be able to approve order
        updated_order = PurchaseOrderService.approve_order(
            self.order,
            self.admin_user
        )
        self.assertEqual(updated_order.status, 'approved')
        self.assertEqual(updated_order.updated_by.user, self.admin_user)
        
        # Stock_Controller should not be able to approve order
        with self.assertRaises(Exception):
            PurchaseOrderService.approve_order(
                self.order,
                self.stock_controller
            )
        
        # Employee should not be able to approve order
        with self.assertRaises(Exception):
            PurchaseOrderService.approve_order(
                self.order,
                self.employee
            )

    def test_reject_order(self):
        """Test order rejection"""
        # Reject order
        reason = "Prices are too high"
        updated_order = PurchaseOrderService.reject_order(
            self.order.id,
            self.admin_user,
            reason
        )
        
        self.assertEqual(updated_order.status, 'rejected')
        self.assertEqual(updated_order.updated_by.user, self.admin_user)
        self.assertEqual(updated_order.notes, reason)

class PurchaseOrderAPITests(APITestCase):
    """Tests for the PurchaseOrder API"""
    
    def setUp(self):
        """Initial setup for tests"""
        # Set up logger
        logging.basicConfig(level=logging.INFO)
        
        # Set up groups and permissions
        call_command('setup_permission_groups')
        
        self.client = APIClient()
        
        # Create users with different types
        self.admin_user = User.objects.create_user(
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = User.objects.create_user(
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stocker'
        )
        
        self.employee = User.objects.create_user(
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Create company
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Get automatically created employees
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associate employees with company
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Reload users to update cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Add users to appropriate groups
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stocker')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Create product
        self.product = Product.objects.create(
            name='Test Product'
        )
        
        # Authenticate client
        self.client.force_authenticate(user=self.admin_user)
    
    def test_create_order(self):
        """Test creating an order via API"""
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
        """Test listing orders via API"""
        # Clear any existing orders to ensure test isolation
        PurchaseOrder.objects.all().delete()
        
        # Create some orders
        order1 = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associate order with company
        )
        order2 = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='pending',
            companie=self.company  # Associate order with company
        )
        
        url = reverse('purchase_order:list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response is paginated
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        
        # Check that we have exactly 2 orders in the results
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_approve_order_api(self):
        """Test approving an order via API"""
        # Create order
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='pending',
            companie=self.company  # Associate order with company
        )
        
        # Add item to order
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
        logger.info(f"User company: {self.admin_user.employeer.companie}")
        logger.info(f"User employeer: {self.admin_user.employeer}")
        
        response = self.client.post(url)
        
        if response.status_code != status.HTTP_200_OK:
            logger.error(f"Response data: {response.data}")
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'approved')

class NotificationTests(TestCase):
    """Tests for the notification system"""
    
    def setUp(self):
        """Initial setup for tests"""
        # Set up groups and permissions
        call_command('setup_permission_groups')
        
        # Create users with different types
        self.admin_user = User.objects.create_user(
            password='admin123',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin'
        )
        
        self.stock_controller = User.objects.create_user(
            password='stock123',
            email='stock@test.com',
            first_name='Stock',
            last_name='Controller',
            user_type='Stocker'
        )
        
        self.employee = User.objects.create_user(
            password='emp123',
            email='emp@test.com',
            first_name='Regular',
            last_name='Employee',
            user_type='Employee'
        )
        
        # Create company
        self.company = Companie.objects.create(
            name='Test Company',
            type='matriz'
        )
        
        # Get automatically created employees
        self.admin_employee = Employeer.objects.get(user=self.admin_user)
        self.stock_employee = Employeer.objects.get(user=self.stock_controller)
        self.regular_employee = Employeer.objects.get(user=self.employee)
        
        # Associate employees with company
        self.admin_employee.companie = self.company
        self.admin_employee.save()
        self.stock_employee.companie = self.company
        self.stock_employee.save()
        self.regular_employee.companie = self.company
        self.regular_employee.save()

        # Reload users to update cache
        self.admin_user.refresh_from_db()
        self.stock_controller.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Add users to appropriate groups
        admin_group = Group.objects.get(name='Admin')
        stock_group = Group.objects.get(name='Stocker')
        employee_group = Group.objects.get(name='Employee')
        
        self.admin_user.groups.add(admin_group)
        self.stock_controller.groups.add(stock_group)
        self.employee.groups.add(employee_group)
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier'
        )
        
        # Create product
        self.product = Product.objects.create(
            name='Test Product'
        )
    
    def test_order_creation_notification(self):
        """Test order creation notification"""
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associate order with company
        )
        
        # TODO: Implement notification checks
        # For now, just check if the order was created
        self.assertTrue(PurchaseOrder.objects.filter(id=order.id).exists())
    
    def test_item_addition_notification(self):
        """Test item addition notification"""
        # Create order
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            expected_delivery=timezone.now().date(),
            status='draft',
            companie=self.company  # Associate order with company
        )
        
        # Add item
        item = PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('10.00')
        )
        
        # TODO: Implement notification checks
        # For now, just check if the item was created
        self.assertTrue(PurchaseOrderItem.objects.filter(id=item.id).exists())
