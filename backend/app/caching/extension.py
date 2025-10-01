"""
Cache Extension

Flask extension for the comprehensive caching system.
"""

from typing import Optional, Dict, Any, List
from flask import Flask, current_app

from .cache_service import CacheService
from .cache_managers import (
    UserCacheManager,
    ProductCacheManager, 
    OrderCacheManager,
    InventoryCacheManager,
    FinancialCacheManager,
    CacheManagerFactory
)
from .cache_config import CacheConfig
from .warmup import warmup_all_cache, schedule_cache_warmup


class CacheExtension:
    """Flask extension for comprehensive caching system."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.cache_service = None
        self.managers = {}
        self.config = CacheConfig()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the cache extension with Flask app."""
        self.app = app
        
        # Check if cache is enabled
        if not self.config.CACHE_ENABLED:
            app.logger.info('Cache system is disabled via configuration')
            return
        
        # Initialize cache service
        self._init_cache_service()
        
        # Initialize cache managers
        self._init_cache_managers()
        
        # Register health check endpoint
        self._register_health_endpoint()
        
        # Register metrics endpoint
        self._register_metrics_endpoint()
        
        # Register cache management endpoints
        self._register_management_endpoints()
        
        # Schedule warmup if enabled
        if self.config.ENABLE_WARMUP:
            schedule_cache_warmup()
    
    def _init_cache_service(self):
        """Initialize cache service."""
        try:
            from extensions import cache
            self.cache_service = CacheService(cache)
            current_app.logger.info('Cache service initialized')
        except Exception as e:
            current_app.logger.error(f'Failed to initialize cache service: {str(e)}')
            self.cache_service = None
    
    def _init_cache_managers(self):
        """Initialize cache managers."""
        if not self.cache_service:
            return
        
        try:
            self.managers = {
                'user': UserCacheManager(self.cache_service),
                'product': ProductCacheManager(self.cache_service),
                'order': OrderCacheManager(self.cache_service),
                'inventory': InventoryCacheManager(self.cache_service),
                'financial': FinancialCacheManager(self.cache_service)
            }
            current_app.logger.info('Cache managers initialized')
        except Exception as e:
            current_app.logger.error(f'Failed to initialize cache managers: {str(e)}')
    
    def _register_health_endpoint(self):
        """Register cache health check endpoint."""
        @self.app.route('/cache/health')
        def cache_health():
            """Cache health check endpoint."""
            if not self.config.CACHE_ENABLED:
                return {
                    'status': 'disabled',
                    'enabled': False,
                    'message': 'Cache system is disabled via configuration'
                }, 200
            
            if not self.cache_service:
                return {'status': 'unhealthy', 'message': 'Cache service not available'}, 503
            
            health_status = self.cache_service.health_check()
            status_code = 200 if health_status['status'] in ['healthy', 'disabled'] else 503
            
            return health_status, status_code
    
    def _register_metrics_endpoint(self):
        """Register cache metrics endpoint."""
        @self.app.route('/cache/metrics')
        def cache_metrics():
            """Cache metrics endpoint."""
            if not self.config.CACHE_ENABLED:
                return {
                    'enabled': False,
                    'message': 'Cache system is disabled via configuration',
                    'stats': {
                        'hits': 0,
                        'misses': 0,
                        'sets': 0,
                        'deletes': 0,
                        'errors': 0,
                        'hit_rate': 0,
                        'total_requests': 0
                    }
                }, 200
            
            if not self.cache_service:
                return {'error': 'Cache service not available'}, 503
            
            metrics = {
                'enabled': True,
                'cache_service': self.cache_service.get_stats(),
                'managers': {}
            }
            
            # Add manager-specific metrics
            for name, manager in self.managers.items():
                metrics['managers'][name] = manager.get_stats()
            
            return metrics, 200
    
    def _register_management_endpoints(self):
        """Register cache management endpoints."""
        @self.app.route('/cache/clear', methods=['POST'])
        def clear_cache():
            """Clear all cache."""
            if not self.config.CACHE_ENABLED:
                return {
                    'success': True,
                    'message': 'Cache system is disabled - no cache to clear'
                }, 200
            
            if not self.cache_service:
                return {'error': 'Cache service not available'}, 503
            
            try:
                success = self.cache_service.clear()
                return {'success': success, 'message': 'Cache cleared'}, 200
            except Exception as e:
                return {'error': str(e)}, 500
        
        @self.app.route('/cache/clear/<entity_type>', methods=['POST'])
        def clear_entity_cache(entity_type: str):
            """Clear cache for specific entity type."""
            if not self.config.CACHE_ENABLED:
                return {
                    'success': True,
                    'message': f'Cache system is disabled - no {entity_type} cache to clear'
                }, 200
            
            if not self.cache_service:
                return {'error': 'Cache service not available'}, 503
            
            if entity_type not in self.managers:
                return {'error': f'Unknown entity type: {entity_type}'}, 400
            
            try:
                manager = self.managers[entity_type]
                if hasattr(manager, 'invalidate_all'):
                    success = manager.invalidate_all()
                else:
                    # Use pattern-based invalidation
                    patterns = self.config.get_invalidation_patterns(entity_type)
                    success = all(
                        self.cache_service.invalidate_pattern(pattern) >= 0
                        for pattern in patterns
                    )
                
                return {'success': success, 'message': f'{entity_type} cache cleared'}, 200
            except Exception as e:
                return {'error': str(e)}, 500
        
        @self.app.route('/cache/warmup', methods=['POST'])
        def warmup_cache():
            """Warm up cache."""
            if not self.config.CACHE_ENABLED:
                return {
                    'success': True,
                    'message': 'Cache system is disabled - no cache to warm up',
                    'warmed': 0,
                    'failed': 0,
                    'errors': []
                }, 200
            
            try:
                results = warmup_all_cache()
                return results, 200
            except Exception as e:
                return {'error': str(e)}, 500
        
        @self.app.route('/cache/keys/<pattern>')
        def get_cache_keys(pattern: str):
            """Get cache keys matching pattern."""
            if not self.config.CACHE_ENABLED:
                return {
                    'keys': [],
                    'count': 0,
                    'message': 'Cache system is disabled - no keys available'
                }, 200
            
            if not self.cache_service:
                return {'error': 'Cache service not available'}, 503
            
            try:
                if not self.cache_service.redis_client:
                    return {'error': 'Redis client not available'}, 503
                
                keys = self.cache_service.redis_client.keys(f"{self.config.KEY_PREFIX}{pattern}")
                return {'keys': keys, 'count': len(keys)}, 200
            except Exception as e:
                return {'error': str(e)}, 500
    
    def get_manager(self, entity_type: str):
        """Get cache manager for entity type."""
        return self.managers.get(entity_type)
    
    def get_cache_service(self) -> Optional[CacheService]:
        """Get cache service instance."""
        return self.cache_service
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        if not self.cache_service:
            return {'error': 'Cache service not available'}
        
        stats = {
            'cache_service': self.cache_service.get_stats(),
            'managers': {}
        }
        
        for name, manager in self.managers.items():
            stats['managers'][name] = manager.get_stats()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        if not self.config.CACHE_ENABLED:
            return {
                'status': 'disabled',
                'enabled': False,
                'message': 'Cache system is disabled via configuration',
                'components': {
                    'cache_service': False,
                    'managers': False
                },
                'config': {
                    'cache_enabled': False,
                    'cache_type': self.config.CACHE_TYPE,
                    'default_timeout': self.config.DEFAULT_TIMEOUT,
                    'key_prefix': self.config.KEY_PREFIX
                }
            }
        
        if not self.cache_service:
            return {
                'status': 'unhealthy',
                'enabled': True,
                'message': 'Cache service not available',
                'components': {
                    'cache_service': False,
                    'managers': False
                }
            }
        
        # Check cache service health
        service_health = self.cache_service.health_check()
        
        # Check managers
        managers_healthy = all(
            hasattr(manager, 'get_stats') for manager in self.managers.values()
        )
        
        overall_healthy = (
            service_health['status'] == 'healthy' and 
            managers_healthy
        )
        
        return {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'enabled': True,
            'cache_service': service_health,
            'managers_healthy': managers_healthy,
            'managers_count': len(self.managers),
            'config': {
                'cache_enabled': True,
                'cache_type': self.config.CACHE_TYPE,
                'default_timeout': self.config.DEFAULT_TIMEOUT,
                'key_prefix': self.config.KEY_PREFIX
            }
        }
    
    def warmup(self) -> Dict[str, Any]:
        """Warm up all cache systems."""
        return warmup_all_cache()
    
    def clear_all(self) -> bool:
        """Clear all cache."""
        if not self.cache_service:
            return False
        
        return self.cache_service.clear()
    
    def clear_entity(self, entity_type: str) -> bool:
        """Clear cache for specific entity."""
        if entity_type not in self.managers:
            return False
        
        manager = self.managers[entity_type]
        if hasattr(manager, 'invalidate_all'):
            return manager.invalidate_all()
        
        # Fallback to pattern-based invalidation
        patterns = self.config.get_invalidation_patterns(entity_type)
        return all(
            self.cache_service.invalidate_pattern(pattern) >= 0
            for pattern in patterns
        )
    
    def get_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            'cache_type': self.config.CACHE_TYPE,
            'default_timeout': self.config.DEFAULT_TIMEOUT,
            'key_prefix': self.config.KEY_PREFIX,
            'redis_config': self.config.get_redis_config(),
            'ttl_defaults': self.config.TTL_DEFAULTS,
            'warmup_enabled': self.config.ENABLE_WARMUP,
            'metrics_enabled': self.config.ENABLE_METRICS
        }
