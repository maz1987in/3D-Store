"""
Base Middleware Class

Provides a common interface for all middleware components.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from flask import Flask, request, g
import time
import uuid


class BaseMiddleware(ABC):
    """Base class for all middleware components."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app."""
        self.app = app
        self._register_hooks()
    
    @abstractmethod
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Process request before it reaches the route handler."""
        pass
    
    @abstractmethod
    def after_request(self, response) -> Any:
        """Process response after route handler completes."""
        pass
    
    def _register_hooks(self):
        """Register Flask hooks for this middleware."""
        if self.app:
            self.app.before_request(self.before_request)
            self.app.after_request(self.after_request)
    
    def _get_request_id(self) -> str:
        """Get or generate request ID."""
        if not hasattr(g, 'request_id'):
            g.request_id = str(uuid.uuid4())
        return g.request_id
    
    def _get_request_start_time(self) -> float:
        """Get request start time."""
        if not hasattr(g, 'request_start_time'):
            g.request_start_time = time.time()
        return g.request_start_time
    
    def _get_request_duration(self) -> float:
        """Calculate request duration."""
        if hasattr(g, 'request_start_time'):
            return time.time() - g.request_start_time
        return 0.0
