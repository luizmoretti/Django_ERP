from django.test import TestCase
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from ..product.models import Product
from .models import Warehouse, WarehouseProduct
from apps.companies.models import Companie
from apps.accounts.models import User
from apps.companies.employeers.models import Employeer

class WarehouseCapacityTests(TestCase):
    def setUp(self):
        # Create Employee group
        self.employee_group = Group.objects.create(name='Employee')
        
        # Create test company and user
        self.company = Companie.objects.create(name="Test Company")
        
        # Create test user with unique username/email
        test_number = id(self)  # Use test instance id to generate unique values
        self.user = User.objects.create(
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
    
    def test_multiple_products_capacity(self):
        """Test capacity validation with multiple products"""
        # Add first product at 60% capacity
        warehouse_product1 = WarehouseProduct.objects.create(
            warehouse=self.warehouse,
            product=self.product,
            current_quantity=60,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Create second product
        product2 = Product.objects.create(
            name="Test Product 2",
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to add second product at 50% capacity (would total 110%)
        with self.assertRaises(ValidationError):
            warehouse_product2 = WarehouseProduct.objects.create(
                warehouse=self.warehouse,
                product=product2,
                current_quantity=50,
                companie=self.company,
                created_by=self.employee,
                updated_by=self.employee
            )
    
    def test_negative_quantity_prevention(self):
        """Test that negative quantities are prevented"""
        # First create a product with quantity 50
        warehouse_product = WarehouseProduct.objects.create(
            warehouse=self.warehouse,
            product=self.product,
            current_quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to update to negative quantity
        with self.assertRaises(ValidationError):
            warehouse_product.current_quantity = -10
            warehouse_product.save()
    
    def test_atomic_transaction_rollback(self):
        """Test that failed capacity validation rolls back all changes"""
        # Create first product with quantity 50
        warehouse_product1 = WarehouseProduct.objects.create(
            warehouse=self.warehouse,
            product=self.product,
            current_quantity=50,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Create second product
        product2 = Product.objects.create(
            name="Test Product 2",
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to add second product that would exceed capacity
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                warehouse_product2 = WarehouseProduct.objects.create(
                    warehouse=self.warehouse,
                    product=product2,
                    current_quantity=60,  # Would total 110%
                    companie=self.company,
                    created_by=self.employee,
                    updated_by=self.employee
                )
        
        # Verify the first product's quantity is unchanged
        warehouse_product1.refresh_from_db()
        self.assertEqual(warehouse_product1.current_quantity, 50)
        
        # Verify warehouse total quantity is unchanged
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 50)
        
        # Verify second product was not created in warehouse
        self.assertFalse(
            WarehouseProduct.objects.filter(
                warehouse=self.warehouse,
                product=product2
            ).exists()
        )
    
    def test_warehouse_limit_change(self):
        """Test changing warehouse capacity limit"""
        # Add product at 80% of current capacity
        warehouse_product = WarehouseProduct.objects.create(
            warehouse=self.warehouse,
            product=self.product,
            current_quantity=80,
            companie=self.company,
            created_by=self.employee,
            updated_by=self.employee
        )
        
        # Try to reduce limit below current quantity
        with self.assertRaises(ValidationError):
            self.warehouse.limit = 70
            self.warehouse.save()
