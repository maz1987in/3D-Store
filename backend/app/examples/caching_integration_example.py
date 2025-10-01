"""
Caching Integration Examples

This file demonstrates how to integrate the new caching system with existing services.
"""

from flask import current_app
from app.caching import (
    CacheService, 
    cache_result, 
    cache_invalidate, 
    UserCacheManager,
    ProductCacheManager,
    OrderCacheManager
)
from app.caching.extension import CacheExtension


def example_user_service_integration():
    """Example of integrating caching with user service."""
    
    class CachedUserService:
        """Example user service with caching integration."""
        
        def __init__(self):
            # Get cache extension
            cache_ext = current_app.extensions.get('cache_extension')
            if cache_ext:
                self.cache_service = cache_ext.get_cache_service()
                self.user_cache = cache_ext.get_manager('user')
            else:
                self.cache_service = None
                self.user_cache = None
        
        @cache_result(timeout=3600, key_prefix="user")
        def get_user_by_id(self, user_id: str):
            """Get user by ID with caching."""
            # This would call your actual user service
            # from app.users.service import UserService
            # user_service = UserService()
            # return user_service.get_user_by_id(user_id)
            
            # Example implementation
            return {
                'id': user_id,
                'name': 'John Doe',
                'email': 'john@example.com',
                'roles': ['user']
            }
        
        @cache_result(timeout=1800, key_prefix="user_roles")
        def get_user_roles(self, user_id: str):
            """Get user roles with caching."""
            # This would call your actual user service
            return ['user', 'customer']
        
        @cache_invalidate(pattern="user|*")
        def update_user(self, user_id: str, user_data: dict):
            """Update user and invalidate cache."""
            # Update user in database
            # Then cache will be automatically invalidated
            return {'success': True, 'user_id': user_id}
        
        def get_user_with_cache_manager(self, user_id: str):
            """Example using cache manager."""
            if not self.user_cache:
                # Fallback to direct database call
                return self.get_user_by_id(user_id)
            
            def fetch_user():
                # This would be your actual database call
                return {
                    'id': user_id,
                    'name': 'John Doe',
                    'email': 'john@example.com'
                }
            
            return self.user_cache.get_user(user_id, fetch_user)


def example_product_service_integration():
    """Example of integrating caching with product service."""
    
    class CachedProductService:
        """Example product service with caching integration."""
        
        def __init__(self):
            cache_ext = current_app.extensions.get('cache_extension')
            if cache_ext:
                self.product_cache = cache_ext.get_manager('product')
            else:
                self.product_cache = None
        
        @cache_result(timeout=1800, key_prefix="product")
        def get_product(self, product_id: str):
            """Get product with caching."""
            return {
                'id': product_id,
                'name': '3D Printed Model',
                'price': 25.99,
                'category': 'toys'
            }
        
        @cache_result(timeout=900, key_prefix="products_by_category")
        def get_products_by_category(self, category_id: str, limit: int = 20, offset: int = 0):
            """Get products by category with caching."""
            return [
                {'id': f'product_{i}', 'name': f'Product {i}', 'category_id': category_id}
                for i in range(offset, offset + limit)
            ]
        
        @cache_invalidate(pattern="product|*")
        def update_product(self, product_id: str, product_data: dict):
            """Update product and invalidate cache."""
            # Update product in database
            return {'success': True, 'product_id': product_id}
        
        def search_products_with_cache(self, query: str, filters: dict = None):
            """Search products with caching."""
            if not self.product_cache:
                return self._search_products_direct(query, filters)
            
            def fetch_search_results():
                return self._search_products_direct(query, filters)
            
            return self.product_cache.get_products_search(query, filters or {}, fetch_search_results)
        
        def _search_products_direct(self, query: str, filters: dict):
            """Direct search without cache."""
            # This would be your actual search implementation
            return [
                {'id': f'product_{i}', 'name': f'Product {i}', 'query': query}
                for i in range(5)
            ]


def example_order_service_integration():
    """Example of integrating caching with order service."""
    
    class CachedOrderService:
        """Example order service with caching integration."""
        
        def __init__(self):
            cache_ext = current_app.extensions.get('cache_extension')
            if cache_ext:
                self.order_cache = cache_ext.get_manager('order')
            else:
                self.order_cache = None
        
        @cache_result(timeout=900, key_prefix="order")
        def get_order(self, order_id: str):
            """Get order with caching."""
            return {
                'id': order_id,
                'user_id': 'user_123',
                'status': 'pending',
                'total': 99.99,
                'items': []
            }
        
        @cache_result(timeout=600, key_prefix="user_orders")
        def get_user_orders(self, user_id: str, limit: int = 20, offset: int = 0):
            """Get user orders with caching."""
            return [
                {'id': f'order_{i}', 'user_id': user_id, 'status': 'completed'}
                for i in range(offset, offset + limit)
            ]
        
        @cache_invalidate(pattern="order|*")
        def update_order_status(self, order_id: str, status: str):
            """Update order status and invalidate cache."""
            # Update order in database
            return {'success': True, 'order_id': order_id, 'status': status}


def example_cache_management():
    """Example of cache management operations."""
    
    def get_cache_stats():
        """Get cache statistics."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return {'error': 'Cache extension not available'}
        
        return cache_ext.get_stats()
    
    def clear_user_cache():
        """Clear user cache."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return False
        
        return cache_ext.clear_entity('user')
    
    def warmup_cache():
        """Warm up cache."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return {'error': 'Cache extension not available'}
        
        return cache_ext.warmup()
    
    def get_cache_health():
        """Get cache health status."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return {'status': 'unhealthy', 'message': 'Cache extension not available'}
        
        return cache_ext.health_check()


def example_advanced_caching():
    """Example of advanced caching patterns."""
    
    from app.caching.cache_decorators import cache_conditional, cache_with_fallback
    
    class AdvancedCachedService:
        """Example service with advanced caching patterns."""
        
        def __init__(self):
            cache_ext = current_app.extensions.get('cache_extension')
            self.cache_service = cache_ext.get_cache_service() if cache_ext else None
        
        @cache_conditional(
            condition_func=lambda result, *args, **kwargs: result.get('status') == 'active',
            timeout=3600
        )
        def get_active_users(self, limit: int = 100):
            """Only cache active users."""
            # This would fetch users from database
            users = [
                {'id': f'user_{i}', 'status': 'active' if i % 2 == 0 else 'inactive'}
                for i in range(limit)
            ]
            return users
        
        @cache_with_fallback(
            fallback_func=lambda user_id: {'id': user_id, 'name': 'Unknown User'},
            timeout=1800
        )
        def get_user_with_fallback(self, user_id: str):
            """Get user with fallback on cache miss."""
            # This would try to fetch from database
            # If not found, fallback function will be called
            return None  # Simulate user not found
        
        def get_user_with_custom_key(self, user_id: str, include_roles: bool = False):
            """Get user with custom cache key generation."""
            if not self.cache_service:
                return self._fetch_user_direct(user_id, include_roles)
            
            # Custom key generation
            key = f"user:{user_id}:roles:{include_roles}"
            
            # Try to get from cache
            cached_user = self.cache_service.get(key)
            if cached_user:
                return cached_user
            
            # Fetch from database
            user = self._fetch_user_direct(user_id, include_roles)
            
            # Cache the result
            self.cache_service.set(key, user, 1800)
            
            return user
        
        def _fetch_user_direct(self, user_id: str, include_roles: bool):
            """Direct database fetch."""
            user = {'id': user_id, 'name': 'John Doe'}
            if include_roles:
                user['roles'] = ['user', 'customer']
            return user


def example_cache_warmup():
    """Example of cache warmup operations."""
    
    def warmup_frequently_accessed_data():
        """Warm up frequently accessed data."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return {'error': 'Cache extension not available'}
        
        # Get cache service
        cache_service = cache_ext.get_cache_service()
        if not cache_service:
            return {'error': 'Cache service not available'}
        
        # Warm up data
        warmup_data = {
            'popular_products': [
                {'id': f'product_{i}', 'name': f'Popular Product {i}'}
                for i in range(10)
            ],
            'active_categories': [
                {'id': f'category_{i}', 'name': f'Category {i}'}
                for i in range(5)
            ],
            'recent_orders': [
                {'id': f'order_{i}', 'status': 'completed'}
                for i in range(20)
            ]
        }
        
        # Cache the data
        for key, data in warmup_data.items():
            cache_service.set(f"warmup:{key}", data, 3600)
        
        return {'warmed': len(warmup_data), 'message': 'Cache warmed up successfully'}


def example_cache_monitoring():
    """Example of cache monitoring operations."""
    
    def monitor_cache_performance():
        """Monitor cache performance."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return {'error': 'Cache extension not available'}
        
        stats = cache_ext.get_stats()
        
        # Calculate performance metrics
        total_requests = stats['cache_service']['hits'] + stats['cache_service']['misses']
        hit_rate = stats['cache_service']['hit_rate']
        
        performance = {
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'cache_efficiency': 'excellent' if hit_rate > 80 else 'good' if hit_rate > 60 else 'needs_improvement',
            'recommendations': []
        }
        
        # Add recommendations based on performance
        if hit_rate < 60:
            performance['recommendations'].append('Consider increasing cache TTL for frequently accessed data')
        if hit_rate > 90:
            performance['recommendations'].append('Cache is performing well')
        
        return performance
    
    def get_cache_usage_by_entity():
        """Get cache usage by entity type."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return {'error': 'Cache extension not available'}
        
        usage = {}
        for entity_type, manager in cache_ext.managers.items():
            stats = manager.get_stats()
            usage[entity_type] = {
                'hits': stats['cache_stats']['hits'],
                'misses': stats['cache_stats']['misses'],
                'hit_rate': stats['cache_stats']['hit_rate']
            }
        
        return usage


# Example usage in Flask routes
def example_flask_routes():
    """Example Flask routes using caching."""
    
    from flask import Blueprint, jsonify, request
    
    cache_bp = Blueprint('cache_examples', __name__)
    
    @cache_bp.route('/user/<user_id>')
    def get_user_route(user_id):
        """Get user route with caching."""
        service = CachedUserService()
        user = service.get_user_by_id(user_id)
        return jsonify(user)
    
    @cache_bp.route('/products')
    def get_products_route():
        """Get products route with caching."""
        service = CachedProductService()
        category_id = request.args.get('category_id')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        if category_id:
            products = service.get_products_by_category(category_id, limit, offset)
        else:
            products = service.search_products_with_cache('', {})
        
        return jsonify(products)
    
    @cache_bp.route('/cache/stats')
    def cache_stats_route():
        """Cache statistics route."""
        stats = get_cache_stats()
        return jsonify(stats)
    
    @cache_bp.route('/cache/clear', methods=['POST'])
    def clear_cache_route():
        """Clear cache route."""
        cache_ext = current_app.extensions.get('cache_extension')
        if not cache_ext:
            return jsonify({'error': 'Cache extension not available'}), 503
        
        success = cache_ext.clear_all()
        return jsonify({'success': success})
    
    return cache_bp


if __name__ == '__main__':
    print("Caching Integration Examples")
    print("=" * 50)
    
    # These examples show how to integrate the caching system
    # with existing services in the 3D Store application
    
    print("\n1. User Service Integration:")
    print("- Use @cache_result decorator for automatic caching")
    print("- Use UserCacheManager for advanced cache operations")
    print("- Use @cache_invalidate for cache invalidation")
    
    print("\n2. Product Service Integration:")
    print("- Cache product data with appropriate TTL")
    print("- Cache search results and category-based queries")
    print("- Invalidate cache when products are updated")
    
    print("\n3. Order Service Integration:")
    print("- Cache order data with shorter TTL (more dynamic)")
    print("- Cache user-specific order lists")
    print("- Invalidate cache when order status changes")
    
    print("\n4. Cache Management:")
    print("- Monitor cache performance and hit rates")
    print("- Clear cache when needed")
    print("- Warm up cache with frequently accessed data")
    
    print("\n5. Advanced Patterns:")
    print("- Conditional caching based on data characteristics")
    print("- Fallback caching for graceful degradation")
    print("- Custom key generation for complex scenarios")
    
    print("\nIntegration completed!")
