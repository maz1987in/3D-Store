"""
Middleware Extension

Flask extension for the middleware system.
"""

from flask import Flask
from typing import Optional

from .middleware_manager import MiddlewareManager
from .config import MiddlewareConfig


class MiddlewareExtension:
    """Flask extension for middleware system."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.manager = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the middleware extension with Flask app."""
        self.app = app
        
        # Create middleware manager
        self.manager = MiddlewareManager(app)
        
        # Configure middleware based on app config
        self._configure_middleware()
        
        # Register health check endpoint
        self._register_health_endpoint()
        
        # Register metrics endpoint
        self._register_metrics_endpoint()
    
    def _configure_middleware(self):
        """Configure middleware based on app configuration."""
        config = MiddlewareConfig()
        
        # Configure CORS middleware
        cors_middleware = self.manager.get_middleware(CORSMiddleware)
        if cors_middleware:
            cors_config = config.get_cors_config()
            cors_middleware.origins = cors_config['origins']
            cors_middleware.methods = cors_config['methods']
            cors_middleware.headers = cors_config['allow_headers']
        
        # Configure rate limiting middleware
        rate_middleware = self.manager.get_middleware(RateLimitMiddleware)
        if rate_middleware:
            rate_config = config.get_rate_limit_config()
            # Apply endpoint-specific rate limits
            for endpoint, limits in rate_config['endpoint_limits'].items():
                rate_middleware.set_rate_limit(endpoint, limits)
        
        # Configure security middleware
        security_middleware = self.manager.get_middleware(SecurityMiddleware)
        if security_middleware:
            security_config = config.get_security_config()
            # Add suspicious patterns
            for pattern in security_config['suspicious_patterns']:
                security_middleware.add_suspicious_pattern(pattern)
    
    def _register_health_endpoint(self):
        """Register health check endpoint for middleware."""
        @self.app.route('/middleware/health')
        def middleware_health():
            """Health check endpoint for middleware system."""
            health_status = self.manager.health_check()
            return health_status, 200 if health_status['overall'] == 'healthy' else 503
    
    def _register_metrics_endpoint(self):
        """Register metrics endpoint for middleware."""
        @self.app.route('/middleware/metrics')
        def middleware_metrics():
            """Metrics endpoint for middleware system."""
            metrics = {
                'performance': self.manager.get_performance_metrics(),
                'rate_limits': self.manager.get_rate_limit_info(),
                'system': self._get_system_metrics()
            }
            return metrics, 200
    
    def _get_system_metrics(self):
        """Get system metrics."""
        perf_middleware = self.manager.get_middleware(PerformanceMiddleware)
        if perf_middleware:
            return perf_middleware.get_system_metrics()
        return {}
    
    def get_manager(self) -> MiddlewareManager:
        """Get the middleware manager instance."""
        return self.manager
    
    def enable_middleware(self, middleware_class):
        """Enable specific middleware."""
        if self.manager:
            self.manager.enable_middleware(middleware_class)
    
    def disable_middleware(self, middleware_class):
        """Disable specific middleware."""
        if self.manager:
            self.manager.disable_middleware(middleware_class)
    
    def get_status(self):
        """Get middleware system status."""
        if self.manager:
            return self.manager.get_middleware_status()
        return {}


# Import middleware classes for the extension
from .cors_middleware import CORSMiddleware
from .rate_limit_middleware import RateLimitMiddleware
from .security_middleware import SecurityMiddleware
from .performance_middleware import PerformanceMiddleware
