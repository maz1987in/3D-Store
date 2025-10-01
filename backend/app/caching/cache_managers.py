"""
Cache Managers

Specialized cache managers for different business entities.
"""

from typing import Any, Optional, List, Dict, Callable
from datetime import datetime, timedelta

from .cache_service import CacheService
from .cache_strategies import TTLStrategy, CacheStrategy
from .cache_config import CacheConfig


class BaseCacheManager:
    """Base cache manager for common functionality."""
    
    def __init__(self, cache_service: CacheService, entity_name: str):
        self.cache_service = cache_service
        self.entity_name = entity_name
        self.config = CacheConfig()
        self.key_prefix = f"{self.config.KEY_PREFIX}{entity_name}"
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key for entity."""
        key_parts = [self.key_prefix]
        
        # Add arguments
        for arg in args:
            key_parts.append(str(arg))
        
        # Add keyword arguments
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        return "|".join(key_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics for this entity."""
        return {
            'entity': self.entity_name,
            'key_prefix': self.key_prefix,
            'cache_stats': self.cache_service.get_stats()
        }


class UserCacheManager(BaseCacheManager):
    """Cache manager for user-related data."""
    
    def __init__(self, cache_service: CacheService):
        super().__init__(cache_service, "user")
        self.strategy = TTLStrategy(cache_service, default_ttl=3600)  # 1 hour
    
    def get_user(self, user_id: str, fetch_func: Callable) -> Any:
        """Get user data from cache."""
        key = self._generate_key("user", user_id)
        return self.strategy.get(key, fetch_func)
    
    def set_user(self, user_id: str, user_data: Any, ttl: Optional[int] = None) -> bool:
        """Set user data in cache."""
        key = self._generate_key("user", user_id)
        return self.strategy.set(key, user_data, ttl)
    
    def get_user_roles(self, user_id: str, fetch_func: Callable) -> Any:
        """Get user roles from cache."""
        key = self._generate_key("user_roles", user_id)
        return self.strategy.get(key, fetch_func)
    
    def set_user_roles(self, user_id: str, roles: Any, ttl: Optional[int] = None) -> bool:
        """Set user roles in cache."""
        key = self._generate_key("user_roles", user_id)
        return self.strategy.set(key, roles, ttl)
    
    def get_user_permissions(self, user_id: str, fetch_func: Callable) -> Any:
        """Get user permissions from cache."""
        key = self._generate_key("user_permissions", user_id)
        return self.strategy.get(key, fetch_func)
    
    def set_user_permissions(self, user_id: str, permissions: Any, ttl: Optional[int] = None) -> bool:
        """Set user permissions in cache."""
        key = self._generate_key("user_permissions", user_id)
        return self.strategy.set(key, permissions, ttl)
    
    def invalidate_user(self, user_id: str) -> bool:
        """Invalidate all user-related cache."""
        patterns = [
            f"user|{user_id}",
            f"user_roles|{user_id}",
            f"user_permissions|{user_id}"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.cache_service.invalidate_pattern(pattern)
        
        return total_invalidated > 0
    
    def invalidate_all_users(self) -> int:
        """Invalidate all user cache."""
        return self.cache_service.invalidate_pattern("user*")


class ProductCacheManager(BaseCacheManager):
    """Cache manager for product-related data."""
    
    def __init__(self, cache_service: CacheService):
        super().__init__(cache_service, "product")
        self.strategy = TTLStrategy(cache_service, default_ttl=1800)  # 30 minutes
    
    def get_product(self, product_id: str, fetch_func: Callable) -> Any:
        """Get product data from cache."""
        key = self._generate_key("product", product_id)
        return self.strategy.get(key, fetch_func)
    
    def set_product(self, product_id: str, product_data: Any, ttl: Optional[int] = None) -> bool:
        """Set product data in cache."""
        key = self._generate_key("product", product_id)
        return self.strategy.set(key, product_data, ttl)
    
    def get_products_by_category(self, category_id: str, fetch_func: Callable) -> Any:
        """Get products by category from cache."""
        key = self._generate_key("products_by_category", category_id)
        return self.strategy.get(key, fetch_func)
    
    def set_products_by_category(self, category_id: str, products: Any, ttl: Optional[int] = None) -> bool:
        """Set products by category in cache."""
        key = self._generate_key("products_by_category", category_id)
        return self.strategy.set(key, products, ttl)
    
    def get_products_search(self, query: str, filters: Dict, fetch_func: Callable) -> Any:
        """Get product search results from cache."""
        key = self._generate_key("products_search", query, **filters)
        return self.strategy.get(key, fetch_func)
    
    def set_products_search(self, query: str, filters: Dict, results: Any, ttl: Optional[int] = None) -> bool:
        """Set product search results in cache."""
        key = self._generate_key("products_search", query, **filters)
        return self.strategy.set(key, results, ttl)
    
    def invalidate_product(self, product_id: str) -> bool:
        """Invalidate product-related cache."""
        patterns = [
            f"product|{product_id}",
            f"products_by_category*",
            f"products_search*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.cache_service.invalidate_pattern(pattern)
        
        return total_invalidated > 0
    
    def invalidate_category(self, category_id: str) -> bool:
        """Invalidate category-related cache."""
        patterns = [
            f"products_by_category|{category_id}",
            f"products_search*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.cache_service.invalidate_pattern(pattern)
        
        return total_invalidated > 0


class OrderCacheManager(BaseCacheManager):
    """Cache manager for order-related data."""
    
    def __init__(self, cache_service: CacheService):
        super().__init__(cache_service, "order")
        self.strategy = TTLStrategy(cache_service, default_ttl=900)  # 15 minutes
    
    def get_order(self, order_id: str, fetch_func: Callable) -> Any:
        """Get order data from cache."""
        key = self._generate_key("order", order_id)
        return self.strategy.get(key, fetch_func)
    
    def set_order(self, order_id: str, order_data: Any, ttl: Optional[int] = None) -> bool:
        """Set order data in cache."""
        key = self._generate_key("order", order_id)
        return self.strategy.set(key, order_data, ttl)
    
    def get_user_orders(self, user_id: str, fetch_func: Callable) -> Any:
        """Get user orders from cache."""
        key = self._generate_key("user_orders", user_id)
        return self.strategy.get(key, fetch_func)
    
    def set_user_orders(self, user_id: str, orders: Any, ttl: Optional[int] = None) -> bool:
        """Set user orders in cache."""
        key = self._generate_key("user_orders", user_id)
        return self.strategy.set(key, orders, ttl)
    
    def get_order_status(self, order_id: str, fetch_func: Callable) -> Any:
        """Get order status from cache."""
        key = self._generate_key("order_status", order_id)
        return self.strategy.get(key, fetch_func)
    
    def set_order_status(self, order_id: str, status: Any, ttl: Optional[int] = None) -> bool:
        """Set order status in cache."""
        key = self._generate_key("order_status", order_id)
        return self.strategy.set(key, status, ttl)
    
    def invalidate_order(self, order_id: str) -> bool:
        """Invalidate order-related cache."""
        patterns = [
            f"order|{order_id}",
            f"order_status|{order_id}"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.cache_service.invalidate_pattern(pattern)
        
        return total_invalidated > 0
    
    def invalidate_user_orders(self, user_id: str) -> bool:
        """Invalidate user orders cache."""
        key = self._generate_key("user_orders", user_id)
        return self.cache_service.delete(key)


class InventoryCacheManager(BaseCacheManager):
    """Cache manager for inventory-related data."""
    
    def __init__(self, cache_service: CacheService):
        super().__init__(cache_service, "inventory")
        self.strategy = TTLStrategy(cache_service, default_ttl=600)  # 10 minutes
    
    def get_inventory(self, product_id: str, branch_id: str, fetch_func: Callable) -> Any:
        """Get inventory data from cache."""
        key = self._generate_key("inventory", product_id, branch_id)
        return self.strategy.get(key, fetch_func)
    
    def set_inventory(self, product_id: str, branch_id: str, inventory_data: Any, ttl: Optional[int] = None) -> bool:
        """Set inventory data in cache."""
        key = self._generate_key("inventory", product_id, branch_id)
        return self.strategy.set(key, inventory_data, ttl)
    
    def get_branch_inventory(self, branch_id: str, fetch_func: Callable) -> Any:
        """Get branch inventory from cache."""
        key = self._generate_key("branch_inventory", branch_id)
        return self.strategy.get(key, fetch_func)
    
    def set_branch_inventory(self, branch_id: str, inventory: Any, ttl: Optional[int] = None) -> bool:
        """Set branch inventory in cache."""
        key = self._generate_key("branch_inventory", branch_id)
        return self.strategy.set(key, inventory, ttl)
    
    def invalidate_product_inventory(self, product_id: str) -> bool:
        """Invalidate product inventory cache."""
        patterns = [
            f"inventory|{product_id}*",
            f"branch_inventory*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.cache_service.invalidate_pattern(pattern)
        
        return total_invalidated > 0
    
    def invalidate_branch_inventory(self, branch_id: str) -> bool:
        """Invalidate branch inventory cache."""
        patterns = [
            f"inventory|*|{branch_id}",
            f"branch_inventory|{branch_id}"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += self.cache_service.invalidate_pattern(pattern)
        
        return total_invalidated > 0


class FinancialCacheManager(BaseCacheManager):
    """Cache manager for financial data."""
    
    def __init__(self, cache_service: CacheService):
        super().__init__(cache_service, "financial")
        self.strategy = TTLStrategy(cache_service, default_ttl=1800)  # 30 minutes
    
    def get_financial_report(self, report_type: str, period: str, fetch_func: Callable) -> Any:
        """Get financial report from cache."""
        key = self._generate_key("financial_report", report_type, period)
        return self.strategy.get(key, fetch_func)
    
    def set_financial_report(self, report_type: str, period: str, report_data: Any, ttl: Optional[int] = None) -> bool:
        """Set financial report in cache."""
        key = self._generate_key("financial_report", report_type, period)
        return self.strategy.set(key, report_data, ttl)
    
    def get_dashboard_stats(self, user_id: str, fetch_func: Callable) -> Any:
        """Get dashboard statistics from cache."""
        key = self._generate_key("dashboard_stats", user_id)
        return self.strategy.get(key, fetch_func)
    
    def set_dashboard_stats(self, user_id: str, stats: Any, ttl: Optional[int] = None) -> bool:
        """Set dashboard statistics in cache."""
        key = self._generate_key("dashboard_stats", user_id)
        return self.strategy.set(key, stats, ttl)
    
    def invalidate_financial_data(self) -> int:
        """Invalidate all financial data cache."""
        return self.cache_service.invalidate_pattern("financial*")


class CacheManagerFactory:
    """Factory for creating cache managers."""
    
    @staticmethod
    def create_manager(entity_type: str, cache_service: CacheService) -> BaseCacheManager:
        """Create cache manager by entity type."""
        managers = {
            'user': UserCacheManager,
            'product': ProductCacheManager,
            'order': OrderCacheManager,
            'inventory': InventoryCacheManager,
            'financial': FinancialCacheManager
        }
        
        manager_class = managers.get(entity_type)
        if not manager_class:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        return manager_class(cache_service)
