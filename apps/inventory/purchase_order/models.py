# apps/inventory/purchase_order/models.py

from decimal import Decimal
from django.db import models, transaction, IntegrityError
from apps.inventory.product.models import Product
from apps.inventory.supplier.models import Supplier
from basemodels.models import BaseModel
from core.constants.choices import PURCHASE_ORDER_STATUS_CHOICES

class PurchaseOrder(BaseModel):
    """Purchase Order model for tracking product purchases from suppliers
    
    Fields:
        supplier: ForeignKey to Supplier - The supplier providing the products
        order_date: DateField - Date when the order was placed
        expected_delivery: DateField - Expected delivery date
        status: CharField - Current status of the purchase order
        notes: TextField - Additional notes about the order
        
    Inheritance:
        BaseModel{
            id: UUIDField
            companie: ForeignKey to Companie
            created_at: DateTimeField
            updated_at: DateTimeField
            created_by: ForeignKey to Employeer
            updated_by: ForeignKey to Employeer
        }
    """
    order_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='The order number of the purchase order'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        help_text='Supplier providing the products'
    )
    order_date = models.DateField(
        help_text='Date when the order was placed',
        blank=True,
        null=True,
        auto_now_add=True
    )
    expected_delivery = models.DateField(
        help_text='Expected delivery date',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=PURCHASE_ORDER_STATUS_CHOICES,
        default='draft',
        help_text='Current status of the purchase order'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about the order'
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Total value of the purchase order',
        default=0.00
    )
    
    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Purchase Order #{self.order_number}"
    
    def calculate_total(self):
        """Calculate the total value of the purchase order based on all items"""
        total = sum(item.calculate_total() for item in self.items.all())
        return total
    
    def update_total(self):
        """Update the total value of the purchase order"""
        new_total = self.calculate_total()
        # Usa update para evitar recursão e garantir que o total seja atualizado
        PurchaseOrder.objects.filter(pk=self.pk).update(total=new_total)
        # Atualiza o valor em memória tambem
        self.total = new_total
    
    def generate_unique_order_number(self):
        """Generate a unique order number.
        
        This method attempts to create a unique 5-digit order number
        by incrementing the last used number. It will retry up to 5 times
        in case of conflicts.
        
        Raises:
            IntegrityError: If unable to generate a unique number after max retries
        """
        if not self.order_number:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        last_purchase_order = (
                            PurchaseOrder.objects.select_for_update()
                            .order_by("-order_number")
                            .first()
                        )
                        if last_purchase_order and last_purchase_order.order_number:
                            try:
                                last_number = int(last_purchase_order.order_number)
                            except ValueError:
                                last_number = 0
                        else:
                            last_number = 0
                        new_number = last_number + 1
                        self.order_number = f"{new_number:05d}"
                except IntegrityError:
                    continue
                break
            else:
                raise IntegrityError("Unable to generate a unique order number after max retries")
    
    def save(self, *args, **kwargs):
        """Save the purchase order.
        
        This method generates a unique order number if not provided.
        """
        self.generate_unique_order_number()
        super().save(*args, **kwargs)

class PurchaseOrderItem(BaseModel):
    """Purchase Order Item for tracking individual products and their prices"""
    
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='The related purchase order'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchase_order_items',
        help_text='The product being purchased'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text='Quantity ordered'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Agreed price per unit'
    )
    
    class Meta:
        verbose_name = 'Purchase Order Item'
        verbose_name_plural = 'Purchase Order Items'
        ordering = ['purchase_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} @ ${self.unit_price}"
    
    def calculate_total(self):
        """Calculate the total value for this item"""
        return Decimal(str(self.unit_price)) * Decimal(str(self.quantity))
    
    def save(self, *args, **kwargs):
        """Save the purchase order item and update the order total"""
        super().save(*args, **kwargs)
        # Força a atualização do total do pedido
        self.purchase_order.update_total()
    
    def delete(self, *args, **kwargs):
        """Delete the purchase order item and update the order total"""
        order = self.purchase_order
        super().delete(*args, **kwargs)
        order.update_total()