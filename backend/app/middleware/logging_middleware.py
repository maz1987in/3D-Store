"""
Logging Middleware

Handles request/response logging, error logging, and audit trails.
"""

import logging
import json
from typing import Optional, Dict, Any
from flask import request, g, current_app
from datetime import datetime, timezone

from .base_middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    """Middleware for comprehensive request/response logging."""
    
    def __init__(self, app=None):
        self.logger = logging.getLogger('middleware.access')
        super().__init__(app)
    
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Log request details before processing."""
        # Set request start time
        g.request_start_time = self._get_request_start_time()
        g.request_id = self._get_request_id()
        
        # Log request details
        self._log_request()
        
        return None
    
    def after_request(self, response):
        """Log response details after processing."""
        # Calculate request duration
        duration = self._get_request_duration()
        
        # Log response details
        self._log_response(response, duration)
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    def _log_request(self):
        """Log incoming request details."""
        log_data = {
            'request_id': g.request_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'method': request.method,
            'path': request.path,
            'query_string': request.query_string.decode('utf-8'),
            'remote_addr': request.remote_addr,
            'user_agent': request.user_agent.string,
            'content_type': request.content_type,
            'content_length': request.content_length,
            'headers': dict(request.headers),
            'user_id': getattr(g, 'user_id', None),
            'event_type': 'request'
        }
        
        # Log request body for non-GET requests (excluding sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            try:
                body = request.get_json()
                # Remove sensitive fields
                sanitized_body = self._sanitize_request_body(body)
                log_data['request_body'] = sanitized_body
            except Exception:
                log_data['request_body'] = 'Unable to parse JSON'
        
        self.logger.info('Request received', extra=log_data)
    
    def _log_response(self, response, duration: float):
        """Log response details."""
        log_data = {
            'request_id': g.request_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'content_length': response.content_length,
            'user_id': getattr(g, 'user_id', None),
            'event_type': 'response'
        }
        
        # Log response body for errors
        if response.status_code >= 400:
            try:
                if response.is_json:
                    log_data['response_body'] = response.get_json()
                else:
                    log_data['response_body'] = response.get_data(as_text=True)
            except Exception:
                log_data['response_body'] = 'Unable to parse response'
        
        # Set log level based on status code
        if response.status_code >= 500:
            self.logger.error('Response sent', extra=log_data)
        elif response.status_code >= 400:
            self.logger.warning('Response sent', extra=log_data)
        else:
            self.logger.info('Response sent', extra=log_data)
    
    def _sanitize_request_body(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from request body for logging."""
        if not isinstance(body, dict):
            return body
        
        sensitive_fields = [
            'password', 'token', 'secret', 'key', 'auth',
            'credit_card', 'cvv', 'ssn', 'social_security'
        ]
        
        sanitized = {}
        for key, value in body.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_request_body(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_request_body(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit events for compliance and security."""
        audit_logger = logging.getLogger('middleware.audit')
        
        log_data = {
            'request_id': g.request_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'user_id': getattr(g, 'user_id', None),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string,
            'details': details
        }
        
        audit_logger.info('Audit event', extra=log_data)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events for monitoring."""
        security_logger = logging.getLogger('middleware.security')
        
        log_data = {
            'request_id': g.request_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'user_id': getattr(g, 'user_id', None),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string,
            'details': details
        }
        
        security_logger.warning('Security event', extra=log_data)
