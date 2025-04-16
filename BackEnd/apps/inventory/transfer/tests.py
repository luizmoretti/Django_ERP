from django.test import TestCase
from django.db import transaction
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from ..warehouse.models import Warehouse, WarehouseProduct
from ..product.models import Product
from .models import Transfer, TransferItems
from apps.companies.models import Companie
from apps.accounts.models import User
from apps.companies.employeers.models import Employeer

class TransferCapacityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create Employee group
        cls.employee_group = Group.objects.create(name='Employee')
        
        # Create test company
        cls.company = Companie.objects.create(name="Test Company")
        
        # Create test user with unique name for transfer tests
        cls.user = User.objects.create(
            email="transfer_test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            user_type='Employee'  # Set user type to match group
        )
        
        # Create employee record
        cls.employee = Employeer.objects.create(
            name="Transfer Test User",
            companie=cls.company,
            email="transfer_test@example.com"
        )
        
        # Create test product
        cls.product = Product.objects.create(
            name="Test Product",
            companie=cls.company,
            created_by=cls.employee,
            updated_by=cls.employee
        )
        
        # Create test warehouses
        cls.origin_warehouse = Warehouse.objects.create(
            name="Origin Warehouse",
            limit=100,
            companie=cls.company,
            created_by=cls.employee,
            updated_by=cls.employee
        )
        
        cls.destiny_warehouse = Warehouse.objects.create(
            name="Destiny Warehouse",
            limit=100,
            companie=cls.company,
            created_by=cls.employee,
            updated_by=cls.employee
        )
        
    def setUp(self):
        # Create base transfer
        self.transfer = Transfer.objects.create(
            origin=self.origin_warehouse,
            destiny=self.destiny_warehouse,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Setup initial warehouse stock
        self.origin_warehouse_product = WarehouseProduct.objects.create(
            warehouse=self.origin_warehouse,
            product=self.product,
            current_quantity=100,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        self.origin_warehouse.update_total_quantity()
        
        self.destiny_warehouse_product = WarehouseProduct.objects.create(
            warehouse=self.destiny_warehouse,
            product=self.product,
            current_quantity=0,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        self.destiny_warehouse.update_total_quantity()

    def test_transfer_within_limits(self):
        """Test transfer within warehouse limits"""
        # Create transfer item within limits
        transfer_item = TransferItems.objects.create(
            transfer=self.transfer,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify quantities were updated correctly
        self.origin_warehouse_product.refresh_from_db()
        self.destiny_warehouse_product.refresh_from_db()
        self.origin_warehouse.refresh_from_db()
        self.destiny_warehouse.refresh_from_db()
        
        self.assertEqual(self.origin_warehouse_product.current_quantity, 50)
        self.assertEqual(self.destiny_warehouse_product.current_quantity, 50)
        self.assertEqual(self.origin_warehouse.quantity, 50)
        self.assertEqual(self.destiny_warehouse.quantity, 50)

    def test_transfer_exceeding_origin_quantity(self):
        """Test transfer exceeding origin warehouse quantity"""
        # Try to create transfer item exceeding available quantity
        with self.assertRaises(ValidationError):
            TransferItems.objects.create(
                transfer=self.transfer,
                product=self.product,
                quantity=150,  # Exceeds available quantity of 100
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_transfer_exceeding_destiny_limit(self):
        """Test transfer exceeding destiny warehouse limit"""
        # Set destiny warehouse limit to 30
        self.destiny_warehouse.limit = 30
        self.destiny_warehouse.save()
        
        # Try to transfer amount that would exceed destiny limit
        with self.assertRaises(ValidationError):
            TransferItems.objects.create(
                transfer=self.transfer,
                product=self.product,
                quantity=50,  # Would exceed destiny limit of 30
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_transfer_update_quantity(self):
        """Test quantity validation when updating transfer quantity"""
        # Create initial transfer
        transfer_item = TransferItems.objects.create(
            transfer=self.transfer,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to update quantity beyond available
        with self.assertRaises(ValidationError):
            transfer_item.quantity = 150  # Would exceed available quantity
            transfer_item.save()
        
        # Verify original quantity unchanged
        transfer_item.refresh_from_db()
        self.assertEqual(transfer_item.quantity, 50)
        
        # Verify warehouse quantities unchanged
        self.origin_warehouse_product.refresh_from_db()
        self.destiny_warehouse_product.refresh_from_db()
        self.origin_warehouse.refresh_from_db()
        self.destiny_warehouse.refresh_from_db()
        
        self.assertEqual(self.origin_warehouse_product.current_quantity, 50)
        self.assertEqual(self.destiny_warehouse_product.current_quantity, 50)
        self.assertEqual(self.origin_warehouse.quantity, 50)
        self.assertEqual(self.destiny_warehouse.quantity, 50)

    def test_transfer_to_unlimited_warehouse(self):
        """Test transfer to warehouse with unlimited capacity"""
        # Create warehouse with unlimited capacity (limit=0)
        unlimited_warehouse = Warehouse.objects.create(
            name="Unlimited Warehouse",
            limit=0,  # 0 means unlimited
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Create transfer to unlimited warehouse
        unlimited_transfer = Transfer.objects.create(
            origin=self.origin_warehouse,
            destiny=unlimited_warehouse,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Should allow transfer up to origin quantity
        transfer_item = TransferItems.objects.create(
            transfer=unlimited_transfer,
            product=self.product,
            quantity=100,  # Can transfer all available quantity
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify quantities
        self.origin_warehouse_product.refresh_from_db()
        self.origin_warehouse.refresh_from_db()
        
        unlimited_warehouse_product = WarehouseProduct.objects.get(
            warehouse=unlimited_warehouse,
            product=self.product
        )
        unlimited_warehouse.refresh_from_db()
        
        self.assertEqual(self.origin_warehouse_product.current_quantity, 0)
        self.assertEqual(self.origin_warehouse.quantity, 0)
        self.assertEqual(unlimited_warehouse_product.current_quantity, 100)
        self.assertEqual(unlimited_warehouse.quantity, 100)

    def test_warehouse_total_after_multiple_operations(self):
        """Test warehouse total is correctly updated after multiple operations"""
        # Initial state
        self.assertEqual(self.origin_warehouse.quantity, 100)
        self.assertEqual(self.destiny_warehouse.quantity, 0)
        
        # Create first transfer
        transfer1 = TransferItems.objects.create(
            transfer=self.transfer,
            product=self.product,
            quantity=30,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify totals after first transfer
        self.origin_warehouse.refresh_from_db()
        self.destiny_warehouse.refresh_from_db()
        self.assertEqual(self.origin_warehouse.quantity, 70)
        self.assertEqual(self.destiny_warehouse.quantity, 30)
        
        # Create second transfer
        transfer2 = TransferItems.objects.create(
            transfer=self.transfer,
            product=self.product,
            quantity=20,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify totals after second transfer
        self.origin_warehouse.refresh_from_db()
        self.destiny_warehouse.refresh_from_db()
        self.assertEqual(self.origin_warehouse.quantity, 50)
        self.assertEqual(self.destiny_warehouse.quantity, 50)
        
        # Delete first transfer
        transfer1.delete()
        
        # Verify totals after deletion
        self.origin_warehouse.refresh_from_db()
        self.destiny_warehouse.refresh_from_db()
        self.assertEqual(self.origin_warehouse.quantity, 80)
        self.assertEqual(self.destiny_warehouse.quantity, 20)
        
        # Update second transfer
        transfer2.quantity = 30
        transfer2.save()
        
        # Verify totals after update
        self.origin_warehouse.refresh_from_db()
        self.destiny_warehouse.refresh_from_db()
        self.assertEqual(self.origin_warehouse.quantity, 70)
        self.assertEqual(self.destiny_warehouse.quantity, 30)

    def test_transfer_capacity_warning(self):
        """Test warning when transfer approaches destiny capacity"""
        with self.assertLogs('apps.inventory.warehouse.signals', level='WARNING') as cm:
            # Create transfer that will result in 91% capacity
            TransferItems.objects.create(
                transfer=self.transfer,
                product=self.product,
                quantity=91,  # 91% of destiny limit
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )
            
            # Check that warning was logged
            self.assertTrue(any('91.0% capacity' in msg for msg in cm.output))

    def test_multiple_transfers_capacity(self):
        """Test capacity validation with multiple transfers"""
        # First transfer
        TransferItems.objects.create(
            transfer=self.transfer,
            product=self.product,
            quantity=60,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try second transfer that would exceed destiny capacity
        with self.assertRaises(ValidationError):
            TransferItems.objects.create(
                transfer=self.transfer,
                product=self.product,
                quantity=50,  # Would exceed destiny limit
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_transfer_update_quantity(self):
        """Test capacity validation when updating transfer quantity"""
        # Create initial transfer
        transfer_item = TransferItems.objects.create(
            transfer=self.transfer,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to update quantity beyond destiny capacity
        with self.assertRaises(ValidationError):
            transfer_item.quantity = 150
            transfer_item.save()
        
        # Verify original quantity unchanged
        transfer_item.refresh_from_db()
        self.assertEqual(transfer_item.quantity, 50)

    def test_transfer_deletion_updates_quantities(self):
        """Test warehouse quantities are updated when transfer is deleted"""
        # Create transfer
        transfer_item = TransferItems.objects.create(
            transfer=self.transfer,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify initial quantities
        self.origin_warehouse_product.refresh_from_db()
        destiny_product = WarehouseProduct.objects.get(
            warehouse=self.destiny_warehouse,
            product=self.product
        )
        
        self.assertEqual(self.origin_warehouse_product.current_quantity, 50)
        self.assertEqual(destiny_product.current_quantity, 50)
        
        # Delete transfer
        transfer_item.delete()
        
        # Verify quantities restored
        self.origin_warehouse_product.refresh_from_db()
        destiny_product.refresh_from_db()
        
        self.assertEqual(self.origin_warehouse_product.current_quantity, 100)
        self.assertEqual(destiny_product.current_quantity, 0)
