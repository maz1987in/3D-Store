"""
CORS Middleware

Handles Cross-Origin Resource Sharing configuration and validation.
"""

from typing import Optional, Dict, Any, List
from flask import request, g, current_app
from flask_cors import CORS

from .base_middleware import BaseMiddleware


class CORSMiddleware(BaseMiddleware):
    """Middleware for handling CORS configuration and validation."""
    
    def __init__(self, app=None, origins=None, methods=None, headers=None):
        self.origins = origins or ['*']
        self.methods = methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.headers = headers or ['Content-Type', 'Authorization', 'x-access-tokens']
        self.cors = None
        super().__init__(app)
    
    def init_app(self, app):
        """Initialize CORS with Flask app."""
        super().init_app(app)
        
        # Configure CORS
        self.cors = CORS(app, 
                        origins=self.origins,
                        methods=self.methods,
                        allow_headers=self.headers,
                        supports_credentials=True,
                        vary_header=True)
    
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Handle CORS preflight requests."""
        if request.method == 'OPTIONS':
            # Handle preflight request
            return self._handle_preflight()
        
        # Validate origin for non-preflight requests
        if not self._is_origin_allowed():
            return {
                'error': True,
                'message': 'CORS policy violation: Origin not allowed',
                'status_code': 403
            }
        
        return None
    
    def after_request(self, response):
        """Add CORS headers to response."""
        if self.cors:
            # Let Flask-CORS handle the headers
            pass
        
        return response
    
    def _handle_preflight(self) -> Optional[Dict[str, Any]]:
        """Handle CORS preflight OPTIONS request."""
        # Flask-CORS will handle this automatically
        return None
    
    def _is_origin_allowed(self) -> bool:
        """Check if the request origin is allowed."""
        origin = request.headers.get('Origin')
        
        if not origin:
            return True  # Same-origin request
        
        if '*' in self.origins:
            return True
        
        return origin in self.origins
    
    def add_origin(self, origin: str):
        """Add a new allowed origin."""
        if origin not in self.origins:
            self.origins.append(origin)
    
    def remove_origin(self, origin: str):
        """Remove an allowed origin."""
        if origin in self.origins:
            self.origins.remove(origin)
    
    def get_allowed_origins(self) -> List[str]:
        """Get list of allowed origins."""
        return self.origins.copy()
    
    def is_origin_allowed(self, origin: str) -> bool:
        """Check if a specific origin is allowed."""
        return origin in self.origins or '*' in self.origins
