"""
Rate Limiting Middleware

Handles rate limiting and request throttling.
"""

from typing import Optional, Dict, Any
from flask import request, g, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .base_middleware import BaseMiddleware


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting and request throttling."""
    
    def __init__(self, app=None, limiter=None):
        self.limiter = limiter
        super().__init__(app)
    
    def init_app(self, app):
        """Initialize rate limiting with Flask app."""
        super().init_app(app)
        
        if not self.limiter:
            # Create default limiter
            self.limiter = Limiter(
                app,
                key_func=self._get_rate_limit_key,
                default_limits=["1000 per hour", "100 per minute"],
                headers_enabled=True,
                strategy="fixed-window"
            )
    
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Check rate limits before processing request."""
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit():
            return None
        
        # Check rate limit
        try:
            # The limiter will automatically check limits
            # If limit is exceeded, it will raise an exception
            pass
        except Exception as e:
            # Rate limit exceeded
            return {
                'error': True,
                'message': 'Rate limit exceeded. Please try again later.',
                'status_code': 429,
                'retry_after': self._get_retry_after()
            }
        
        return None
    
    def after_request(self, response):
        """Add rate limit headers to response."""
        if hasattr(self.limiter, 'get_window_stats'):
            try:
                stats = self.limiter.get_window_stats(
                    self._get_rate_limit_key(),
                    "1000 per hour"
                )
                
                if stats:
                    response.headers['X-RateLimit-Limit'] = str(stats[0])
                    response.headers['X-RateLimit-Remaining'] = str(stats[1])
                    response.headers['X-RateLimit-Reset'] = str(stats[2])
            except Exception:
                pass
        
        return response
    
    def _get_rate_limit_key(self) -> str:
        """Get rate limit key for the current request."""
        # Use user ID if authenticated, otherwise use IP address
        if hasattr(g, 'user_id') and g.user_id:
            return f"user:{g.user_id}"
        
        return get_remote_address()
    
    def _should_skip_rate_limit(self) -> bool:
        """Check if rate limiting should be skipped for this request."""
        skip_paths = [
            '/health',
            '/static',
            '/favicon.ico'
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _get_retry_after(self) -> int:
        """Get retry after seconds for rate limit response."""
        # Default to 60 seconds
        return 60
    
    def set_rate_limit(self, endpoint: str, limit: str):
        """Set custom rate limit for an endpoint."""
        if self.limiter:
            self.limiter.limit(limit)(endpoint)
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit information."""
        try:
            key = self._get_rate_limit_key()
            stats = self.limiter.get_window_stats(key, "1000 per hour")
            
            if stats:
                return {
                    'limit': stats[0],
                    'remaining': stats[1],
                    'reset_time': stats[2]
                }
        except Exception:
            pass
        
        return {
            'limit': 1000,
            'remaining': 999,
            'reset_time': 3600
        }
