# Middleware System

A comprehensive middleware system for authentication, logging, security, and performance monitoring in the 3D Store Flask application.

## Overview

The middleware system provides a layered approach to handling cross-cutting concerns in the Flask application. It includes authentication, logging, CORS handling, rate limiting, security monitoring, and performance tracking.

## Architecture

### Middleware Stack

The middleware components are executed in the following order:

1. **RequestIDMiddleware** - Generates unique request IDs for tracing
2. **LoggingMiddleware** - Logs requests, responses, and audit events
3. **SecurityMiddleware** - Monitors for security threats and adds security headers
4. **CORSMiddleware** - Handles Cross-Origin Resource Sharing
5. **RateLimitMiddleware** - Implements rate limiting and throttling
6. **AuthMiddleware** - Handles JWT authentication and authorization
7. **PerformanceMiddleware** - Tracks performance metrics and system resources

### Base Architecture

All middleware components inherit from `BaseMiddleware` which provides:
- Common interface for before/after request processing
- Request ID generation and tracking
- Request timing utilities
- Flask app integration

## Components

### 1. Authentication Middleware (`AuthMiddleware`)

Handles JWT token validation, user authentication, and authorization.

**Features:**
- JWT token extraction from headers and query parameters
- User validation and role checking
- Permission-based access control
- Security event logging

**Configuration:**
```python
AUTH_TOKEN_HEADER = 'Authorization'
AUTH_TOKEN_PREFIX = 'Bearer'
AUTH_LEGACY_HEADER = 'x-access-tokens'
AUTH_SKIP_PATHS = ['/health', '/login', '/signup']
```

**Usage:**
```python
from app.middleware.auth_middleware import require_auth, require_roles, require_permissions

@require_auth
def protected_route():
    return {'message': 'Access granted'}

@require_roles('admin', 'manager')
def admin_route():
    return {'message': 'Admin access'}

@require_permissions('read:users', 'write:users')
def user_management():
    return {'message': 'User management access'}
```

### 2. Logging Middleware (`LoggingMiddleware`)

Comprehensive request/response logging and audit trails.

**Features:**
- Request/response logging with structured data
- Sensitive data sanitization
- Audit event logging
- Security event logging
- Performance metrics logging

**Configuration:**
```python
LOG_FORMAT = 'json'  # 'json' or 'text'
LOG_LEVEL = 'INFO'
LOG_REQUEST_BODY = True
LOG_RESPONSE_BODY = False  # Only for errors
LOG_SENSITIVE_FIELDS = ['password', 'token', 'secret']
```

**Log Structure:**
```json
{
  "request_id": "uuid",
  "timestamp": "2024-01-01T12:00:00Z",
  "method": "POST",
  "path": "/api/users",
  "status_code": 200,
  "duration_ms": 150.5,
  "user_id": "user-uuid",
  "event_type": "response"
}
```

### 3. CORS Middleware (`CORSMiddleware`)

Handles Cross-Origin Resource Sharing configuration.

**Features:**
- Configurable allowed origins
- Preflight request handling
- Dynamic origin management
- Security policy enforcement

**Configuration:**
```python
CORS_ORIGINS = ['https://app.example.com', 'https://admin.example.com']
CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
CORS_HEADERS = ['Content-Type', 'Authorization', 'x-access-tokens']
```

### 4. Rate Limiting Middleware (`RateLimitMiddleware`)

Implements rate limiting and request throttling.

**Features:**
- Per-user and per-IP rate limiting
- Endpoint-specific rate limits
- Rate limit headers in responses
- Configurable strategies

**Configuration:**
```python
RATE_LIMIT_DEFAULT = ["1000 per hour", "100 per minute"]
RATE_LIMITS = {
    '/login': ["5 per minute", "20 per hour"],
    '/signup': ["3 per minute", "10 per hour"],
    '/api/admin': ["100 per hour", "10 per minute"]
}
```

### 5. Security Middleware (`SecurityMiddleware`)

Monitors for security threats and adds security headers.

**Features:**
- XSS attack detection
- SQL injection detection
- Suspicious pattern monitoring
- Security headers injection
- Content Security Policy

**Configuration:**
```python
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000'
}
```

### 6. Request ID Middleware (`RequestIDMiddleware`)

Generates and tracks unique request IDs.

**Features:**
- Unique request ID generation
- Request tracing across services
- Response header injection
- Request correlation

### 7. Performance Middleware (`PerformanceMiddleware`)

Tracks performance metrics and system resources.

**Features:**
- Request duration tracking
- CPU and memory usage monitoring
- Slow request detection
- Performance metrics collection
- System resource monitoring

**Metrics Collected:**
- Request duration (min, max, average)
- CPU usage per request
- Memory usage per request
- Error rates per endpoint
- System resource utilization

## Configuration

### Middleware Configuration

The middleware system is configured through `MiddlewareConfig` class:

```python
from app.middleware.config import MiddlewareConfig

config = MiddlewareConfig()

# CORS configuration
cors_config = config.get_cors_config()

# Rate limiting configuration
rate_config = config.get_rate_limit_config()

# Security configuration
security_config = config.get_security_config()
```

### Feature Flags

Enable/disable specific middleware components:

```python
FEATURES = {
    'auth_middleware': True,
    'logging_middleware': True,
    'cors_middleware': True,
    'rate_limit_middleware': True,
    'security_middleware': True,
    'performance_middleware': True
}
```

## Usage

### Basic Integration

The middleware system is automatically initialized with the Flask app:

```python
from app.middleware.extension import MiddlewareExtension

# In your Flask app initialization
middleware_ext = MiddlewareExtension(app)
```

### Middleware Manager

Access and control middleware through the manager:

```python
# Get middleware manager
manager = middleware_ext.get_manager()

# Get specific middleware
auth_middleware = manager.get_middleware(AuthMiddleware)

# Enable/disable middleware
manager.enable_middleware(PerformanceMiddleware)
manager.disable_middleware(SecurityMiddleware)

# Get performance metrics
metrics = manager.get_performance_metrics()

# Health check
health = manager.health_check()
```

### Custom Middleware

Create custom middleware by extending `BaseMiddleware`:

```python
from app.middleware.base_middleware import BaseMiddleware

class CustomMiddleware(BaseMiddleware):
    def before_request(self):
        # Process request
        return None
    
    def after_request(self, response):
        # Process response
        return response

# Add to middleware stack
manager.add_middleware(CustomMiddleware())
```

## Monitoring and Health Checks

### Health Check Endpoint

Monitor middleware system health:

```bash
GET /middleware/health
```

Response:
```json
{
  "overall": "healthy",
  "middleware": {
    "AuthMiddleware": {
      "status": "healthy",
      "initialized": true
    },
    "LoggingMiddleware": {
      "status": "healthy", 
      "initialized": true
    }
  }
}
```

### Metrics Endpoint

Get performance and system metrics:

```bash
GET /middleware/metrics
```

Response:
```json
{
  "performance": {
    "/api/users": {
      "count": 150,
      "avg_duration": 0.25,
      "max_duration": 2.1,
      "error_count": 2
    }
  },
  "rate_limits": {
    "limit": 1000,
    "remaining": 850,
    "reset_time": 3600
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 67.8,
    "disk_percent": 23.1
  }
}
```

## Security Features

### Threat Detection

The security middleware automatically detects:
- XSS attacks
- SQL injection attempts
- Suspicious request patterns
- Malicious payloads

### Security Headers

Automatic injection of security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: ...`

### Audit Logging

Comprehensive audit trail for:
- Authentication events
- Authorization failures
- Security violations
- Administrative actions

## Performance Monitoring

### Request Metrics

Track performance per endpoint:
- Request count
- Average duration
- Min/max duration
- Error rates
- CPU usage
- Memory usage

### System Metrics

Monitor system resources:
- CPU utilization
- Memory usage
- Disk usage
- Load average

### Slow Request Detection

Automatic detection and logging of slow requests:
- Configurable threshold (default: 5 seconds)
- Detailed performance breakdown
- System resource correlation

## Error Handling

### Middleware Errors

Middleware errors are handled gracefully:
- Authentication failures return 401
- Rate limit exceeded returns 429
- Security violations return 400
- System errors return 500

### Error Logging

All errors are logged with:
- Request ID for correlation
- User context (if available)
- Error details and stack trace
- Performance impact

## Best Practices

### 1. Middleware Order

Maintain proper middleware order:
1. Request ID (for tracing)
2. Logging (for audit)
3. Security (for protection)
4. CORS (for cross-origin)
5. Rate limiting (for throttling)
6. Authentication (for access control)
7. Performance (for monitoring)

### 2. Configuration Management

- Use environment-specific configurations
- Enable/disable features based on environment
- Monitor configuration changes
- Document all configuration options

### 3. Monitoring

- Set up alerts for middleware failures
- Monitor performance metrics
- Track security events
- Regular health checks

### 4. Security

- Regular security pattern updates
- Monitor for new attack vectors
- Implement proper rate limiting
- Use secure headers

## Troubleshooting

### Common Issues

1. **Middleware not executing**
   - Check middleware order
   - Verify initialization
   - Check feature flags

2. **Performance issues**
   - Review middleware configuration
   - Check for slow middleware
   - Monitor system resources

3. **Authentication problems**
   - Verify token format
   - Check user service integration
   - Review permission configuration

4. **Rate limiting issues**
   - Check rate limit configuration
   - Verify key generation
   - Review storage backend

### Debug Mode

Enable debug logging for middleware:

```python
import logging
logging.getLogger('middleware').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Distributed Tracing**
   - OpenTelemetry integration
   - Cross-service request tracing
   - Performance correlation

2. **Advanced Security**
   - Machine learning threat detection
   - Behavioral analysis
   - Real-time threat intelligence

3. **Enhanced Monitoring**
   - Real-time dashboards
   - Automated alerting
   - Performance optimization suggestions

4. **Caching Integration**
   - Middleware response caching
   - Intelligent cache invalidation
   - Performance optimization

## Conclusion

The middleware system provides a robust foundation for handling cross-cutting concerns in the 3D Store application. It ensures security, performance, and maintainability while providing comprehensive monitoring and debugging capabilities.

For more information, see the individual middleware component documentation and configuration examples.
