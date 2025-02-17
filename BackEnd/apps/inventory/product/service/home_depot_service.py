import os
import logging
from typing import Dict, List, Optional
from django.conf import settings
from rest_framework import status
import serpapi

logger = logging.getLogger(__name__)

class HomeDepotServiceException(Exception):
    """Exception for Home Depot service errors"""
    def __init__(self, message: str, status_code: int = 400, details: Dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class HomeDepotService:
    """Service for interacting with Home Depot API"""
    
    def __init__(self):
        """Initialize service with API key"""
        self.api_key = settings.SERPAPI_API_KEY
        if not self.api_key:
            raise HomeDepotServiceException(
                "SERPAPI_API_KEY not configured",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        self.client = serpapi.Client(api_key=self.api_key)
        
    def _extract_price(self, product_data: Dict) -> Optional[float]:
        """Extract price from product data
        
        Args:
            product_data (Dict): Product data from API
            
        Returns:
            Optional[float]: Price if found, None otherwise
        """
        try:
            price = product_data.get('price')
            if isinstance(price, (int, float)):
                return float(price)
            elif isinstance(price, str):
                # Remover '$' e converter para float
                return float(price.replace('$', '').strip())
            return None
        except (ValueError, TypeError):
            return None
    
    def search_products(
        self,
        query: str,
        store_id: Optional[str] = None,
        delivery_zip: Optional[str] = None
    ) -> List[Dict]:
        """Search for products on Home Depot
        
        Args:
            query (str): Search query
            store_id (str, optional): Store ID to check availability
            delivery_zip (str, optional): ZIP code for delivery
            
        Returns:
            List[Dict]: List of products found
        """
        try:
            params = {
                "engine": "home_depot",
                "q": query
            }
            
            if store_id:
                params["store_id"] = store_id
                
            if delivery_zip:
                params["delivery_zip"] = delivery_zip
            
            results = self.client.search(params)
            
            if 'products' in results and isinstance(results['products'], list):
                return [{
                    "product_id": product.get('product_id'),
                    "title": product.get('title'),
                    "price": self._extract_price(product),
                    "brand": product.get('brand'),
                    "store_id": store_id,
                    "delivery_zip": delivery_zip
                } for product in results['products']]
                
            return []
            
        except Exception as e:
            raise HomeDepotServiceException(
                f"Error searching products: {str(e)}",
                status_code=status.HTTP_502_BAD_GATEWAY
            )
            
    def get_product_by_id(
        self,
        product_id: str,
        store_id: Optional[str] = None,
        delivery_zip: Optional[str] = None
    ) -> Optional[Dict]:
        """Get product details from Home Depot
        
        Args:
            product_id (str): Home Depot product ID
            store_id (str, optional): Store ID to check availability
            delivery_zip (str, optional): ZIP code for delivery
            
        Returns:
            Optional[Dict]: Product details if found, None otherwise
        """
        try:
            params = {
                "engine": "home_depot_product",
                "product_id": product_id
            }
            
            if store_id:
                params["store_id"] = store_id
                
            if delivery_zip:
                params["delivery_zip"] = delivery_zip
            
            results = self.client.search(params)
            
            if 'product_results' in results and isinstance(results['product_results'], dict):
                product_data = results['product_results']
                
                return {
                    "title": product_data.get('title'),
                    "price": self._extract_price(product_data),
                    "description": product_data.get('description'),
                    "brand": product_data.get('brand'),
                    "model_number": product_data.get('model_number'),
                    "store_id": store_id,
                    "delivery_zip": delivery_zip
                }
                
            return None
            
        except Exception as e:
            raise HomeDepotServiceException(
                f"Error getting product details: {str(e)}",
                status_code=status.HTTP_502_BAD_GATEWAY
            )
