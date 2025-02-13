from django.test import TestCase
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from ..product.models import Product
from ..warehouse.models import Warehouse, WarehouseProduct
from .models import Inflow, InflowItems
from apps.companies.models import Companie
from apps.accounts.models import NormalUser
from apps.companies.employeers.models import Employeer
from apps.inventory.supplier.models import Supplier

class InflowCapacityTests(TestCase):
    def setUp(self):
        # Create Employee group
        self.employee_group = Group.objects.create(name='Employee')
        
        # Create test company and user
        self.company = Companie.objects.create(name="Test Company")
        
        # Create test user with unique username/email
        test_number = id(self)  # Use test instance id to generate unique values
        self.user = NormalUser.objects.create(
            username=f"testuser{test_number}",
            email=f"test{test_number}@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            user_type='Employee'  # Set user type to match group
        )
        
        # Get or create employee record
        self.employee, _ = Employeer.objects.get_or_create(
            user=self.user,
            defaults={
                'name': "Test User",
                'companie': self.company,
                'email': f"test{test_number}@example.com"
            }
        )
        
        # Create test supplier
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Create test warehouse
        self.warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            limit=100,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Create test product
        self.product = Product.objects.create(
            name="Test Product",
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Create base inflow
        self.inflow = Inflow.objects.create(
            origin=self.supplier,
            destiny=self.warehouse,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )

    def test_inflow_within_capacity(self):
        """Test inflow within warehouse capacity limits"""
        # Create inflow item within capacity
        inflow_item = InflowItems.objects.create(
            inflow=self.inflow,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify quantities were updated
        warehouse_product = WarehouseProduct.objects.get(
            warehouse=self.warehouse,
            product=self.product
        )
        self.assertEqual(warehouse_product.current_quantity, 50)
        self.assertEqual(self.warehouse.quantity, 50)

    def test_inflow_exceeding_capacity(self):
        """Test inflow exceeding warehouse capacity"""
        # Try to create inflow item exceeding capacity
        with self.assertRaises(ValidationError):
            InflowItems.objects.create(
                inflow=self.inflow,
                product=self.product,
                quantity=150,  # Exceeds limit of 100
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_inflow_unlimited_capacity(self):
        """Test inflow to warehouse with unlimited capacity"""
        # Create unlimited capacity warehouse
        unlimited_warehouse = Warehouse.objects.create(
            name="Unlimited Warehouse",
            limit=0,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Create inflow to unlimited warehouse
        unlimited_inflow = Inflow.objects.create(
            origin=self.supplier,
            destiny=unlimited_warehouse,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Should allow large quantity
        inflow_item = InflowItems.objects.create(
            inflow=unlimited_inflow,
            product=self.product,
            quantity=1000,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        warehouse_product = WarehouseProduct.objects.get(
            warehouse=unlimited_warehouse,
            product=self.product
        )
        self.assertEqual(warehouse_product.current_quantity, 1000)

    def test_inflow_capacity_warning(self):
        """Test warning when inflow approaches capacity"""
        with self.assertLogs('apps.inventory.warehouse.signals', level='WARNING') as cm:
            # Create inflow item that will result in 91% capacity
            InflowItems.objects.create(
                inflow=self.inflow,
                product=self.product,
                quantity=91,
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )
            
            # Check that warning was logged
            self.assertTrue(any('91.0% capacity' in msg for msg in cm.output))

    def test_multiple_inflows_capacity(self):
        """Test capacity validation with multiple inflows"""
        # First inflow using 60% capacity
        InflowItems.objects.create(
            inflow=self.inflow,
            product=self.product,
            quantity=60,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try second inflow that would exceed capacity
        with self.assertRaises(ValidationError):
            InflowItems.objects.create(
                inflow=self.inflow,
                product=self.product,
                quantity=50,  # Would total 110
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_inflow_update_capacity(self):
        """Test capacity validation when updating inflow quantity"""
        # Create initial inflow
        inflow_item = InflowItems.objects.create(
            inflow=self.inflow,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to update quantity beyond capacity
        with self.assertRaises(ValidationError):
            inflow_item.quantity = 150
            inflow_item.save()
        
        # Verify original quantity unchanged
        inflow_item.refresh_from_db()
        self.assertEqual(inflow_item.quantity, 50)
        
        # Verify warehouse quantities unchanged
        warehouse_product = WarehouseProduct.objects.get(
            warehouse=self.warehouse,
            product=self.product
        )
        self.assertEqual(warehouse_product.current_quantity, 50)
        self.assertEqual(self.warehouse.quantity, 50)

    def test_inflow_deletion_updates_capacity(self):
        """Test warehouse capacity is updated when inflow is deleted"""
        # Create inflow
        inflow_item = InflowItems.objects.create(
            inflow=self.inflow,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify initial quantity
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 50)
        
        # Delete inflow
        inflow_item.delete()
        
        # Verify quantity updated
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 0)

    def test_warehouse_total_after_multiple_operations(self):
        """Test warehouse total is correctly updated after multiple operations"""
        # Initial state
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 0)
        
        # Create first inflow
        inflow1 = InflowItems.objects.create(
            inflow=self.inflow,
            product=self.product,
            quantity=30,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify total after first inflow
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 30)
        
        # Create second inflow
        inflow2 = InflowItems.objects.create(
            inflow=self.inflow,
            product=self.product,
            quantity=20,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify total after second inflow
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 50)
        
        # Delete first inflow
        inflow1.delete()
        
        # Verify total after deletion
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 20)
        
        # Update second inflow
        inflow2.quantity = 30
        inflow2.save()
        
        # Verify total after update
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 30)
