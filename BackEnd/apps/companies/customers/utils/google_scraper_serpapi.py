import logging
import os
import httpx  # Changed from requests to httpx for async
import json
import sys
from typing import Dict, List, Optional, Any, Union
import django
import asyncio  # Added for asyncio operations
from django.core.cache import cache
import hashlib
import tenacity

logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.append(backend_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
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
        self._http_client = None
        
    def _get_cache_key(self, query, location, limit, include_all_pages):
        """Generate a unique cache key for search params"""
        key_parts = f"{query}:{location}:{limit}:{include_all_pages}"
        return f"google_search:{hashlib.sha256(key_parts.encode()).hexdigest()}"
        
    def _get_api_key(self) -> str:
        """
        Retrieve the SerpAPI key from settings or environment variables.
        
        Returns:
            str: The API key for SerpAPI
        """
        api_key = None
        try:
            from django.conf import settings
            api_key = getattr(settings, "SERPAPI_API_KEY", None)
        except (ImportError, ModuleNotFoundError):
            logger.info("[GOOGLE LOCAL SERVICE ASYNC] - Not running within Django context for API key")
        except Exception as e:
            logger.warning(f"[GOOGLE LOCAL SERVICE ASYNC] - Error accessing Django settings for API key: {str(e)}")
        
        if not api_key:
            api_key = os.environ.get("SERPAPI_API_KEY")
            
        if not api_key:
            logger.warning("[GOOGLE LOCAL SERVICE ASYNC] - No SerpAPI key found in settings or environment")
        return api_key
        
    def _get_base_url(self) -> str:
        """
        Retrieve the SerpAPI base URL from settings or environment variables.
        
        Returns:
            str: The base URL for SerpAPI
        """
        base_url = None
        try:
            from django.conf import settings
            base_url = getattr(settings, "SERPAPI_BASE_URL", None)
        except (ImportError, ModuleNotFoundError):
            logger.info("[GOOGLE LOCAL SERVICE ASYNC] - Not running within Django context for base URL")
        except Exception as e:
            logger.warning(f"[GOOGLE LOCAL SERVICE ASYNC] - Error accessing Django settings for base URL: {str(e)}")
        
        if not base_url:
            base_url = os.environ.get("SERPAPI_BASE_URL")
            
        if not base_url:
            base_url = "https://serpapi.com/search"
            logger.warning(f"[GOOGLE LOCAL SERVICE ASYNC] - No SerpAPI base URL found, using default: {base_url}")
        return base_url
    
    def _get_http_client(self):
        """Get or create a shared HTTP client"""
        if self.__class__._http_client is None:
            timeout = httpx.Timeout(30.0, connect=10.0)
            limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
            self.__class__._http_client = httpx.AsyncClient(timeout=timeout, limits=limits)
        return self.__class__._http_client
    
    
    
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        retry=tenacity.retry_if_exception_type((httpx.HTTPError, httpx.NetworkError)),
        reraise=True
    )
    async def _fetch_page(self, client: httpx.AsyncClient, params: Dict[str, Any], page_num_logging: Union[int, str]) -> Optional[Dict[str, Any]]:
        """ Helper function to fetch a single page asynchronously. """
        try:
            logger.info(f"[GOOGLE LOCAL SERVICE ASYNC] - Requesting page {page_num_logging}")
            response = await client.get(self.base_url, params=params)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            data = response.json()
            logger.info(f"[GOOGLE LOCAL SERVICE ASYNC] - Retrieved page {page_num_logging}")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"[GOOGLE LOCAL SERVICE ASYNC] - HTTP error for page {page_num_logging}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"[GOOGLE LOCAL SERVICE ASYNC] - Request error for page {page_num_logging}: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"[GOOGLE LOCAL SERVICE ASYNC] - Invalid JSON for page {page_num_logging}: {str(e)}")
        except Exception as e:
            logger.error(f"[GOOGLE LOCAL SERVICE ASYNC] - Error fetching page {page_num_logging}: {str(e)}")
        return None

    async def search_local_businesses(self, query: str, location: Optional[str] = None, 
                                      limit: int = None, include_all_pages: bool = False) -> List[Dict[str, Any]]:
        """
        Search for local businesses asynchronously based on user query and location.
        
        Args:
            query (str): Search term provided by user
            location (str, optional): Location to search from
            limit (int, optional): Maximum number of results to return per page (applied after fetching)
            include_all_pages (bool): Whether to retrieve results from all available pages
            
        Returns:
            List[Dict]: Processed results with business information
        """
        if not self.api_key:
            logger.error("[GOOGLE LOCAL SERVICE ASYNC] - Cannot search without API key")
            return []
            
        base_params = {
            "api_key": self.api_key,
            "engine": "google_local",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        }
        
        if location:
            base_params["location"] = location
            
        all_results_processed = []
        
        async with httpx.AsyncClient() as client:
            # First request to get initial results and pagination info
            initial_data = await self._fetch_page(client, base_params, page_num_logging=1)
            
            if not initial_data:
                return []

            results_page_1 = self._process_local_results(initial_data) # Limit applied later if not include_all_pages
            all_results_processed.extend(results_page_1)
            
            # If pagination is requested and available, fetch all other pages concurrently
            if include_all_pages and 'serpapi_pagination' in initial_data and 'other_pages' in initial_data['serpapi_pagination']:
                other_pages_info = initial_data['serpapi_pagination']['other_pages']
                tasks = []
                
                for page_num_str, page_url in sorted(other_pages_info.items(), key=lambda x: int(x[0])):
                    start_param_val = None
                    if 'start=' in page_url:
                        try:
                            start_value_str = page_url.split('start=')[1].split('&')[0]
                            start_param_val = int(start_value_str)
                        except (IndexError, ValueError) as e:
                            logger.warning(f"[GOOGLE LOCAL SERVICE ASYNC] - Could not parse 'start' param from URL {page_url}: {e}")
                            continue # Skip this page if URL is malformed
                    
                    if start_param_val is not None:
                        page_params = base_params.copy()
                        page_params['start'] = start_param_val
                        tasks.append(self._fetch_page(client, page_params, page_num_logging=page_num_str))
                
                if tasks:
                    logger.info(f"[GOOGLE LOCAL SERVICE ASYNC] - Fetching {len(tasks)} additional pages concurrently.")
                    pages_data_list = await asyncio.gather(*tasks)
                    for page_data in pages_data_list:
                        if page_data:
                            processed_page_results = self._process_local_results(page_data)
                            all_results_processed.extend(processed_page_results)
            
            # Apply limit to the total collected results if not fetching all pages and limit is set
            if not include_all_pages and limit is not None and len(all_results_processed) > limit:
                 return all_results_processed[:limit]
            elif limit is not None and len(all_results_processed) > limit: # if include_all_pages but still want a total limit
                 logger.info(f"[GOOGLE LOCAL SERVICE ASYNC] - Limiting total results from {len(all_results_processed)} to {limit}")
                 return all_results_processed[:limit]

            return all_results_processed

    def search_local_businesses_sync(self, query: str, location: Optional[str] = None, 
                                     limit: int = None, include_all_pages: bool = False) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for search_local_businesses async method.
        
        This method runs the async search method in a new event loop to maintain
        compatibility with synchronous code such as Django service layer.
        
        Args:
            query (str): Search term provided by user
            location (str, optional): Location to search from
            limit (int, optional): Maximum number of results to return per page
            include_all_pages (bool): Whether to retrieve results from all available pages
            
        Returns:
            List[Dict]: Processed results with business information
        """
        # Verify cache first
        cache_key = self._get_cache_key(query, location, limit, include_all_pages)
        cached_results = cache.get(cache_key)
        
        if cached_results:
            logger.info(f"[GOOGLE LOCAL SERVICE] - Returning cached results for '{query}' in '{location}'")
            return cached_results
        
        try:
            logger.info(f"[GOOGLE LOCAL SERVICE] - Starting synchronous search for '{query}' in '{location}'")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                self.search_local_businesses(
                    query=query,
                    location=location,
                    limit=limit,
                    include_all_pages=include_all_pages
                )
            )
            loop.close()
            logger.info(f"[GOOGLE LOCAL SERVICE] - Completed synchronous search with {len(results)} results")
            
            # Save results in cache
            if results:
                logger.info(f"[GOOGLE LOCAL SERVICE] - Saving results in cache for '{query}' in '{location}'")
                cache.set(cache_key, results, timeout=3600) # 1 Hour
            
            return results
        except Exception as e:
            logger.error(f"[GOOGLE LOCAL SERVICE] - Error in synchronous search: {str(e)}")
            return []
            
    def _process_local_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and format relevant business information from API response.
        No limit applied here anymore, it's applied after all data is fetched or on the first page if not include_all_pages.
        
        Args:
            data (Dict): Raw API response data
            
        Returns:
            List[Dict]: Formatted business records
        """
        if "local_results" not in data or not data["local_results"]:
            logger.warning("[GOOGLE LOCAL SERVICE ASYNC] - No local results found in response data chunk.")
            return []
            
        results = []
        local_results_data = data["local_results"]
        
        for item in local_results_data:
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
        if "phone" in item:
            return item["phone"]
        return "NO PHONE FOUND"
    
    def _extract_website(self, item: Dict[str, Any]) -> Optional[str]:
        if "links" in item and "website" in item["links"]:
            return item["links"]["website"]
        return "NO WEBSITE FOUND"

async def get_business_data_from_user_input_async() -> List[Dict[str, Any]]:
    """
    Interactive async function to search for business data based on user input.
    
    Returns:
        List[Dict]: List of business records matching search criteria
    """
    print("\n=== Google Local Business Search (Async) ===")
    query = input("Enter search term (e.g., restaurant, plumber): ")
    location = input("Enter location (optional, e.g., New York, NY): ")
    all_pages_input = input("Retrieve all pages? (y/n): ").lower().strip()
    include_all_pages = all_pages_input == 'y'
    
    limit_input = input("Enter maximum number of results (optional, e.g., 10, press Enter for no limit): ").strip()
    limit = int(limit_input) if limit_input.isdigit() else None

    print("\nSearching for businesses asynchronously, please wait...")
    service = GoogleLocalSearchService()
    # Note: In a real async UI, input() would be non-blocking or handled differently.
    # For this script, input() is still blocking.
    results = await service.search_local_businesses(query, location, limit=limit, include_all_pages=include_all_pages)
    
    if not results:
        print("No results found. Try a different search term or location.")
        return []
        
    print(f"\nFound {len(results)} businesses:")
    for i, business in enumerate(results, 1):
        print(f"\n{i}. {business['name']}")
        print(f"   Address: {business['address']}")
        print(f"   Phone: {business['phone']}")
        print(f"   Website: {business['website']}")
        # Add other fields as needed, e.g., hours, rating
        
    export_input = input("\nDo you want to export results to CSV? (y/n): ").lower().strip()
    if export_input == 'y':
        try:
            import csv
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"business_search_async_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["name", "address", "phone", "website", "rating", 
                             "reviews", "category", "hours", "place_id"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                
                writer.writeheader()
                for business in results:
                    writer.writerow(business)
                
            print(f"Results exported to {filename}")
        except Exception as e:
            print(f"Error exporting results: {str(e)}")
            
    return results

# Example usage for the async version
if __name__ == "__main__":
    # Configure basic logging for seeing the service logs
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Set API key and Base URL via environment variables if not in Django settings
    # Example: export SERPAPI_API_KEY="your_actual_api_key_here"
    #          export SERPAPI_BASE_URL="https://serpapi.com/search" (optional, has default)
    if not os.environ.get("SERPAPI_API_KEY"):
        print("Warning: SERPAPI_API_KEY environment variable not set. The script might not work.")
        print("Please set it, e.g., export SERPAPI_API_KEY='your_key'")

    asyncio.run(get_business_data_from_user_input_async())