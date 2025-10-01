"""
Monitoring System Demo

This script demonstrates the comprehensive monitoring and observability system
including logging, metrics, health monitoring, performance tracking, error tracking,
alerting, and insights collection.
"""

import os
import time
import random
import requests
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

# Set up environment for demo
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['LOG_FORMAT'] = 'json'
os.environ['LOG_CONSOLE_ENABLED'] = 'True'
os.environ['LOG_FILE_ENABLED'] = 'True'

from app.monitoring.extension import MonitoringExtension
from app.monitoring.logging_config import get_logger, log_access, log_performance, log_audit
from app.monitoring.metrics_collector import get_metrics_collector, increment_counter, set_gauge, record_timer
from app.monitoring.health_monitor import get_health_monitor, HealthCheck, HealthStatus
from app.monitoring.performance_tracker import get_performance_tracker, time_function
from app.monitoring.error_tracker import get_error_tracker, track_error, track_custom_error, ErrorSeverity, ErrorCategory
from app.monitoring.alerting import get_alert_manager, send_alert, AlertSeverity, AlertChannel
from app.monitoring.insights import get_insights_collector, add_insight, add_business_metric

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo_secret_key'
app.config['DATABASE_URL'] = 'sqlite:///demo.db'

# Initialize monitoring extension
monitoring = MonitoringExtension(app)

# Get monitoring components
logger = get_logger('monitoring_demo')
metrics = get_metrics_collector()
health = get_health_monitor()
performance = get_performance_tracker()
errors = get_error_tracker()
alerts = get_alert_manager()
insights = get_insights_collector()

# Demo data
demo_users = [
    {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
    {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
    {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
]

demo_products = [
    {'id': 1, 'name': '3D Printed Phone Case', 'price': 25.99},
    {'id': 2, 'name': 'Custom Keychain', 'price': 5.99},
    {'id': 3, 'name': 'Desk Organizer', 'price': 45.99}
]

# Demo routes
@app.route('/')
def home():
    """Home page with monitoring demo links."""
    return jsonify({
        'message': 'Monitoring System Demo',
        'endpoints': {
            'users': '/users',
            'products': '/products',
            'orders': '/orders',
            'health': '/health',
            'metrics': '/monitoring/metrics',
            'performance': '/monitoring/performance',
            'errors': '/monitoring/errors',
            'alerts': '/monitoring/alerts',
            'insights': '/monitoring/insights',
            'dashboard': '/monitoring/dashboard'
        }
    })

@app.route('/users')
def get_users():
    """Get users with monitoring."""
    start_time = time.time()
    
    # Log access
    log_access({
        'method': 'GET',
        'path': '/users',
        'status_code': 200,
        'response_time': 0
    })
    
    # Increment counter
    increment_counter('api_requests', 1, {'endpoint': '/users'})
    
    # Simulate some processing time
    time.sleep(random.uniform(0.1, 0.5))
    
    # Record performance
    duration = time.time() - start_time
    record_timer('api_response_time', duration, {'endpoint': '/users'})
    
    # Add business metric
    add_business_metric('users_accessed', len(demo_users), 'engagement')
    
    # Add insight
    add_insight(
        category='user_activity',
        title='Users Accessed',
        description=f'{len(demo_users)} users were accessed',
        value=len(demo_users),
        trend='stable',
        confidence=1.0
    )
    
    return jsonify({
        'users': demo_users,
        'count': len(demo_users),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/products')
def get_products():
    """Get products with monitoring."""
    start_time = time.time()
    
    # Log access
    log_access({
        'method': 'GET',
        'path': '/products',
        'status_code': 200,
        'response_time': 0
    })
    
    # Increment counter
    increment_counter('api_requests', 1, {'endpoint': '/products'})
    
    # Simulate some processing time
    time.sleep(random.uniform(0.1, 0.3))
    
    # Record performance
    duration = time.time() - start_time
    record_timer('api_response_time', duration, {'endpoint': '/products'})
    
    # Add business metric
    total_value = sum(product['price'] for product in demo_products)
    add_business_metric('products_value', total_value, 'financial')
    
    return jsonify({
        'products': demo_products,
        'count': len(demo_products),
        'total_value': total_value,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/orders')
def get_orders():
    """Get orders with monitoring and potential errors."""
    start_time = time.time()
    
    # Simulate random errors
    if random.random() < 0.1:  # 10% chance of error
        try:
            raise Exception("Database connection timeout")
        except Exception as e:
            # Track error
            error_id = track_error(e, ErrorSeverity.MEDIUM, ErrorCategory.DATABASE)
            
            # Send alert
            send_alert(
                'Database Error',
                f'Database connection timeout occurred: {str(e)}',
                AlertSeverity.WARNING,
                [AlertChannel.LOG]
            )
            
            return jsonify({
                'error': 'Database connection timeout',
                'error_id': error_id
            }), 500
    
    # Log access
    log_access({
        'method': 'GET',
        'path': '/orders',
        'status_code': 200,
        'response_time': 0
    })
    
    # Increment counter
    increment_counter('api_requests', 1, {'endpoint': '/orders'})
    
    # Simulate some processing time
    time.sleep(random.uniform(0.2, 0.8))
    
    # Record performance
    duration = time.time() - start_time
    record_timer('api_response_time', duration, {'endpoint': '/orders'})
    
    # Generate demo orders
    orders = []
    for i in range(random.randint(1, 5)):
        orders.append({
            'id': i + 1,
            'user_id': random.randint(1, 3),
            'product_id': random.randint(1, 3),
            'quantity': random.randint(1, 3),
            'total': round(random.uniform(10, 100), 2),
            'status': random.choice(['pending', 'processing', 'completed']),
            'created_at': datetime.utcnow().isoformat()
        })
    
    # Add business metrics
    total_orders = len(orders)
    total_revenue = sum(order['total'] for order in orders)
    add_business_metric('orders_count', total_orders, 'sales')
    add_business_metric('revenue', total_revenue, 'financial')
    
    # Add insight
    add_insight(
        category='sales',
        title='Order Volume',
        description=f'{total_orders} orders generated',
        value=total_orders,
        trend='up' if total_orders > 3 else 'stable',
        confidence=0.9
    )
    
    return jsonify({
        'orders': orders,
        'count': total_orders,
        'total_revenue': total_revenue,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/simulate-load')
def simulate_load():
    """Simulate high load for performance monitoring."""
    start_time = time.time()
    
    # Simulate high CPU usage
    for i in range(1000000):
        _ = i * i
    
    # Simulate memory usage
    data = [random.random() for _ in range(10000)]
    
    # Record performance
    duration = time.time() - start_time
    record_timer('load_simulation', duration)
    
    # Set gauge
    set_gauge('simulated_load', duration)
    
    # Add insight
    add_insight(
        category='performance',
        title='Load Simulation',
        description=f'Load simulation completed in {duration:.3f}s',
        value=duration,
        trend='stable',
        confidence=1.0
    )
    
    return jsonify({
        'message': 'Load simulation completed',
        'duration': duration,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/trigger-error')
def trigger_error():
    """Trigger various types of errors for demonstration."""
    error_type = request.args.get('type', 'generic')
    
    if error_type == 'validation':
        track_custom_error(
            'ValidationError',
            'Invalid input data provided',
            ErrorSeverity.LOW,
            ErrorCategory.VALIDATION,
            {'field': 'email', 'value': 'invalid-email'}
        )
        return jsonify({'error': 'Validation error triggered'}), 400
    
    elif error_type == 'database':
        try:
            raise Exception("Database connection failed")
        except Exception as e:
            track_error(e, ErrorSeverity.HIGH, ErrorCategory.DATABASE)
            return jsonify({'error': 'Database error triggered'}), 500
    
    elif error_type == 'external':
        track_custom_error(
            'ExternalServiceError',
            'Payment gateway unavailable',
            ErrorSeverity.MEDIUM,
            ErrorCategory.EXTERNAL_SERVICE,
            {'service': 'payment_gateway', 'endpoint': '/process_payment'}
        )
        return jsonify({'error': 'External service error triggered'}), 502
    
    else:
        try:
            raise Exception("Generic application error")
        except Exception as e:
            track_error(e, ErrorSeverity.MEDIUM, ErrorCategory.INTERNAL)
            return jsonify({'error': 'Generic error triggered'}), 500

@app.route('/send-alert')
def send_alert_demo():
    """Send a demo alert."""
    alert_type = request.args.get('type', 'info')
    
    if alert_type == 'critical':
        send_alert(
            'Critical System Alert',
            'System is experiencing critical issues',
            AlertSeverity.CRITICAL,
            [AlertChannel.LOG]
        )
    elif alert_type == 'warning':
        send_alert(
            'Warning Alert',
            'System performance is degraded',
            AlertSeverity.WARNING,
            [AlertChannel.LOG]
        )
    else:
        send_alert(
            'Info Alert',
            'System is operating normally',
            AlertSeverity.INFO,
            [AlertChannel.LOG]
        )
    
    return jsonify({
        'message': f'{alert_type} alert sent',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/generate-insights')
def generate_insights():
    """Generate demo insights."""
    # Generate various insights
    insights_data = [
        {
            'category': 'performance',
            'title': 'High Response Time',
            'description': 'Average response time is 2.5s',
            'value': 2.5,
            'trend': 'up',
            'confidence': 0.8
        },
        {
            'category': 'user_activity',
            'title': 'User Engagement',
            'description': 'User engagement score is 0.85',
            'value': 0.85,
            'trend': 'up',
            'confidence': 0.9
        },
        {
            'category': 'business',
            'title': 'Revenue Growth',
            'description': 'Revenue grew by 15% this month',
            'value': 0.15,
            'trend': 'up',
            'confidence': 0.95
        }
    ]
    
    for insight in insights_data:
        add_insight(**insight)
    
    # Generate business metrics
    business_metrics = [
        ('revenue', 15000.0, 'financial'),
        ('orders', 150, 'sales'),
        ('users', 500, 'growth'),
        ('products', 25, 'inventory')
    ]
    
    for name, value, category in business_metrics:
        add_business_metric(name, value, category)
    
    return jsonify({
        'message': 'Insights and metrics generated',
        'insights_count': len(insights_data),
        'metrics_count': len(business_metrics),
        'timestamp': datetime.utcnow().isoformat()
    })

# Custom health check
def check_demo_service():
    """Custom health check for demo service."""
    return HealthCheck(
        name='demo_service',
        status=HealthStatus.HEALTHY,
        message='Demo service is operational',
        details={'version': '1.0.0', 'uptime': '5 minutes'}
    )

# Register custom health check
health.register_check('demo_service', check_demo_service)

# Performance tracking decorator example
@time_function('demo_processing')
def process_demo_data(data):
    """Process demo data with performance tracking."""
    time.sleep(random.uniform(0.1, 0.3))
    return {'processed': True, 'items': len(data)}

# Demo function with performance tracking
@app.route('/process-data')
def process_data():
    """Process data with performance tracking."""
    data = [{'id': i, 'value': random.random()} for i in range(100)]
    result = process_demo_data(data)
    
    return jsonify({
        'message': 'Data processed successfully',
        'result': result,
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print("Starting Monitoring System Demo...")
    print("Available endpoints:")
    print("- GET / - Home page with links")
    print("- GET /users - Get users with monitoring")
    print("- GET /products - Get products with monitoring")
    print("- GET /orders - Get orders with monitoring (10% error rate)")
    print("- GET /simulate-load - Simulate high load")
    print("- GET /trigger-error?type=validation|database|external|generic - Trigger errors")
    print("- GET /send-alert?type=info|warning|critical - Send alerts")
    print("- GET /generate-insights - Generate demo insights")
    print("- GET /process-data - Process data with performance tracking")
    print("\nMonitoring endpoints:")
    print("- GET /health - Health check")
    print("- GET /monitoring/dashboard - Comprehensive dashboard")
    print("- GET /monitoring/metrics - All metrics")
    print("- GET /monitoring/performance - Performance summary")
    print("- GET /monitoring/errors - Error summary")
    print("- GET /monitoring/alerts - Recent alerts")
    print("- GET /monitoring/insights - Recent insights")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
