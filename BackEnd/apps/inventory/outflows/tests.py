from django.test import TestCase
from django.db import transaction
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from ..warehouse.models import Warehouse, WarehouseProduct
from ..product.models import Product
from .models import Outflow, OutflowItems
from apps.companies.models import Companie
from apps.accounts.models import User
from apps.companies.employeers.models import Employeer
from apps.companies.customers.models import Customer

class OutflowCapacityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create Employee group
        cls.employee_group = Group.objects.create(name='Employee')
        
        # Create test company
        cls.company = Companie.objects.create(name="Test Company")
        
        # Create test user with unique name for outflow tests
        cls.user = User.objects.create(
            email="outflow_test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            user_type='Employee'  # Set user type to match group
        )
        
        # Create employee record
        cls.employee = Employeer.objects.create(
            name="Outflow Test User",
            companie=cls.company,
            email="outflow_test@example.com"
        )
        
        # Create test product
        cls.product = Product.objects.create(
            name="Test Product",
            companie=cls.company,
            created_by=cls.employee,
            updated_by=cls.employee
        )
        
        # Create test warehouse
        cls.warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            limit=100,
            companie=cls.company,
            created_by=cls.employee,
            updated_by=cls.employee
        )
        
        # Create test customer
        cls.customer = Customer.objects.create(
            first_name="Test",
            last_name="Customer",
            companie=cls.company,
            created_by=cls.employee,
            updated_by=cls.employee
        )
        
    def setUp(self):
        # Create base outflow
        self.outflow = Outflow.objects.create(
            origin=self.warehouse,
            destiny=self.customer,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Setup initial warehouse stock
        self.warehouse_product = WarehouseProduct.objects.create(
            warehouse=self.warehouse,
            product=self.product,
            current_quantity=100,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        # Update product quantity to match warehouse stock
        self.product.quantity = 100
        self.product.save()
        
        self.warehouse.update_total_quantity()

    def test_outflow_within_quantity(self):
        """Test outflow within available quantity"""
        # Create outflow item within available quantity
        outflow_item = OutflowItems.objects.create(
            outflow=self.outflow,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify quantities were updated
        self.warehouse_product.refresh_from_db()
        self.warehouse.refresh_from_db()
        
        self.assertEqual(self.warehouse_product.current_quantity, 50)
        self.assertEqual(self.warehouse.quantity, 50)

    def test_outflow_exceeding_quantity(self):
        """Test outflow exceeding available quantity"""
        # Try to create outflow item exceeding available quantity
        with self.assertRaises(ValidationError):
            OutflowItems.objects.create(
                outflow=self.outflow,
                product=self.product,
                quantity=150,  # Exceeds available quantity of 100
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_outflow_update_quantity(self):
        """Test quantity validation when updating outflow quantity"""
        # Create initial outflow
        outflow_item = OutflowItems.objects.create(
            outflow=self.outflow,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to update quantity beyond available
        with self.assertRaises(ValidationError):
            outflow_item.quantity = 150  # Would exceed available quantity
            outflow_item.save()
        
        # Verify original quantity unchanged
        outflow_item.refresh_from_db()
        self.assertEqual(outflow_item.quantity, 50)
        
        # Verify warehouse quantities unchanged
        self.warehouse_product.refresh_from_db()
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse_product.current_quantity, 50)
        self.assertEqual(self.warehouse.quantity, 50)

    def test_multiple_outflows_quantity(self):
        """Test quantity validation with multiple outflows"""
        # First outflow using 60 units
        OutflowItems.objects.create(
            outflow=self.outflow,
            product=self.product,
            quantity=60,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try second outflow that would exceed available quantity
        with self.assertRaises(ValidationError):
            OutflowItems.objects.create(
                outflow=self.outflow,
                product=self.product,
                quantity=50,  # Would exceed available quantity
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_outflow_deletion_updates_quantity(self):
        """Test warehouse quantity is updated when outflow is deleted"""
        # Create outflow
        outflow_item = OutflowItems.objects.create(
            outflow=self.outflow,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify initial quantities
        self.warehouse_product.refresh_from_db()
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse_product.current_quantity, 50)
        self.assertEqual(self.warehouse.quantity, 50)
        
        # Delete outflow
        outflow_item.delete()
        
        # Verify quantities restored
        self.warehouse_product.refresh_from_db()
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse_product.current_quantity, 100)
        self.assertEqual(self.warehouse.quantity, 100)

    def test_negative_quantity_prevention(self):
        """Test that negative quantities are prevented"""
        with self.assertRaises(ValidationError):
            OutflowItems.objects.create(
                outflow=self.outflow,
                product=self.product,
                quantity=-10,
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )

    def test_warehouse_total_after_multiple_operations(self):
        """Test warehouse total is correctly updated after multiple operations"""
        # Initial state
        self.assertEqual(self.warehouse.quantity, 100)
        
        # Create first outflow
        outflow1 = OutflowItems.objects.create(
            outflow=self.outflow,
            product=self.product,
            quantity=30,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify total after first outflow
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 70)
        
        # Create second outflow
        outflow2 = OutflowItems.objects.create(
            outflow=self.outflow,
            product=self.product,
            quantity=20,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Verify total after second outflow
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 50)
        
        # Delete first outflow
        outflow1.delete()
        
        # Verify total after deletion
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 80)
        
        # Update second outflow
        outflow2.quantity = 30
        outflow2.save()
        
        # Verify total after update
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 70)

    def test_atomic_transaction_rollback(self):
        """Test that failed quantity validation rolls back all changes"""
        # Create initial outflow
        outflow_item = OutflowItems.objects.create(
            outflow=self.outflow,
            product=self.product,
            quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to update multiple items in a way that would exceed quantity
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                # Update existing item
                outflow_item.quantity = 70
                outflow_item.save()
                
                # Create new item that would exceed quantity
                OutflowItems.objects.create(
                    outflow=self.outflow,
                    product=self.product,
                    quantity=40,  # Would exceed available quantity
                    companie=self.company,
                    created_by=self.employee,
                    updated_by=self.employee
                )
        
        # Verify original quantity was not changed
        outflow_item.refresh_from_db()
        self.assertEqual(outflow_item.quantity, 50)
