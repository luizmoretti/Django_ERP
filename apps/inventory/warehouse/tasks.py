import logging
from celery import shared_task
from django.db.models import F
from apps.inventory.product.models import Product
from apps.inventory.warehouse.models import WarehouseProduct
from apps.inventory.warehouse.notifications.handlers import WarehouseNotificationHandler
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

@shared_task(
    name='check_low_stock',
    queue='warehouse',
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True
)
def check_low_stock():
    """
    Check for products with low stock across all warehouses.
    """
    try:
        # Get all warehouse products where current quantity is below minimum
        low_stock_products = WarehouseProduct.objects.filter(
            current_quantity__lt=F('product__min_quantity'),
            product__min_quantity__gt=0  # Only check products with defined minimums
        ).select_related('product', 'warehouse')
        
        total_products = low_stock_products.count()
        logger.info(f"Found {total_products} products with low stock")
        
        if total_products == 0:
            # Log all products and their stock levels for debugging
            all_products = WarehouseProduct.objects.select_related('product', 'warehouse').all()
            for wp in all_products:
                logger.debug(
                    f"Product: {wp.product.name}, "
                    f"Current: {wp.current_quantity}, "
                    f"Min: {wp.product.min_quantity}, "
                    f"Warehouse: {wp.warehouse.name}"
                )
        
        # Process each low stock item
        for warehouse_product in low_stock_products:
            try:
                logger.info(
                    f"Processing low stock notification for "
                    f"Product: {warehouse_product.product.name}, "
                    f"Current: {warehouse_product.current_quantity}, "
                    f"Min: {warehouse_product.product.min_quantity}, "
                    f"Warehouse: {warehouse_product.warehouse.name}"
                )
                
                WarehouseNotificationHandler.notify_low_stock(
                    product=warehouse_product.product,
                    warehouse=warehouse_product.warehouse,
                    current_quantity=warehouse_product.current_quantity
                )
            except Exception as e:
                logger.error(f"Error processing product {warehouse_product.product.name}: {str(e)}")
        
        return f"Checked {total_products} products for low stock"
        
    except Exception as e:
        logger.error(f"Error in check_low_stock task: {str(e)}")
        raise

@shared_task(
    name='check_specific_product',
    queue='warehouse',
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True
)
def check_specific_product(product_id=None):
    """
    Check stock levels for a specific product across all warehouses.
    """
    if not product_id:
        return "No product_id provided"
        
    try:
        product = Product.objects.get(id=product_id)
        logger.info(f"Checking stock for product: {product.name}")
        
        # Get all warehouse entries for this product
        warehouse_products = WarehouseProduct.objects.filter(
            product=product,
            current_quantity__lt=F('product__min_quantity'),
            product__min_quantity__gt=0
        ).select_related('warehouse')
        
        total_warehouses = warehouse_products.count()
        logger.info(f"Found {total_warehouses} warehouses with low stock")
        
        # Check each warehouse
        for warehouse_product in warehouse_products:
            try:
                logger.info(
                    f"Processing warehouse: {warehouse_product.warehouse.name}, "
                    f"Current: {warehouse_product.current_quantity}, "
                    f"Min: {product.min_quantity}"
                )
                
                WarehouseNotificationHandler.notify_low_stock(
                    product=warehouse_product.product,
                    warehouse=warehouse_product.warehouse,
                    current_quantity=warehouse_product.current_quantity
                )
            except Exception as e:
                logger.error(f"Error processing warehouse {warehouse_product.warehouse.name}: {str(e)}")
            
        return f"Checked product {product.name} in {total_warehouses} warehouses"
        
    except Product.DoesNotExist:
        logger.warning(f"Product with id {product_id} not found")
        return f"Product with id {product_id} not found"
    except Exception as e:
        logger.error(f"Error checking product: {str(e)}")
        return f"Error checking product: {str(e)}"