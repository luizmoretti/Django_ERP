"""
Cache utilities for the DryWall WareHouse ERP system.
Provides decorators and helper functions for caching operations.
"""

from functools import wraps
from django.core.cache import caches
from django.conf import settings
from rest_framework.response import Response
from rest_framework.request import Request
from typing import Any, Callable, Optional, Union
import hashlib
import json

def get_cache(alias: str = 'default'):
    """Get the cache instance for the given alias."""
    return caches[alias]

def make_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """
    Create a cache key from prefix and arguments.
    Handles complex types by converting them to JSON strings.
    """
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (dict, list, tuple)):
            key_parts.append(hashlib.md5(json.dumps(arg, sort_keys=True).encode()).hexdigest())
        else:
            key_parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        for key, value in sorted_items:
            if isinstance(value, (dict, list, tuple)):
                key_parts.append(f"{key}:{hashlib.md5(json.dumps(value, sort_keys=True).encode()).hexdigest()}")
            else:
                key_parts.append(f"{key}:{value}")
    
    return ":".join(key_parts)

def cache_response(
    timeout: int = None,
    key_prefix: str = '',
    cache_alias: str = 'default',
    key_func: Callable = None
):
    """
    Cache decorator for DRF views.
    
    Args:
        timeout: Cache timeout in seconds. If None, uses the cache's default
        key_prefix: Prefix for the cache key
        cache_alias: Cache backend to use
        key_func: Custom function to generate cache key
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request: Request, *args, **kwargs):
            # Get cache backend
            cache = get_cache(cache_alias)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                # Default key generation
                key_parts = [
                    key_prefix,
                    request.method,
                    request.path,
                ]
                
                # Add query params if any
                if request.query_params:
                    key_parts.append(hashlib.md5(
                        json.dumps(dict(request.query_params), sort_keys=True).encode()
                    ).hexdigest())
                
                # Add user info if authenticated
                if request.user.is_authenticated:
                    key_parts.append(str(request.user.id))
                
                cache_key = make_key(*key_parts)
            
            # Try to get from cache
            response_data = cache.get(cache_key)
            
            if response_data is not None:
                return Response(response_data)
            
            # If not in cache, generate response
            response = view_func(view_instance, request, *args, **kwargs)
            
            # Cache the response data
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout)
            
            return response
        return _wrapped_view
    return decorator

def cache_method_result(
    timeout: int = None,
    key_prefix: str = '',
    cache_alias: str = 'default'
):
    """
    Cache decorator for class methods.
    
    Args:
        timeout: Cache timeout in seconds. If None, uses the cache's default
        key_prefix: Prefix for the cache key
        cache_alias: Cache backend to use
    """
    def decorator(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            cache = get_cache(cache_alias)
            
            # Generate cache key
            cache_key = make_key(
                key_prefix,
                method.__name__,
                self.__class__.__name__,
                getattr(self, 'id', None),
                *args,
                **kwargs
            )
            
            # Try to get from cache
            result = cache.get(cache_key)
            
            if result is None:
                result = method(self, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapped
    return decorator

def invalidate_cache_key(key: str, cache_alias: str = 'default'):
    """Invalidate a specific cache key."""
    cache = get_cache(cache_alias)
    cache.delete(key)

def invalidate_cache_pattern(pattern: str, cache_alias: str = 'default'):
    """
    Invalidate all cache keys matching a pattern.
    Note: This is a basic implementation. For production, consider using Redis' SCAN command.
    """
    cache = get_cache(cache_alias)
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)

def cache_get_or_set(
    key: str,
    default_func: Callable,
    timeout: Optional[int] = None,
    cache_alias: str = 'default'
) -> Any:
    """
    Get value from cache or set it if missing.
    
    Args:
        key: Cache key
        default_func: Function to generate value if not in cache
        timeout: Cache timeout in seconds
        cache_alias: Cache backend to use
    
    Returns:
        Cached value
    """
    cache = get_cache(cache_alias)
    value = cache.get(key)
    
    if value is None:
        value = default_func()
        cache.set(key, value, timeout)
    
    return value

# Cache key prefixes for different types of data
CACHE_KEYS = {
    'product': 'product:{id}',
    'warehouse': 'warehouse:{id}',
    'movements': 'movements:{id}',
    'customer': 'customer:{id}',
    'supplier': 'supplier:{id}',
    'user': 'user:{id}',
    'company': 'company:{id}',
}

def get_cache_key(key_type: str, **kwargs) -> str:
    """
    Get a formatted cache key for a specific type of data.
    
    Args:
        key_type: Type of data (e.g., 'product', 'warehouse', 'movements')
        **kwargs: Key-value pairs to format the cache key
    
    Returns:
        Formatted cache key string
    
    Example:
        >>> get_cache_key('movements', companie_id='123', method='GET', url='/api/v1/movements/', query_params='*')
        'movements:123:GET:/api/v1/movements/:*'
    """
    if key_type not in CACHE_KEYS:
        raise ValueError(f"Invalid key_type: {key_type}. Must be one of {list(CACHE_KEYS.keys())}")
    
    try:
        # Get the key template
        key_template = CACHE_KEYS[key_type]
        
        # For movements, handle query params specially
        if key_type == 'movements' and 'query_params' in kwargs:
            if isinstance(kwargs['query_params'], (dict, list)):
                kwargs['query_params'] = hashlib.md5(
                    json.dumps(kwargs['query_params'], sort_keys=True).encode()
                ).hexdigest()
        
        # Format the key template with provided kwargs
        return key_template.format(**kwargs)
        
    except KeyError as e:
        missing_key = str(e).strip("'")
        raise ValueError(
            f"Missing required parameter '{missing_key}' for key_type '{key_type}'. "
            f"Required parameters: {key_template.count('{')}"
        )
    except Exception as e:
        raise ValueError(f"Error generating cache key: {str(e)}")
