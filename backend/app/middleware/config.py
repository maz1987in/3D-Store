"""
Middleware Configuration

Configuration settings for all middleware components.
"""

from typing import List, Dict, Any


class MiddlewareConfig:
    """Configuration for middleware components."""
    
    # CORS Configuration
    CORS_ORIGINS = ['*']  # Configure based on your frontend domains
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
    CORS_HEADERS = [
        'Content-Type', 
        'Authorization', 
        'x-access-tokens',
        'X-Request-ID',
        'X-API-Key'
    ]
    
    # Rate Limiting Configuration
    RATE_LIMIT_DEFAULT = ["1000 per hour", "100 per minute"]
    RATE_LIMIT_STRATEGY = "fixed-window"
    RATE_LIMIT_HEADERS_ENABLED = True
    
    # Rate limits by endpoint
    RATE_LIMITS = {
        '/login': ["5 per minute", "20 per hour"],
        '/signup': ["3 per minute", "10 per hour"],
        '/password/reset': ["2 per minute", "5 per hour"],
        '/api/admin': ["100 per hour", "10 per minute"],
        '/api/upload': ["10 per minute", "50 per hour"]
    }
    
    # Security Configuration
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # Content Security Policy
    CSP_POLICY = (
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
    
    # Suspicious patterns for security monitoring
    SUSPICIOUS_PATTERNS = [
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
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
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
    
    # Logging Configuration
    LOG_FORMAT = 'json'  # 'json' or 'text'
    LOG_LEVEL = 'INFO'
    LOG_REQUEST_BODY = True
    LOG_RESPONSE_BODY = False  # Only for errors
    LOG_SENSITIVE_FIELDS = [
        'password', 'token', 'secret', 'key', 'auth',
        'credit_card', 'cvv', 'ssn', 'social_security'
    ]
    
    # Performance Configuration
    PERFORMANCE_SLOW_REQUEST_THRESHOLD = 5.0  # seconds
    PERFORMANCE_METRICS_ENABLED = True
    PERFORMANCE_HEADERS_ENABLED = True
    
    # Authentication Configuration
    AUTH_TOKEN_HEADER = 'Authorization'
    AUTH_TOKEN_PREFIX = 'Bearer'
    AUTH_LEGACY_HEADER = 'x-access-tokens'
    AUTH_QUERY_PARAM = 'token'
    
    # Skip authentication for these paths
    AUTH_SKIP_PATHS = [
        '/health',
        '/login',
        '/signup',
        '/email',
        '/api/docs',
        '/static',
        '/favicon.ico',
        '/metrics',
        '/status'
    ]
    
    # Skip rate limiting for these paths
    RATE_LIMIT_SKIP_PATHS = [
        '/health',
        '/static',
        '/favicon.ico',
        '/metrics'
    ]
    
    # Request ID Configuration
    REQUEST_ID_HEADER = 'X-Request-ID'
    REQUEST_ID_GENERATE_IF_MISSING = True
    
    # Middleware Order (execution order)
    MIDDLEWARE_ORDER = [
        'RequestIDMiddleware',
        'LoggingMiddleware', 
        'SecurityMiddleware',
        'CORSMiddleware',
        'RateLimitMiddleware',
        'AuthMiddleware',
        'PerformanceMiddleware'
    ]
    
    # Feature flags
    FEATURES = {
        'auth_middleware': True,
        'logging_middleware': True,
        'cors_middleware': True,
        'rate_limit_middleware': True,
        'request_id_middleware': True,
        'security_middleware': True,
        'performance_middleware': True
    }
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Get CORS configuration."""
        return {
            'origins': cls.CORS_ORIGINS,
            'methods': cls.CORS_METHODS,
            'allow_headers': cls.CORS_HEADERS,
            'supports_credentials': True,
            'vary_header': True
        }
    
    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            'default_limits': cls.RATE_LIMIT_DEFAULT,
            'strategy': cls.RATE_LIMIT_STRATEGY,
            'headers_enabled': cls.RATE_LIMIT_HEADERS_ENABLED,
            'endpoint_limits': cls.RATE_LIMITS
        }
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            'headers': cls.SECURITY_HEADERS,
            'csp_policy': cls.CSP_POLICY,
            'suspicious_patterns': cls.SUSPICIOUS_PATTERNS,
            'sql_injection_patterns': cls.SQL_INJECTION_PATTERNS
        }
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'format': cls.LOG_FORMAT,
            'level': cls.LOG_LEVEL,
            'log_request_body': cls.LOG_REQUEST_BODY,
            'log_response_body': cls.LOG_RESPONSE_BODY,
            'sensitive_fields': cls.LOG_SENSITIVE_FIELDS
        }
    
    @classmethod
    def get_performance_config(cls) -> Dict[str, Any]:
        """Get performance configuration."""
        return {
            'slow_request_threshold': cls.PERFORMANCE_SLOW_REQUEST_THRESHOLD,
            'metrics_enabled': cls.PERFORMANCE_METRICS_ENABLED,
            'headers_enabled': cls.PERFORMANCE_HEADERS_ENABLED
        }
    
    @classmethod
    def get_auth_config(cls) -> Dict[str, Any]:
        """Get authentication configuration."""
        return {
            'token_header': cls.AUTH_TOKEN_HEADER,
            'token_prefix': cls.AUTH_TOKEN_PREFIX,
            'legacy_header': cls.AUTH_LEGACY_HEADER,
            'query_param': cls.AUTH_QUERY_PARAM,
            'skip_paths': cls.AUTH_SKIP_PATHS
        }
