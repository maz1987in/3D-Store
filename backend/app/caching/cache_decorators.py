"""
Cache Decorators

Decorators for easy caching integration with functions and methods.
"""

import functools
import inspect
from typing import Any, Optional, Callable, Union, List
from flask import current_app

from .cache_service import CacheService
from .cache_config import CacheConfig


def cache_result(
    timeout: Optional[int] = None,
    key_prefix: str = "",
    key_func: Optional[Callable] = None,
    unless: Optional[Callable] = None,
    cache_errors: bool = False
):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
        key_func: Custom function to generate cache key
        unless: Function that returns True to skip caching
        cache_errors: Whether to cache error results
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if caching should be skipped
            if unless and unless(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Get cache service
            cache_service = get_cache_service()
            if not cache_service:
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _generate_cache_key(func, key_prefix, *args, **kwargs)
            
            # Try to get from cache
            try:
                result = cache_service.get(cache_key)
                if result is not None:
                    current_app.logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return result
            except Exception as e:
                current_app.logger.error(f"Cache get error for {func.__name__}: {str(e)}")
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                
                # Cache the result
                try:
                    cache_service.set(cache_key, result, timeout)
                    current_app.logger.debug(f"Cached result for {func.__name__}: {cache_key}")
                except Exception as e:
                    current_app.logger.error(f"Cache set error for {func.__name__}: {str(e)}")
                
                return result
            except Exception as e:
                if cache_errors:
                    try:
                        cache_service.set(cache_key, {'error': str(e)}, timeout)
                    except Exception:
                        pass
                raise
        
        return wrapper
    return decorator


def cache_invalidate(
    pattern: Optional[str] = None,
    keys: Optional[List[str]] = None,
    key_func: Optional[Callable] = None
):
    """
    Decorator to invalidate cache after function execution.
    
    Args:
        pattern: Pattern to match keys for invalidation
        keys: Specific keys to invalidate
        key_func: Function to generate keys for invalidation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)
            
            # Get cache service
            cache_service = get_cache_service()
            if not cache_service:
                return result
            
            # Invalidate cache
            try:
                if pattern:
                    invalidated_count = cache_service.invalidate_pattern(pattern)
                    current_app.logger.debug(f"Invalidated {invalidated_count} keys matching pattern: {pattern}")
                elif keys:
                    cache_service.delete_many(keys)
                    current_app.logger.debug(f"Invalidated keys: {keys}")
                elif key_func:
                    keys_to_invalidate = key_func(*args, **kwargs)
                    if isinstance(keys_to_invalidate, list):
                        cache_service.delete_many(keys_to_invalidate)
                    else:
                        cache_service.delete(keys_to_invalidate)
                    current_app.logger.debug(f"Invalidated keys: {keys_to_invalidate}")
            except Exception as e:
                current_app.logger.error(f"Cache invalidation error for {func.__name__}: {str(e)}")
            
            return result
        
        return wrapper
    return decorator


def cache_warmup(timeout: Optional[int] = None):
    """
    Decorator to mark functions for cache warmup.
    
    Args:
        timeout: Cache timeout for warmup data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)
            
            # Get cache service
            cache_service = get_cache_service()
            if not cache_service:
                return result
            
            # Cache the result for warmup
            try:
                cache_key = _generate_cache_key(func, "warmup", *args, **kwargs)
                cache_service.set(cache_key, result, timeout)
                current_app.logger.debug(f"Warmed up cache for {func.__name__}: {cache_key}")
            except Exception as e:
                current_app.logger.error(f"Cache warmup error for {func.__name__}: {str(e)}")
            
            return result
        
        # Mark function as warmup function
        wrapper._is_warmup = True
        return wrapper
    return decorator


def cache_conditional(
    condition_func: Callable,
    timeout: Optional[int] = None,
    key_prefix: str = ""
):
    """
    Decorator to conditionally cache function results.
    
    Args:
        condition_func: Function that returns True if result should be cached
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)
            
            # Check if result should be cached
            if condition_func(result, *args, **kwargs):
                cache_service = get_cache_service()
                if cache_service:
                    try:
                        cache_key = _generate_cache_key(func, key_prefix, *args, **kwargs)
                        cache_service.set(cache_key, result, timeout)
                        current_app.logger.debug(f"Conditionally cached result for {func.__name__}: {cache_key}")
                    except Exception as e:
                        current_app.logger.error(f"Conditional cache error for {func.__name__}: {str(e)}")
            
            return result
        
        return wrapper
    return decorator


def cache_with_fallback(
    fallback_func: Callable,
    timeout: Optional[int] = None,
    key_prefix: str = ""
):
    """
    Decorator to cache function results with fallback on cache miss.
    
    Args:
        fallback_func: Function to call if cache miss
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_service = get_cache_service()
            if not cache_service:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = _generate_cache_key(func, key_prefix, *args, **kwargs)
            
            # Try to get from cache
            try:
                result = cache_service.get(cache_key)
                if result is not None:
                    current_app.logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return result
            except Exception as e:
                current_app.logger.error(f"Cache get error for {func.__name__}: {str(e)}")
            
            # Try fallback function
            try:
                result = fallback_func(*args, **kwargs)
                if result is not None:
                    # Cache the fallback result
                    try:
                        cache_service.set(cache_key, result, timeout)
                        current_app.logger.debug(f"Cached fallback result for {func.__name__}: {cache_key}")
                    except Exception as e:
                        current_app.logger.error(f"Cache set error for {func.__name__}: {str(e)}")
                    return result
            except Exception as e:
                current_app.logger.error(f"Fallback function error for {func.__name__}: {str(e)}")
            
            # Execute original function as last resort
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def _generate_cache_key(func: Callable, key_prefix: str, *args, **kwargs) -> str:
    """Generate cache key for function."""
    # Get function name
    func_name = func.__name__
    
    # Get module name
    module_name = func.__module__.split('.')[-1] if func.__module__ else 'unknown'
    
    # Create key parts
    key_parts = [key_prefix, module_name, func_name] if key_prefix else [module_name, func_name]
    
    # Add arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword arguments
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}:{value}")
        else:
            key_parts.append(f"{key}:{hash(str(value))}")
    
    # Join and create hash
    key_string = "|".join(key_parts)
    return f"{key_prefix}_{hash(key_string)}" if key_prefix else f"cache_{hash(key_string)}"


def get_cache_service() -> Optional[CacheService]:
    """Get cache service instance."""
    try:
        from extensions import cache
        cache_service = CacheService(cache)
        return cache_service if cache_service.enabled else None
    except Exception:
        return None


def clear_cache_pattern(pattern: str) -> int:
    """Clear cache keys matching pattern."""
    cache_service = get_cache_service()
    if cache_service:
        return cache_service.invalidate_pattern(pattern)
    return 0


def clear_cache_keys(keys: List[str]) -> bool:
    """Clear specific cache keys."""
    cache_service = get_cache_service()
    if cache_service:
        return cache_service.delete_many(keys)
    return False
