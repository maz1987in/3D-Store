"""
Middleware Manager

Coordinates and manages all middleware components.
"""

from typing import List, Optional, Dict, Any
from flask import Flask

from .auth_middleware import AuthMiddleware
from .logging_middleware import LoggingMiddleware
from .cors_middleware import CORSMiddleware
from .rate_limit_middleware import RateLimitMiddleware
from .request_id_middleware import RequestIDMiddleware
from .security_middleware import SecurityMiddleware
from .performance_middleware import PerformanceMiddleware


class MiddlewareManager:
    """Manages and coordinates all middleware components."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.middleware_stack: List[Any] = []
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware manager with Flask app."""
        self.app = app
        self._setup_middleware_stack()
    
    def _setup_middleware_stack(self):
        """Setup the middleware stack in the correct order."""
        # Order matters: earlier middleware runs first
        self.middleware_stack = [
            RequestIDMiddleware(self.app),
            LoggingMiddleware(self.app),
            SecurityMiddleware(self.app),
            CORSMiddleware(self.app),
            RateLimitMiddleware(self.app),
            AuthMiddleware(self.app),
            PerformanceMiddleware(self.app)
        ]
    
    def add_middleware(self, middleware, position: Optional[int] = None):
        """Add middleware to the stack."""
        if position is None:
            position = len(self.middleware_stack)
        
        self.middleware_stack.insert(position, middleware)
        
        if self.app:
            middleware.init_app(self.app)
    
    def remove_middleware(self, middleware_class):
        """Remove middleware from the stack."""
        self.middleware_stack = [
            m for m in self.middleware_stack 
            if not isinstance(m, middleware_class)
        ]
    
    def get_middleware(self, middleware_class):
        """Get specific middleware instance."""
        for middleware in self.middleware_stack:
            if isinstance(middleware, middleware_class):
                return middleware
        return None
    
    def get_all_middleware(self) -> List[Any]:
        """Get all middleware instances."""
        return self.middleware_stack.copy()
    
    def get_middleware_status(self) -> Dict[str, Any]:
        """Get status of all middleware."""
        status = {}
        
        for middleware in self.middleware_stack:
            middleware_name = middleware.__class__.__name__
            status[middleware_name] = {
                'enabled': True,
                'type': middleware.__class__.__name__,
                'app_initialized': middleware.app is not None
            }
        
        return status
    
    def enable_middleware(self, middleware_class):
        """Enable specific middleware."""
        middleware = self.get_middleware(middleware_class)
        if middleware and not middleware.app:
            middleware.init_app(self.app)
    
    def disable_middleware(self, middleware_class):
        """Disable specific middleware."""
        middleware = self.get_middleware(middleware_class)
        if middleware and middleware.app:
            # Remove hooks to disable middleware
            if hasattr(middleware, '_unregister_hooks'):
                middleware._unregister_hooks()
            middleware.app = None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from performance middleware."""
        perf_middleware = self.get_middleware(PerformanceMiddleware)
        if perf_middleware:
            return perf_middleware.get_performance_metrics()
        return {}
    
    def get_security_events(self) -> List[Dict[str, Any]]:
        """Get security events from security middleware."""
        # This would need to be implemented in SecurityMiddleware
        # to store and retrieve security events
        return []
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information."""
        rate_middleware = self.get_middleware(RateLimitMiddleware)
        if rate_middleware:
            return rate_middleware.get_rate_limit_info()
        return {}
    
    def reset_metrics(self):
        """Reset all middleware metrics."""
        perf_middleware = self.get_middleware(PerformanceMiddleware)
        if perf_middleware:
            perf_middleware.reset_metrics()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all middleware."""
        health_status = {
            'overall': 'healthy',
            'middleware': {}
        }
        
        for middleware in self.middleware_stack:
            middleware_name = middleware.__class__.__name__
            try:
                # Basic health check - middleware is initialized
                is_healthy = middleware.app is not None
                health_status['middleware'][middleware_name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'initialized': is_healthy
                }
            except Exception as e:
                health_status['middleware'][middleware_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall'] = 'unhealthy'
        
        return health_status
