"""
Cache Service

Core caching service with Redis integration and advanced features.
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Union, Dict, List, Callable
from datetime import datetime, timedelta
from flask import current_app
from flask_caching import Cache
import redis
from redis.exceptions import RedisError

from .cache_config import CacheConfig


class CacheService:
    """Advanced caching service with Redis integration."""
    
    def __init__(self, cache: Cache, redis_client: Optional[redis.Redis] = None):
        self.cache = cache
        self.redis_client = redis_client or self._get_redis_client()
        self.config = CacheConfig()
        self.enabled = self.config.CACHE_ENABLED
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def _get_redis_client(self) -> Optional[redis.Redis]:
        """Get Redis client from Flask-Caching backend."""
        try:
            if hasattr(self.cache.cache, 'redis_client'):
                return self.cache.cache.redis_client
            return None
        except Exception:
            return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        if not self.enabled:
            return default
        
        try:
            value = self.cache.get(key)
            if value is not None:
                self._stats['hits'] += 1
                return value
            else:
                self._stats['misses'] += 1
                return default
        except Exception as e:
            self._stats['errors'] += 1
            current_app.logger.error(f"Cache get error for key {key}: {str(e)}")
            return default
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.enabled:
            return True  # Return True to indicate "success" when cache is disabled
        
        try:
            timeout = timeout or self.config.DEFAULT_TIMEOUT
            self.cache.set(key, value, timeout=timeout)
            self._stats['sets'] += 1
            return True
        except Exception as e:
            self._stats['errors'] += 1
            current_app.logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled:
            return True  # Return True to indicate "success" when cache is disabled
        
        try:
            self.cache.delete(key)
            self._stats['deletes'] += 1
            return True
        except Exception as e:
            self._stats['errors'] += 1
            current_app.logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled:
            return False
        
        try:
            return self.cache.get(key) is not None
        except Exception:
            return False
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        if not self.enabled:
            return {}
        
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def set_many(self, mapping: Dict[str, Any], timeout: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        if not self.enabled:
            return True  # Return True to indicate "success" when cache is disabled
        
        try:
            timeout = timeout or self.config.DEFAULT_TIMEOUT
            for key, value in mapping.items():
                self.set(key, value, timeout)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache set_many error: {str(e)}")
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """Delete multiple values from cache."""
        if not self.enabled:
            return True  # Return True to indicate "success" when cache is disabled
        
        try:
            for key in keys:
                self.delete(key)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache delete_many error: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        if not self.enabled:
            return True  # Return True to indicate "success" when cache is disabled
        
        try:
            self.cache.clear()
            return True
        except Exception as e:
            current_app.logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def get_or_set(self, key: str, func: Callable, timeout: Optional[int] = None) -> Any:
        """Get value from cache or set it using function."""
        if not self.enabled:
            return func()  # Execute function directly when cache is disabled
        
        value = self.get(key)
        if value is not None:
            return value
        
        try:
            value = func()
            self.set(key, value, timeout)
            return value
        except Exception as e:
            current_app.logger.error(f"Cache get_or_set error for key {key}: {str(e)}")
            return func()
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(f"{self.config.KEY_PREFIX}{pattern}")
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            current_app.logger.error(f"Cache invalidate_pattern error for pattern {pattern}: {str(e)}")
            return 0
    
    def get_ttl(self, key: str) -> int:
        """Get time to live for key."""
        if not self.enabled or not self.redis_client:
            return -1
        
        try:
            return self.redis_client.ttl(f"{self.config.KEY_PREFIX}{key}")
        except Exception:
            return -1
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """Set time to live for key."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.expire(f"{self.config.KEY_PREFIX}{key}", ttl))
        except Exception:
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            return self.redis_client.incrby(f"{self.config.KEY_PREFIX}{key}", amount)
        except Exception:
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement numeric value in cache."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            return self.redis_client.decrby(f"{self.config.KEY_PREFIX}{key}", amount)
        except Exception:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes'],
            'errors': self._stats['errors'],
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def reset_stats(self):
        """Reset cache statistics."""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check cache health."""
        if not self.enabled:
            return {
                'status': 'disabled',
                'enabled': False,
                'message': 'Cache is disabled via configuration',
                'stats': self.get_stats()
            }
        
        try:
            # Test basic operations
            test_key = "health_check_test"
            test_value = "test_value"
            
            # Test set
            set_success = self.set(test_key, test_value, 10)
            
            # Test get
            get_value = self.get(test_key)
            get_success = get_value == test_value
            
            # Test delete
            delete_success = self.delete(test_key)
            
            # Test Redis connection if available
            redis_connected = True
            if self.redis_client:
                try:
                    self.redis_client.ping()
                except Exception:
                    redis_connected = False
            
            return {
                'status': 'healthy' if all([set_success, get_success, delete_success]) else 'unhealthy',
                'enabled': True,
                'set_operation': set_success,
                'get_operation': get_success,
                'delete_operation': delete_success,
                'redis_connected': redis_connected,
                'stats': self.get_stats()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'enabled': True,
                'error': str(e),
                'stats': self.get_stats()
            }
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_parts = []
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))
        
        # Add keyword arguments
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (str, int, float, bool)):
                key_parts.append(f"{key}:{value}")
            elif isinstance(value, (dict, list)):
                key_parts.append(f"{key}:{json.dumps(value, sort_keys=True)}")
            else:
                key_parts.append(f"{key}:{str(value)}")
        
        # Create hash of key parts
        key_string = "|".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{self.config.KEY_PREFIX}{key_hash}"
    
    def warmup(self, warmup_funcs: List[Callable]) -> Dict[str, Any]:
        """Warm up cache with provided functions."""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for func in warmup_funcs:
            try:
                func()
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                current_app.logger.error(f"Cache warmup error: {str(e)}")
        
        return results
