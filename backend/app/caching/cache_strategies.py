"""
Cache Strategies

Different caching strategies for various use cases.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime, timedelta
import threading
import time

from .cache_service import CacheService


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
    
    @abstractmethod
    def get(self, key: str, fetch_func: Callable, *args, **kwargs) -> Any:
        """Get value using strategy."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, *args, **kwargs) -> bool:
        """Set value using strategy."""
        pass
    
    @abstractmethod
    def invalidate(self, key: str) -> bool:
        """Invalidate value using strategy."""
        pass


class TTLStrategy(CacheStrategy):
    """Time-to-Live cache strategy."""
    
    def __init__(self, cache_service: CacheService, default_ttl: int = 300):
        super().__init__(cache_service)
        self.default_ttl = default_ttl
    
    def get(self, key: str, fetch_func: Callable, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """Get value with TTL."""
        # Try to get from cache
        value = self.cache_service.get(key)
        if value is not None:
            return value
        
        # Fetch from source
        value = fetch_func(*args, **kwargs)
        
        # Cache with TTL
        ttl = ttl or self.default_ttl
        self.cache_service.set(key, value, ttl)
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, *args, **kwargs) -> bool:
        """Set value with TTL."""
        ttl = ttl or self.default_ttl
        return self.cache_service.set(key, value, ttl)
    
    def invalidate(self, key: str) -> bool:
        """Invalidate value."""
        return self.cache_service.delete(key)


class LRUStrategy(CacheStrategy):
    """Least Recently Used cache strategy."""
    
    def __init__(self, cache_service: CacheService, max_size: int = 1000):
        super().__init__(cache_service)
        self.max_size = max_size
        self.access_times = {}
        self.lock = threading.Lock()
    
    def get(self, key: str, fetch_func: Callable, *args, **kwargs) -> Any:
        """Get value with LRU eviction."""
        with self.lock:
            # Update access time
            self.access_times[key] = time.time()
        
        # Try to get from cache
        value = self.cache_service.get(key)
        if value is not None:
            return value
        
        # Check if we need to evict
        self._evict_if_needed()
        
        # Fetch from source
        value = fetch_func(*args, **kwargs)
        
        # Cache the value
        self.cache_service.set(key, value)
        
        return value
    
    def set(self, key: str, value: Any, *args, **kwargs) -> bool:
        """Set value with LRU eviction."""
        with self.lock:
            # Update access time
            self.access_times[key] = time.time()
            
            # Check if we need to evict
            self._evict_if_needed()
        
        return self.cache_service.set(key, value)
    
    def invalidate(self, key: str) -> bool:
        """Invalidate value."""
        with self.lock:
            self.access_times.pop(key, None)
        return self.cache_service.delete(key)
    
    def _evict_if_needed(self):
        """Evict least recently used items if cache is full."""
        if len(self.access_times) >= self.max_size:
            # Find least recently used key
            lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            self.cache_service.delete(lru_key)
            self.access_times.pop(lru_key, None)


class WriteThroughStrategy(CacheStrategy):
    """Write-through cache strategy."""
    
    def __init__(self, cache_service: CacheService, write_func: Callable):
        super().__init__(cache_service)
        self.write_func = write_func
    
    def get(self, key: str, fetch_func: Callable, *args, **kwargs) -> Any:
        """Get value from cache."""
        return self.cache_service.get(key)
    
    def set(self, key: str, value: Any, *args, **kwargs) -> bool:
        """Set value in both cache and persistent storage."""
        # Write to persistent storage first
        try:
            self.write_func(key, value, *args, **kwargs)
        except Exception as e:
            # If write fails, don't cache
            return False
        
        # Write to cache
        return self.cache_service.set(key, value)
    
    def invalidate(self, key: str) -> bool:
        """Invalidate value."""
        return self.cache_service.delete(key)


class WriteBehindStrategy(CacheStrategy):
    """Write-behind cache strategy."""
    
    def __init__(self, cache_service: CacheService, write_func: Callable, batch_size: int = 10):
        super().__init__(cache_service)
        self.write_func = write_func
        self.batch_size = batch_size
        self.pending_writes = {}
        self.lock = threading.Lock()
    
    def get(self, key: str, fetch_func: Callable, *args, **kwargs) -> Any:
        """Get value from cache."""
        return self.cache_service.get(key)
    
    def set(self, key: str, value: Any, *args, **kwargs) -> bool:
        """Set value in cache and queue for write-behind."""
        # Set in cache immediately
        cache_success = self.cache_service.set(key, value)
        
        if cache_success:
            # Queue for write-behind
            with self.lock:
                self.pending_writes[key] = (value, args, kwargs)
                
                # Write if batch is full
                if len(self.pending_writes) >= self.batch_size:
                    self._flush_pending_writes()
        
        return cache_success
    
    def invalidate(self, key: str) -> bool:
        """Invalidate value."""
        with self.lock:
            self.pending_writes.pop(key, None)
        return self.cache_service.delete(key)
    
    def _flush_pending_writes(self):
        """Flush pending writes to persistent storage."""
        if not self.pending_writes:
            return
        
        try:
            for key, (value, args, kwargs) in self.pending_writes.items():
                self.write_func(key, value, *args, **kwargs)
        except Exception as e:
            # Log error but don't fail
            pass
        finally:
            self.pending_writes.clear()
    
    def flush(self):
        """Manually flush pending writes."""
        with self.lock:
            self._flush_pending_writes()


class CacheAsideStrategy(CacheStrategy):
    """Cache-aside strategy."""
    
    def get(self, key: str, fetch_func: Callable, *args, **kwargs) -> Any:
        """Get value using cache-aside pattern."""
        # Try to get from cache
        value = self.cache_service.get(key)
        if value is not None:
            return value
        
        # Fetch from source
        value = fetch_func(*args, **kwargs)
        
        # Cache the value
        self.cache_service.set(key, value)
        
        return value
    
    def set(self, key: str, value: Any, *args, **kwargs) -> bool:
        """Set value in cache."""
        return self.cache_service.set(key, value)
    
    def invalidate(self, key: str) -> bool:
        """Invalidate value."""
        return self.cache_service.delete(key)


class RefreshAheadStrategy(CacheStrategy):
    """Refresh-ahead cache strategy."""
    
    def __init__(self, cache_service: CacheService, refresh_threshold: float = 0.8):
        super().__init__(cache_service)
        self.refresh_threshold = refresh_threshold
        self.refresh_tasks = {}
        self.lock = threading.Lock()
    
    def get(self, key: str, fetch_func: Callable, ttl: int = 300, *args, **kwargs) -> Any:
        """Get value with refresh-ahead."""
        # Get current TTL
        current_ttl = self.cache_service.get_ttl(key)
        
        # If TTL is below threshold, refresh in background
        if current_ttl > 0 and current_ttl < (ttl * self.refresh_threshold):
            self._schedule_refresh(key, fetch_func, ttl, *args, **kwargs)
        
        # Try to get from cache
        value = self.cache_service.get(key)
        if value is not None:
            return value
        
        # Fetch from source
        value = fetch_func(*args, **kwargs)
        
        # Cache the value
        self.cache_service.set(key, value, ttl)
        
        return value
    
    def set(self, key: str, value: Any, ttl: int = 300, *args, **kwargs) -> bool:
        """Set value with TTL."""
        return self.cache_service.set(key, value, ttl)
    
    def invalidate(self, key: str) -> bool:
        """Invalidate value."""
        with self.lock:
            self.refresh_tasks.pop(key, None)
        return self.cache_service.delete(key)
    
    def _schedule_refresh(self, key: str, fetch_func: Callable, ttl: int, *args, **kwargs):
        """Schedule background refresh."""
        with self.lock:
            if key in self.refresh_tasks:
                return  # Already scheduled
        
        def refresh_task():
            try:
                # Fetch fresh data
                value = fetch_func(*args, **kwargs)
                
                # Update cache
                self.cache_service.set(key, value, ttl)
                
                # Remove from refresh tasks
                with self.lock:
                    self.refresh_tasks.pop(key, None)
            except Exception:
                # Remove from refresh tasks on error
                with self.lock:
                    self.refresh_tasks.pop(key, None)
        
        # Schedule refresh
        with self.lock:
            self.refresh_tasks[key] = True
        
        # Start refresh in background thread
        import threading
        thread = threading.Thread(target=refresh_task)
        thread.daemon = True
        thread.start()


class CacheStrategyFactory:
    """Factory for creating cache strategies."""
    
    @staticmethod
    def create_strategy(strategy_type: str, cache_service: CacheService, **kwargs) -> CacheStrategy:
        """Create cache strategy by type."""
        strategies = {
            'ttl': TTLStrategy,
            'lru': LRUStrategy,
            'write_through': WriteThroughStrategy,
            'write_behind': WriteBehindStrategy,
            'cache_aside': CacheAsideStrategy,
            'refresh_ahead': RefreshAheadStrategy
        }
        
        strategy_class = strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        return strategy_class(cache_service, **kwargs)
