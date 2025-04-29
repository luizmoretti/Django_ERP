import logging
import os
import requests
import json
from typing import Dict, List, Optional, Any, Union
import django

logger = logging.getLogger(__name__)
        
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
class GoogleLocalSearchService:
    """
    Service for interacting with Google Local data via SerpAPI.
    
    This service facilitates the retrieval of business information using
    the Google Local API from SerpAPI. It processes user search queries to
    extract detailed business information that can be used to enhance
    customer records.
    """
    
    def __init__(self):
        """Initialize the service with API key from settings"""
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        
    def _get_api_key(self) -> str:
        """
        Retrieve the SerpAPI key from settings or environment variables.
        
        Returns:
            str: The API key for SerpAPI
        """
        # First try Django settings if running inside Django
        api_key = None
        
        try:
            from django.conf import settings
            api_key = getattr(settings, 'SERPAPI_API_KEY', None)
        except (ImportError, ModuleNotFoundError):
            logger.info("[GOOGLE LOCAL SERVICE] - Not running within Django context")
        except Exception as e:
            logger.warning(f"[GOOGLE LOCAL SERVICE] - Error accessing Django settings: {str(e)}")
        
        # Fall back to environment variable if not found in settings
        if not api_key:
            api_key = os.environ.get('SERPAPI_API_KEY')
            
        if not api_key:
            logger.warning("[GOOGLE LOCAL SERVICE] - No SerpAPI key found in settings or environment")
            
        return api_key
        
    def _get_base_url(self) -> str:
        """
        Retrieve the SerpAPI base URL from settings or environment variables.
        
        Returns:
            str: The base URL for SerpAPI
        """
        # First try Django settings if running inside Django
        base_url = None
        
        try:
            from django.conf import settings
            base_url = getattr(settings, 'SERPAPI_BASE_URL', None)
        except (ImportError, ModuleNotFoundError):
            logger.info("[GOOGLE LOCAL SERVICE] - Not running within Django context")
        except Exception as e:
            logger.warning(f"[GOOGLE LOCAL SERVICE] - Error accessing Django settings: {str(e)}")
        
        # Fall back to environment variable
        if not base_url:
            base_url = os.environ.get('SERPAPI_BASE_URL')
            
        # Default fallback if not configured
        if not base_url:
            base_url = "https://serpapi.com/search"
            logger.warning(f"[GOOGLE LOCAL SERVICE] - No SerpAPI base URL found in settings or environment, using default: {base_url}")
            
        return base_url
    
    def search_local_businesses(self, query: str, location: Optional[str] = None, 
                               limit: int = None, include_all_pages: bool = False) -> List[Dict[str, Any]]:
        """
        Search for local businesses based on user query and location.
        
        Args:
            query (str): Search term provided by user
            location (str, optional): Location to search from
            limit (int, optional): Maximum number of results to return per page
            include_all_pages (bool): Whether to retrieve results from all available pages
            
        Returns:
            List[Dict]: Processed results with business information
        """
        if not self.api_key:
            logger.error("[GOOGLE LOCAL SERVICE] - Cannot search without API key")
            return []
            
        params = {
            "api_key": self.api_key,
            "engine": "google_local",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        }
        
        if location:
            params["location"] = location
            
        try:
            all_results = []
            current_page = 1
            
            # First request to get initial results
            logger.info(f"[GOOGLE LOCAL SERVICE] - Requesting page {current_page}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"[GOOGLE LOCAL SERVICE] - Retrieved page {current_page}")
            
            # Process the first page of results
            results = self._process_local_results(data, limit)
            all_results.extend(results)
            
            # If pagination is requested, fetch all pages
            if include_all_pages and 'serpapi_pagination' in data and 'other_pages' in data['serpapi_pagination']:
                other_pages = data['serpapi_pagination']['other_pages']
                
                for page_num, page_url in sorted(other_pages.items(), key=lambda x: int(x[0])):
                    logger.info(f"[GOOGLE LOCAL SERVICE] - Requesting page {page_num}")
                    
                    # Extract 'start' parameter from the URL
                    start_param = None
                    if 'start=' in page_url:
                        start_value = page_url.split('start=')[1].split('&')[0]
                        start_param = int(start_value)
                    
                    if start_param is not None:
                        # Create new params with the start parameter
                        page_params = params.copy()
                        page_params['start'] = start_param
                        
                        # Make request for this page
                        page_response = requests.get(self.base_url, params=page_params)
                        page_response.raise_for_status()
                        
                        page_data = page_response.json()
                        
                        logger.info(f"[GOOGLE LOCAL SERVICE] - Retrieved page {page_num}")
                        
                        # Process this page's results and add to all_results
                        page_results = self._process_local_results(page_data, limit)
                        all_results.extend(page_results)
            
            return all_results
            
        except requests.RequestException as e:
            logger.error(f"[GOOGLE LOCAL SERVICE] - Request error: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"[GOOGLE LOCAL SERVICE] - Invalid JSON response: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"[GOOGLE LOCAL SERVICE] - Error fetching data: {str(e)}")
            return []
            
    def _process_local_results(self, data: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Extract and format relevant business information from API response.
        
        Args:
            data (Dict): Raw API response data
            limit (int, optional): Maximum number of results to return
            
        Returns:
            List[Dict]: Formatted business records
        """
        if "local_results" not in data:
            logger.warning("[GOOGLE LOCAL SERVICE] - No local results found in response")
            return []
            
        results = []
        local_results = data["local_results"]
        
        # Apply limit if specified
        if limit is not None:
            local_results = local_results[:limit]
            
        for item in local_results:
            business = {
                "name": item.get("title", "INFO NOT INCLUDED"),
                "address": item.get("address", "INFO NOT INCLUDED"),
                "phone": self._extract_phone(item) or "INFO NOT INCLUDED",
                "website": self._extract_website(item) or "INFO NOT INCLUDED",
                "rating": item.get("rating", "NO RATING FOUND"),
                "reviews": item.get("reviews", "NO REVIEWS FOUND"),
                "category": item.get("type", "INFO NOT INCLUDED"),
                "hours": item.get("hours", "INFO NOT INCLUDED"),
                "coordinates": item.get("gps_coordinates", "INFO NOT INCLUDED"),
                "place_id": item.get("place_id", "INFO NOT INCLUDED")
            }
            results.append(business)
            
        return results
        
    def _extract_phone(self, item: Dict[str, Any]) -> Optional[str]:
        """
        Extract phone number from business data if available.
        
        Args:
            item (Dict): Business data from API
            
        Returns:
            Optional[str]: Phone number or None
        """
        if "phone" in item:
            return item["phone"]
        return "NO PHONE FOUND"
    
    def _extract_website(self, item: Dict[str, Any]) -> Optional[str]:
        """
        Extract website URL from business data if available.
        
        Args:
            item (Dict): Business data from API
            
        Returns:
            Optional[str]: Website URL or None
        """
        if "links" in item and "website" in item["links"]:
            return item["links"]["website"]
        return "NO WEBSITE FOUND"

def get_business_data_from_user_input() -> List[Dict[str, Any]]:
    """
    Interactive function to search for business data based on user input.
    
    Returns:
        List[Dict]: List of business records matching search criteria
    """
    print("\n=== Google Local Business Search ===")
    query = input("Enter search term (e.g., restaurant, plumber): ")
    location = input("Enter location (optional, e.g., New York, NY): ")
    all_pages = input("Retrieve all pages? (y/n): ").lower().strip() == 'y'
    
    print("\nSearching for businesses, please wait...")
    service = GoogleLocalSearchService()
    results = service.search_local_businesses(query, location, include_all_pages=all_pages)
    
    if not results:
        print("No results found. Try a different search term or location.")
        return []
        
    print(f"\nFound {len(results)} businesses:")
    for i, business in enumerate(results, 1):
        print(f"\n{i}. {business['name']}")
        print(f"   Address: {business['address']}")
        print(f"   Phone: {business['phone']}")
        print(f"   Website: {business['website']}")
        print(f"   Hours: {business['hours']}")
        print(f"   Rating: {business['rating']} ({business['reviews']} reviews)")
        print(f"   Category: {business['category']}")
        
    # Ask if user wants to export results
    export = input("\nDo you want to export results to CSV? (y/n): ").lower().strip() == 'y'
    if export:
        try:
            import csv
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"business_search_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["name", "address", "phone", "website", "rating", 
                             "reviews", "category", "hours", "place_id"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for business in results:
                    writer.writerow({
                        "name": business["name"],
                        "address": business["address"],
                        "phone": business["phone"],
                        "website": business["website"],
                        "rating": business["rating"],
                        "reviews": business["reviews"],
                        "category": business["category"],
                        "hours": business["hours"],
                        "place_id": business["place_id"]
                    })
                
            print(f"Results exported to {filename}")
        except Exception as e:
            print(f"Error exporting results: {str(e)}")
        
    return results

# Example usage
if __name__ == "__main__":
    businesses = get_business_data_from_user_input()