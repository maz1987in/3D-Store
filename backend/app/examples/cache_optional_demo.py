"""
Cache Optional Demo

This script demonstrates how the caching system behaves when enabled or disabled.
"""

import os
from flask import Flask
from app.caching import CacheService, cache_result, cache_invalidate
from app.caching.extension import CacheExtension


def create_test_app(cache_enabled=True):
    """Create a test Flask app with cache enabled or disabled."""
    app = Flask(__name__)
    
    # Set cache configuration
    os.environ['CACHE_ENABLED'] = str(cache_enabled)
    os.environ['CACHE_TYPE'] = 'SimpleCache'
    os.environ['CACHE_DEFAULT_TIMEOUT'] = '300'
    os.environ['CACHE_KEY_PREFIX'] = 'test_'
    
    # Initialize cache extension
    cache_ext = CacheExtension()
    cache_ext.init_app(app)
    
    return app, cache_ext


def test_cache_behavior():
    """Test cache behavior when enabled vs disabled."""
    
    print("=" * 60)
    print("CACHE OPTIONAL DEMONSTRATION")
    print("=" * 60)
    
    # Test with cache ENABLED
    print("\n1. Testing with CACHE_ENABLED=True")
    print("-" * 40)
    
    app_enabled, cache_ext_enabled = create_test_app(cache_enabled=True)
    
    with app_enabled.app_context():
        cache_service = cache_ext_enabled.get_cache_service()
        
        if cache_service:
            print(f"✓ Cache service initialized: {cache_service.enabled}")
            
            # Test basic operations
            cache_service.set('test_key', 'test_value', 60)
            value = cache_service.get('test_key')
            print(f"✓ Set/Get test: {value}")
            
            # Test health check
            health = cache_service.health_check()
            print(f"✓ Health check: {health['status']}")
        else:
            print("✗ Cache service not available")
    
    # Test with cache DISABLED
    print("\n2. Testing with CACHE_ENABLED=False")
    print("-" * 40)
    
    app_disabled, cache_ext_disabled = create_test_app(cache_enabled=False)
    
    with app_disabled.app_context():
        cache_service = cache_ext_disabled.get_cache_service()
        
        if cache_service:
            print(f"✓ Cache service initialized: {cache_service.enabled}")
            
            # Test basic operations (should return defaults)
            cache_service.set('test_key', 'test_value', 60)
            value = cache_service.get('test_key')
            print(f"✓ Set/Get test: {value} (should be None when disabled)")
            
            # Test health check
            health = cache_service.health_check()
            print(f"✓ Health check: {health['status']}")
        else:
            print("✓ Cache service not initialized (disabled)")
    
    # Test decorators
    print("\n3. Testing Cache Decorators")
    print("-" * 40)
    
    call_count = 0
    
    def expensive_operation():
        nonlocal call_count
        call_count += 1
        return f"Expensive result {call_count}"
    
    # Test with cache enabled
    print("\nWith cache ENABLED:")
    os.environ['CACHE_ENABLED'] = 'True'
    
    @cache_result(timeout=60, key_prefix="test")
    def cached_function_enabled():
        return expensive_operation()
    
    call_count = 0
    result1 = cached_function_enabled()
    result2 = cached_function_enabled()
    print(f"  First call: {result1}")
    print(f"  Second call: {result2}")
    print(f"  Function called {call_count} times (should be 1 with cache)")
    
    # Test with cache disabled
    print("\nWith cache DISABLED:")
    os.environ['CACHE_ENABLED'] = 'False'
    
    @cache_result(timeout=60, key_prefix="test")
    def cached_function_disabled():
        return expensive_operation()
    
    call_count = 0
    result1 = cached_function_disabled()
    result2 = cached_function_disabled()
    print(f"  First call: {result1}")
    print(f"  Second call: {result2}")
    print(f"  Function called {call_count} times (should be 2 without cache)")


def test_endpoints():
    """Test cache management endpoints."""
    
    print("\n4. Testing Cache Management Endpoints")
    print("-" * 50)
    
    # Test with cache enabled
    print("\nWith cache ENABLED:")
    app_enabled, cache_ext_enabled = create_test_app(cache_enabled=True)
    
    with app_enabled.test_client() as client:
        # Health check
        response = client.get('/cache/health')
        print(f"  Health check: {response.status_code} - {response.json}")
        
        # Metrics
        response = client.get('/cache/metrics')
        print(f"  Metrics: {response.status_code} - enabled: {response.json.get('enabled', 'N/A')}")
        
        # Clear cache
        response = client.post('/cache/clear')
        print(f"  Clear cache: {response.status_code} - {response.json}")
    
    # Test with cache disabled
    print("\nWith cache DISABLED:")
    app_disabled, cache_ext_disabled = create_test_app(cache_enabled=False)
    
    with app_disabled.test_client() as client:
        # Health check
        response = client.get('/cache/health')
        print(f"  Health check: {response.status_code} - {response.json}")
        
        # Metrics
        response = client.get('/cache/metrics')
        print(f"  Metrics: {response.status_code} - enabled: {response.json.get('enabled', 'N/A')}")
        
        # Clear cache
        response = client.post('/cache/clear')
        print(f"  Clear cache: {response.status_code} - {response.json}")


def test_configuration():
    """Test configuration options."""
    
    print("\n5. Testing Configuration Options")
    print("-" * 40)
    
    from app.caching.cache_config import CacheConfig
    
    # Test with cache enabled
    os.environ['CACHE_ENABLED'] = 'True'
    config_enabled = CacheConfig()
    print(f"Cache enabled: {config_enabled.CACHE_ENABLED}")
    print(f"Feature flags: {config_enabled.get_feature_flags()}")
    
    # Test with cache disabled
    os.environ['CACHE_ENABLED'] = 'False'
    config_disabled = CacheConfig()
    print(f"Cache enabled: {config_disabled.CACHE_ENABLED}")
    print(f"Feature flags: {config_disabled.get_feature_flags()}")


def demonstrate_graceful_degradation():
    """Demonstrate graceful degradation when cache is disabled."""
    
    print("\n6. Demonstrating Graceful Degradation")
    print("-" * 45)
    
    # Simulate a service that uses caching
    class UserService:
        def __init__(self):
            self.call_count = 0
        
        @cache_result(timeout=3600, key_prefix="user")
        def get_user(self, user_id):
            self.call_count += 1
            print(f"  Database query executed for user {user_id} (call #{self.call_count})")
            return {
                'id': user_id,
                'name': f'User {user_id}',
                'email': f'user{user_id}@example.com'
            }
        
        @cache_invalidate(pattern="user|*")
        def update_user(self, user_id, user_data):
            print(f"  User {user_id} updated in database")
            return {'success': True, 'user_id': user_id}
    
    # Test with cache enabled
    print("\nWith cache ENABLED:")
    os.environ['CACHE_ENABLED'] = 'True'
    
    user_service_enabled = UserService()
    user1 = user_service_enabled.get_user('123')
    user2 = user_service_enabled.get_user('123')  # Should use cache
    print(f"  User data: {user1}")
    print(f"  Call count: {user_service_enabled.call_count}")
    
    # Test with cache disabled
    print("\nWith cache DISABLED:")
    os.environ['CACHE_ENABLED'] = 'False'
    
    user_service_disabled = UserService()
    user1 = user_service_disabled.get_user('456')
    user2 = user_service_disabled.get_user('456')  # Should call database again
    print(f"  User data: {user1}")
    print(f"  Call count: {user_service_disabled.call_count}")


if __name__ == '__main__':
    print("Starting Cache Optional Demo...")
    
    try:
        test_cache_behavior()
        test_endpoints()
        test_configuration()
        demonstrate_graceful_degradation()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nKey Points:")
        print("1. Set CACHE_ENABLED=False to disable caching")
        print("2. When disabled, all cache operations are bypassed")
        print("3. Functions execute directly without caching")
        print("4. Health checks return 'disabled' status")
        print("5. Management endpoints return appropriate messages")
        print("6. No Redis connection required when disabled")
        
    except Exception as e:
        print(f"\nDemo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
