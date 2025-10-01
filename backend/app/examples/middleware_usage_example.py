"""
Middleware Usage Examples

This file demonstrates how to use the middleware system in the 3D Store application.
"""

from flask import Flask, jsonify, request
from app.middleware.extension import MiddlewareExtension
from app.middleware.auth_middleware import require_auth, require_roles, require_permissions
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.performance_middleware import PerformanceMiddleware


def create_example_app():
    """Create a Flask app with middleware examples."""
    app = Flask(__name__)
    
    # Initialize middleware system
    middleware_ext = MiddlewareExtension(app)
    
    # Get middleware manager for advanced usage
    manager = middleware_ext.get_manager()
    
    # Example routes demonstrating middleware usage
    
    @app.route('/public')
    def public_endpoint():
        """Public endpoint - no authentication required."""
        return jsonify({
            'message': 'This is a public endpoint',
            'request_id': request.headers.get('X-Request-ID', 'unknown')
        })
    
    @app.route('/protected')
    @require_auth
    def protected_endpoint():
        """Protected endpoint - requires authentication."""
        return jsonify({
            'message': 'This is a protected endpoint',
            'user_id': request.user_id if hasattr(request, 'user_id') else 'unknown',
            'request_id': request.headers.get('X-Request-ID', 'unknown')
        })
    
    @app.route('/admin')
    @require_roles('admin', 'manager')
    def admin_endpoint():
        """Admin endpoint - requires admin or manager role."""
        return jsonify({
            'message': 'This is an admin endpoint',
            'user_id': request.user_id if hasattr(request, 'user_id') else 'unknown',
            'roles': request.user_roles if hasattr(request, 'user_roles') else []
        })
    
    @app.route('/users')
    @require_permissions('read:users', 'write:users')
    def user_management():
        """User management endpoint - requires specific permissions."""
        return jsonify({
            'message': 'User management endpoint',
            'permissions': request.permission if hasattr(request, 'permission') else []
        })
    
    @app.route('/slow')
    def slow_endpoint():
        """Simulate a slow endpoint for performance monitoring."""
        import time
        time.sleep(2)  # Simulate slow operation
        return jsonify({
            'message': 'This endpoint is intentionally slow',
            'duration': '2 seconds'
        })
    
    @app.route('/error')
    def error_endpoint():
        """Simulate an error for error handling demonstration."""
        raise ValueError("This is a test error")
    
    @app.route('/rate-limited')
    def rate_limited_endpoint():
        """Endpoint that will be rate limited."""
        return jsonify({
            'message': 'This endpoint has rate limiting applied',
            'rate_limit_info': manager.get_rate_limit_info()
        })
    
    @app.route('/metrics')
    def metrics_endpoint():
        """Get middleware metrics."""
        return jsonify({
            'performance_metrics': manager.get_performance_metrics(),
            'rate_limit_info': manager.get_rate_limit_info(),
            'middleware_status': manager.get_middleware_status()
        })
    
    @app.route('/health')
    def health_endpoint():
        """Health check endpoint."""
        health_status = manager.health_check()
        return jsonify(health_status), 200 if health_status['overall'] == 'healthy' else 503
    
    # Example of custom middleware usage
    @app.route('/custom-logging')
    def custom_logging_example():
        """Example of using logging middleware directly."""
        logging_middleware = manager.get_middleware(LoggingMiddleware)
        
        if logging_middleware:
            # Log custom audit event
            logging_middleware.log_audit_event('custom_action', {
                'action': 'custom_logging_example_accessed',
                'details': 'User accessed custom logging example'
            })
        
        return jsonify({
            'message': 'Custom logging example executed',
            'audit_logged': True
        })
    
    # Example of performance monitoring
    @app.route('/performance-test')
    def performance_test():
        """Test endpoint for performance monitoring."""
        perf_middleware = manager.get_middleware(PerformanceMiddleware)
        
        # Simulate some work
        import random
        work_duration = random.uniform(0.1, 1.0)
        time.sleep(work_duration)
        
        if perf_middleware:
            # Get current performance metrics
            metrics = perf_middleware.get_performance_metrics()
            slow_endpoints = perf_middleware.get_slow_endpoints(threshold=0.5)
            system_metrics = perf_middleware.get_system_metrics()
            
            return jsonify({
                'message': 'Performance test completed',
                'work_duration': work_duration,
                'system_metrics': system_metrics,
                'slow_endpoints': slow_endpoints
            })
        
        return jsonify({'message': 'Performance test completed'})
    
    return app


def demonstrate_middleware_features():
    """Demonstrate various middleware features."""
    app = create_example_app()
    
    print("Middleware System Demo")
    print("=" * 50)
    
    # Test public endpoint
    print("\n1. Testing public endpoint:")
    with app.test_client() as client:
        response = client.get('/public')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        print(f"Headers: {dict(response.headers)}")
    
    # Test protected endpoint (without auth)
    print("\n2. Testing protected endpoint (no auth):")
    with app.test_client() as client:
        response = client.get('/protected')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
    
    # Test metrics endpoint
    print("\n3. Testing metrics endpoint:")
    with app.test_client() as client:
        response = client.get('/metrics')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
    
    # Test health endpoint
    print("\n4. Testing health endpoint:")
    with app.test_client() as client:
        response = client.get('/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
    
    # Test slow endpoint
    print("\n5. Testing slow endpoint:")
    with app.test_client() as client:
        response = client.get('/slow')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        print(f"Response Time Header: {response.headers.get('X-Response-Time')}")
    
    # Test rate limited endpoint
    print("\n6. Testing rate limited endpoint:")
    with app.test_client() as client:
        response = client.get('/rate-limited')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        print(f"Rate Limit Headers: {response.headers.get('X-RateLimit-Limit')}")


def demonstrate_middleware_configuration():
    """Demonstrate middleware configuration."""
    print("\nMiddleware Configuration Demo")
    print("=" * 50)
    
    from app.middleware.config import MiddlewareConfig
    
    config = MiddlewareConfig()
    
    print("\nCORS Configuration:")
    print(config.get_cors_config())
    
    print("\nRate Limiting Configuration:")
    print(config.get_rate_limit_config())
    
    print("\nSecurity Configuration:")
    security_config = config.get_security_config()
    print(f"Security Headers: {security_config['headers']}")
    print(f"Suspicious Patterns Count: {len(security_config['suspicious_patterns'])}")
    
    print("\nLogging Configuration:")
    print(config.get_logging_config())
    
    print("\nPerformance Configuration:")
    print(config.get_performance_config())


def demonstrate_custom_middleware():
    """Demonstrate creating custom middleware."""
    print("\nCustom Middleware Demo")
    print("=" * 50)
    
    from app.middleware.base_middleware import BaseMiddleware
    from flask import request, g
    
    class CustomAuditMiddleware(BaseMiddleware):
        """Custom middleware for audit logging."""
        
        def before_request(self):
            """Log request details for audit."""
            g.audit_data = {
                'timestamp': request.headers.get('X-Request-ID', 'unknown'),
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr
            }
            return None
        
        def after_request(self, response):
            """Log response details for audit."""
            if hasattr(g, 'audit_data'):
                g.audit_data['status_code'] = response.status_code
                g.audit_data['response_size'] = response.content_length or 0
                
                # Log audit data
                print(f"Audit Log: {g.audit_data}")
            
            return response
    
    # Create Flask app with custom middleware
    app = Flask(__name__)
    middleware_ext = MiddlewareExtension(app)
    manager = middleware_ext.get_manager()
    
    # Add custom middleware
    custom_middleware = CustomAuditMiddleware(app)
    manager.add_middleware(custom_middleware)
    
    @app.route('/custom-audit')
    def custom_audit_endpoint():
        return jsonify({'message': 'Custom audit middleware active'})
    
    print("Custom middleware added to the stack")
    print(f"Middleware stack: {[m.__class__.__name__ for m in manager.get_all_middleware()]}")


if __name__ == '__main__':
    # Run demonstrations
    demonstrate_middleware_features()
    demonstrate_middleware_configuration()
    demonstrate_custom_middleware()
    
    print("\n" + "=" * 50)
    print("Middleware system demonstration completed!")
    print("=" * 50)
