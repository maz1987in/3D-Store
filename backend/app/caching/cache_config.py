"""
Cache Configuration

Configuration settings for the caching system.
"""

import os
from typing import Dict, Any, List


class CacheConfig:
    """Configuration for caching system."""
    
    # Basic Configuration
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'RedisCache')
    DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutes
    KEY_PREFIX = os.getenv('CACHE_KEY_PREFIX', 'store3d_')
    IGNORE_ERRORS = os.getenv('CACHE_IGNORE_ERRORS', 'True').lower() == 'true'
    
    # Redis Configuration
    REDIS_HOST = os.getenv('CACHE_REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('CACHE_REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('CACHE_REDIS_PASSWORD', None)
    REDIS_DB = int(os.getenv('CACHE_REDIS_DB', 0))
    REDIS_URL = os.getenv('CACHE_REDIS_URL', None)
    
    # Cache Strategies
    DEFAULT_STRATEGY = os.getenv('CACHE_DEFAULT_STRATEGY', 'ttl')
    ENABLE_WRITE_THROUGH = os.getenv('CACHE_ENABLE_WRITE_THROUGH', 'False').lower() == 'true'
    ENABLE_WRITE_BEHIND = os.getenv('CACHE_ENABLE_WRITE_BEHIND', 'False').lower() == 'true'
    ENABLE_REFRESH_AHEAD = os.getenv('CACHE_ENABLE_REFRESH_AHEAD', 'False').lower() == 'true'
    
    # TTL Configuration
    TTL_DEFAULTS = {
        'user': 3600,           # 1 hour
        'product': 1800,        # 30 minutes
        'order': 900,           # 15 minutes
        'inventory': 600,       # 10 minutes
        'financial': 1800,      # 30 minutes
        'category': 3600,       # 1 hour
        'search': 300,          # 5 minutes
        'session': 1800,        # 30 minutes
        'api_response': 60,     # 1 minute
        'static_content': 86400 # 24 hours
    }
    
    # Cache Warming
    ENABLE_WARMUP = os.getenv('CACHE_ENABLE_WARMUP', 'True').lower() == 'true'
    WARMUP_BATCH_SIZE = int(os.getenv('CACHE_WARMUP_BATCH_SIZE', 10))
    WARMUP_DELAY = int(os.getenv('CACHE_WARMUP_DELAY', 5))  # seconds
    
    # Cache Invalidation
    ENABLE_AUTO_INVALIDATION = os.getenv('CACHE_ENABLE_AUTO_INVALIDATION', 'True').lower() == 'true'
    INVALIDATION_PATTERNS = {
        'user': ['user|*', 'user_roles|*', 'user_permissions|*'],
        'product': ['product|*', 'products_by_category|*', 'products_search|*'],
        'order': ['order|*', 'user_orders|*', 'order_status|*'],
        'inventory': ['inventory|*', 'branch_inventory|*'],
        'financial': ['financial|*', 'dashboard_stats|*']
    }
    
    # Performance Configuration
    ENABLE_COMPRESSION = os.getenv('CACHE_ENABLE_COMPRESSION', 'False').lower() == 'true'
    COMPRESSION_THRESHOLD = int(os.getenv('CACHE_COMPRESSION_THRESHOLD', 1024))  # bytes
    ENABLE_SERIALIZATION = os.getenv('CACHE_ENABLE_SERIALIZATION', 'True').lower() == 'true'
    
    # Monitoring Configuration
    ENABLE_METRICS = os.getenv('CACHE_ENABLE_METRICS', 'True').lower() == 'true'
    METRICS_INTERVAL = int(os.getenv('CACHE_METRICS_INTERVAL', 60))  # seconds
    ENABLE_LOGGING = os.getenv('CACHE_ENABLE_LOGGING', 'True').lower() == 'true'
    LOG_LEVEL = os.getenv('CACHE_LOG_LEVEL', 'INFO')
    
    # Cache Limits
    MAX_CACHE_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))  # items
    MAX_KEY_LENGTH = int(os.getenv('CACHE_MAX_KEY_LENGTH', 250))
    MAX_VALUE_SIZE = int(os.getenv('CACHE_MAX_VALUE_SIZE', 1024 * 1024))  # 1MB
    
    # Circuit Breaker
    ENABLE_CIRCUIT_BREAKER = os.getenv('CACHE_ENABLE_CIRCUIT_BREAKER', 'True').lower() == 'true'
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv('CACHE_CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.getenv('CACHE_CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 60))
    
    # Cache Warming Functions
    WARMUP_FUNCTIONS = [
        'app.caching.warmup.warmup_user_cache',
        'app.caching.warmup.warmup_product_cache',
        'app.caching.warmup.warmup_category_cache',
        'app.caching.warmup.warmup_financial_cache'
    ]
    
    # Cache Keys Configuration
    KEY_SEPARATORS = {
        'default': '|',
        'user': ':',
        'product': '_',
        'order': '-',
        'inventory': '.',
        'financial': '::'
    }
    
    # Cache Namespaces
    NAMESPACES = {
        'user': 'usr',
        'product': 'prd',
        'order': 'ord',
        'inventory': 'inv',
        'financial': 'fin',
        'category': 'cat',
        'search': 'src',
        'session': 'ses',
        'api': 'api',
        'static': 'stc'
    }
    
    @classmethod
    def get_ttl(cls, entity_type: str) -> int:
        """Get TTL for entity type."""
        return cls.TTL_DEFAULTS.get(entity_type, cls.DEFAULT_TIMEOUT)
    
    @classmethod
    def get_invalidation_patterns(cls, entity_type: str) -> List[str]:
        """Get invalidation patterns for entity type."""
        return cls.INVALIDATION_PATTERNS.get(entity_type, [])
    
    @classmethod
    def get_key_separator(cls, entity_type: str) -> str:
        """Get key separator for entity type."""
        return cls.KEY_SEPARATORS.get(entity_type, cls.KEY_SEPARATORS['default'])
    
    @classmethod
    def get_namespace(cls, entity_type: str) -> str:
        """Get namespace for entity type."""
        return cls.NAMESPACES.get(entity_type, entity_type[:3])
    
    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis configuration."""
        config = {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'db': cls.REDIS_DB,
            'decode_responses': True
        }
        
        if cls.REDIS_PASSWORD:
            config['password'] = cls.REDIS_PASSWORD
        
        if cls.REDIS_URL:
            config['url'] = cls.REDIS_URL
        
        return config
    
    @classmethod
    def get_flask_cache_config(cls) -> Dict[str, Any]:
        """Get Flask-Caching configuration."""
        config = {
            'CACHE_TYPE': cls.CACHE_TYPE,
            'CACHE_DEFAULT_TIMEOUT': cls.DEFAULT_TIMEOUT,
            'CACHE_IGNORE_ERRORS': cls.IGNORE_ERRORS,
            'CACHE_KEY_PREFIX': cls.KEY_PREFIX
        }
        
        if cls.CACHE_TYPE == 'RedisCache':
            config.update({
                'CACHE_REDIS_HOST': cls.REDIS_HOST,
                'CACHE_REDIS_PORT': cls.REDIS_PORT,
                'CACHE_REDIS_DB': cls.REDIS_DB
            })
            
            if cls.REDIS_PASSWORD:
                config['CACHE_REDIS_PASSWORD'] = cls.REDIS_PASSWORD
            
            if cls.REDIS_URL:
                config['CACHE_REDIS_URL'] = cls.REDIS_URL
        
        return config
    
    @classmethod
    def is_entity_cached(cls, entity_type: str) -> bool:
        """Check if entity type should be cached."""
        return entity_type in cls.TTL_DEFAULTS
    
    @classmethod
    def get_cache_strategy(cls, entity_type: str) -> str:
        """Get cache strategy for entity type."""
        if entity_type in ['user', 'category']:
            return 'ttl'  # Long-lived data
        elif entity_type in ['product', 'financial']:
            return 'refresh_ahead'  # Frequently accessed
        elif entity_type in ['order', 'inventory']:
            return 'write_through'  # Critical data
        else:
            return cls.DEFAULT_STRATEGY
    
    @classmethod
    def get_compression_config(cls) -> Dict[str, Any]:
        """Get compression configuration."""
        return {
            'enabled': cls.ENABLE_COMPRESSION,
            'threshold': cls.COMPRESSION_THRESHOLD,
            'algorithm': 'gzip'
        }
    
    @classmethod
    def get_monitoring_config(cls) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            'enabled': cls.ENABLE_METRICS,
            'interval': cls.METRICS_INTERVAL,
            'logging_enabled': cls.ENABLE_LOGGING,
            'log_level': cls.LOG_LEVEL
        }
    
    @classmethod
    def get_circuit_breaker_config(cls) -> Dict[str, Any]:
        """Get circuit breaker configuration."""
        return {
            'enabled': cls.ENABLE_CIRCUIT_BREAKER,
            'failure_threshold': cls.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            'recovery_timeout': cls.CIRCUIT_BREAKER_RECOVERY_TIMEOUT
        }
    
    @classmethod
    def get_feature_flags(cls) -> Dict[str, Any]:
        """Get feature flags configuration."""
        return {
            'cache_enabled': cls.CACHE_ENABLED,
            'cache_warmup': cls.CACHE_ENABLED and cls.ENABLE_WARMUP,
            'cache_metrics': cls.CACHE_ENABLED and cls.ENABLE_METRICS,
            'cache_compression': cls.CACHE_ENABLED and cls.ENABLE_COMPRESSION,
            'cache_circuit_breaker': cls.CACHE_ENABLED and cls.ENABLE_CIRCUIT_BREAKER,
            'cache_auto_invalidation': cls.CACHE_ENABLED and cls.ENABLE_AUTO_INVALIDATION
        }
