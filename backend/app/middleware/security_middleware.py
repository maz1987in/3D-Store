"""
Security Middleware

Handles security headers, input validation, and security monitoring.
"""

import re
from typing import Optional, Dict, Any, List
from flask import request, g, current_app

from .base_middleware import BaseMiddleware


class SecurityMiddleware(BaseMiddleware):
    """Middleware for security headers and monitoring."""
    
    def __init__(self, app=None):
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<style[^>]*>',
            r'expression\s*\(',
            r'url\s*\(',
            r'@import',
            r'<.*?>',
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'%252e%252e%252f',
            r'%252e%252e%255c'
        ]
        super().__init__(app)
    
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Check for security threats before processing request."""
        # Check for suspicious patterns in request
        if self._detect_suspicious_patterns():
            self._log_security_event('suspicious_request', {
                'path': request.path,
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string
            })
            return {
                'error': True,
                'message': 'Suspicious request detected',
                'status_code': 400
            }
        
        # Check for SQL injection patterns
        if self._detect_sql_injection():
            self._log_security_event('sql_injection_attempt', {
                'path': request.path,
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string
            })
            return {
                'error': True,
                'message': 'Invalid request format',
                'status_code': 400
            }
        
        return None
    
    def after_request(self, response):
        """Add security headers to response."""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = self._get_csp_header()
        
        return response
    
    def _detect_suspicious_patterns(self) -> bool:
        """Detect suspicious patterns in request data."""
        # Check URL parameters
        for key, value in request.args.items():
            if self._contains_suspicious_pattern(str(value)):
                return True
        
        # Check form data
        if request.form:
            for key, value in request.form.items():
                if self._contains_suspicious_pattern(str(value)):
                    return True
        
        # Check JSON data
        if request.is_json:
            json_data = request.get_json()
            if self._check_json_for_suspicious_patterns(json_data):
                return True
        
        return False
    
    def _detect_sql_injection(self) -> bool:
        """Detect SQL injection patterns."""
        sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'alter\s+table',
            r'create\s+table',
            r'exec\s*\(',
            r'execute\s*\(',
            r'sp_',
            r'xp_',
            r'--',
            r'/\*.*?\*/',
            r';\s*drop',
            r';\s*delete',
            r';\s*insert',
            r';\s*update',
            r';\s*alter',
            r';\s*create'
        ]
        
        # Check all request data
        all_data = []
        all_data.extend(request.args.values())
        all_data.extend(request.form.values())
        
        if request.is_json:
            json_data = request.get_json()
            if isinstance(json_data, dict):
                all_data.extend(str(v) for v in json_data.values())
        
        for data in all_data:
            data_str = str(data).lower()
            for pattern in sql_patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    return True
        
        return False
    
    def _contains_suspicious_pattern(self, text: str) -> bool:
        """Check if text contains suspicious patterns."""
        text_lower = text.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def _check_json_for_suspicious_patterns(self, data: Any) -> bool:
        """Recursively check JSON data for suspicious patterns."""
        if isinstance(data, dict):
            for value in data.values():
                if self._check_json_for_suspicious_patterns(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._check_json_for_suspicious_patterns(item):
                    return True
        elif isinstance(data, str):
            return self._contains_suspicious_pattern(data)
        
        return False
    
    def _get_csp_header(self) -> str:
        """Get Content Security Policy header."""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        current_app.logger.warning(f"Security event: {event_type}", extra=details)
    
    def add_suspicious_pattern(self, pattern: str):
        """Add a new suspicious pattern to monitor."""
        if pattern not in self.suspicious_patterns:
            self.suspicious_patterns.append(pattern)
    
    def remove_suspicious_pattern(self, pattern: str):
        """Remove a suspicious pattern from monitoring."""
        if pattern in self.suspicious_patterns:
            self.suspicious_patterns.remove(pattern)
    
    def get_suspicious_patterns(self) -> List[str]:
        """Get list of monitored suspicious patterns."""
        return self.suspicious_patterns.copy()
