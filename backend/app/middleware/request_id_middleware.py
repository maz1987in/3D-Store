"""
Request ID Middleware

Handles request ID generation and tracking for request tracing.
"""

import uuid
from typing import Optional, Dict, Any
from flask import request, g, current_app

from .base_middleware import BaseMiddleware


class RequestIDMiddleware(BaseMiddleware):
    """Middleware for generating and tracking request IDs."""
    
    def __init__(self, app=None, header_name='X-Request-ID'):
        self.header_name = header_name
        super().__init__(app)
    
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Generate or extract request ID before processing."""
        # Check if request ID is provided in headers
        request_id = request.headers.get(self.header_name)
        
        if not request_id:
            # Generate new request ID
            request_id = str(uuid.uuid4())
        
        # Store request ID in Flask g object
        g.request_id = request_id
        
        # Log request ID
        current_app.logger.debug(f"Request ID: {request_id}")
        
        return None
    
    def after_request(self, response):
        """Add request ID to response headers."""
        if hasattr(g, 'request_id'):
            response.headers[self.header_name] = g.request_id
        
        return response
    
    def get_request_id(self) -> str:
        """Get current request ID."""
        return getattr(g, 'request_id', 'unknown')
    
    def set_request_id(self, request_id: str):
        """Set custom request ID."""
        g.request_id = request_id
