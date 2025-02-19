import logging
from typing import Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import NullBooleanField
from apps.inventory.product.models import Product, ProductSku, ProductInStoreID
from apps.inventory.supplier.models import Supplier
from .home_depot_service import HomeDepotService, HomeDepotServiceException

logger = logging.getLogger(__name__)

class ProductServices:
    """Service for product operations"""
    
    @staticmethod
    def get_all_products() -> List[Dict[str, str]]:
        """Get all products from database
        
        Returns:
            List[Dict[str, str]]: List of dicts with product info
        """
        try:
            query = Product.objects.select_related('companie').values('id', 'name')
            return [{"id": str(p['id']), "name": p['name']} for p in query]
        except Exception as e:
            logger.error(f"Error getting all products: {str(e)}")
            return []
            
    @staticmethod
    def get_product_suppliers(product_id: str) -> List[Dict[str, str]]:
        """Get all suppliers for a product
        
        Args:
            product_id (str): ID of the product
            
        Returns:
            List[Dict[str, str]]: List of supplier info
        """
        try:
            product = Product.objects.get(id=product_id)
            suppliers = product.supplier.all().values('id', 'name', 'store_number')
            return [{
                "id": str(s['id']),
                "name": s['name'],
                "store_number": s['store_number']
            } for s in suppliers]
        except Exception as e:
            logger.error(f"Error getting suppliers for product {product_id}: {str(e)}")
            return []
            
    @staticmethod
    def search_and_save_home_depot_id(product_id: str) -> Dict[str, str]:
        """Search for product on Home Depot and save its ID
        
        Args:
            product_id (str): ID of the product to search
            
        Returns:
            Dict[str, str]: Dict with operation status and message
        """
        try:
            # Buscar produto
            product = Product.objects.get(id=product_id)
            
            # Verificar se Home Depot é o fornecedor
            if not product.supplier or product.supplier.name != 'Home Depot':
                return {
                    "status": "error",
                    "message": f"Home Depot is not the supplier for product: {product.name}"
                }
            
            # Criar serviço
            hd_service = HomeDepotService()
            
            # Buscar produto pelo nome
            search_results = hd_service.search_products(
                query=product.name,
                store_id=product.supplier.store_number,
                delivery_zip=product.companie.zip_code
            )
            
            if not search_results:
                return {
                    "status": "error",
                    "message": f"No products found on Home Depot for: {product.name}"
                }
            
            # Pegar primeiro resultado
            hd_product = search_results[0]
            product_id = hd_product['product_id']
            
            # Buscar detalhes completos
            product_details = hd_service.get_product_by_id(
                product_id=product_id,
                store_id=product.supplier.store_number,
                delivery_zip=product.companie.zip_code
            )
            
            if not product_details:
                return {
                    "status": "error",
                    "message": f"Could not get details for product: {product.name}"
                }
            
            with transaction.atomic():
                # Salvar ID na loja
                ProductInStoreID.objects.update_or_create(
                    product=product,
                    defaults={'in_store_id': product_id}
                )
                
                # Atualizar campos do produto
                price = product_details.get('price', 0.00)
                product.price = price if price and str(price).strip() else 0.00
                    
                if description := product_details.get('description'):
                    product.description = description
                    
                product.save()
            
            return {
                "status": "success",
                "message": f"Home Depot ID saved for product: {product.name}",
                "product_id": product_id,
                "price": price,
                "description": description[:100] + "..." if description else None
            }
            
        except ObjectDoesNotExist:
            return {
                "status": "error",
                "message": f"Product not found with ID: {product_id}"
            }
        except HomeDepotServiceException as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Error searching Home Depot ID: {str(e)}")
            return {
                "status": "error",
                "message": f"Error searching Home Depot ID: {str(e)}"
            }
            
    @staticmethod
    def update_product_from_home_depot(product_id: str) -> Dict[str, str]:
        """Update product info from Home Depot using saved ID
        
        Args:
            product_id (str): ID of the product to update
            
        Returns:
            Dict[str, str]: Dict with operation status and message
        """
        try:
            # Buscar produto
            product = Product.objects.get(id=product_id)
            
            # Verificar se Home Depot é o fornecedor
            if not product.supplier or product.supplier.name != 'Home Depot':
                return {
                    "status": "error",
                    "message": f"Home Depot is not the supplier for product: {product.name}"
                }
            
            # Buscar ID na loja
            store_id = ProductInStoreID.objects.filter(product=product).first()
            if not store_id:
                return {
                    "status": "error",
                    "message": f"No Home Depot ID found for product: {product.name}"
                }
            
            # Criar serviço
            hd_service = HomeDepotService()
            
            # Buscar detalhes atualizados
            product_details = hd_service.get_product_by_id(
                product_id=store_id.in_store_id,
                store_id=product.supplier.store_number,
                delivery_zip=product.companie.zip_code
            )
            
            if not product_details:
                return {
                    "status": "error",
                    "message": f"Could not get details from Home Depot for: {product.name}"
                }
            
            with transaction.atomic():
                # Atualizar campos do produto
                price = product_details.get('price', 0.00)
                product.price = price if price and str(price).strip() else 0.00
                    
                if description := product_details.get('description'):
                    product.description = description
                    
                product.save()
            
            return {
                "status": "success",
                "message": f"Product updated from Home Depot: {product.name}",
                "price": price,
                "description": description[:100] + "..." if description else None
            }
            
        except ObjectDoesNotExist:
            return {
                "status": "error",
                "message": f"Product not found with ID: {product_id}"
            }
        except HomeDepotServiceException as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Error updating from Home Depot: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating from Home Depot: {str(e)}"
            }
