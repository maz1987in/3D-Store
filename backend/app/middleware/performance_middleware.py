"""
Performance Middleware

Handles performance monitoring, metrics collection, and optimization.
"""

import time
import psutil
from typing import Optional, Dict, Any
from flask import request, g, current_app

from .base_middleware import BaseMiddleware


class PerformanceMiddleware(BaseMiddleware):
    """Middleware for performance monitoring and optimization."""
    
    def __init__(self, app=None):
        self.metrics = {}
        super().__init__(app)
    
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Start performance monitoring before request."""
        # Record request start time
        g.request_start_time = time.time()
        g.request_start_cpu = psutil.cpu_percent()
        g.request_start_memory = psutil.virtual_memory().percent
        
        return None
    
    def after_request(self, response):
        """Record performance metrics after request."""
        # Calculate performance metrics
        duration = time.time() - g.request_start_time
        cpu_usage = psutil.cpu_percent() - g.request_start_cpu
        memory_usage = psutil.virtual_memory().percent - g.request_start_memory
        
        # Record metrics
        self._record_metrics({
            'path': request.path,
            'method': request.method,
            'status_code': response.status_code,
            'duration': duration,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'content_length': response.content_length or 0
        })
        
        # Add performance headers
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        response.headers['X-CPU-Usage'] = f"{cpu_usage:.2f}%"
        response.headers['X-Memory-Usage'] = f"{memory_usage:.2f}%"
        
        return response
    
    def _record_metrics(self, metrics: Dict[str, Any]):
        """Record performance metrics."""
        path = metrics['path']
        
        if path not in self.metrics:
            self.metrics[path] = {
                'count': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'min_duration': float('inf'),
                'max_duration': 0,
                'total_cpu': 0,
                'avg_cpu': 0,
                'total_memory': 0,
                'avg_memory': 0,
                'error_count': 0
            }
        
        path_metrics = self.metrics[path]
        path_metrics['count'] += 1
        path_metrics['total_duration'] += metrics['duration']
        path_metrics['avg_duration'] = path_metrics['total_duration'] / path_metrics['count']
        path_metrics['min_duration'] = min(path_metrics['min_duration'], metrics['duration'])
        path_metrics['max_duration'] = max(path_metrics['max_duration'], metrics['duration'])
        
        path_metrics['total_cpu'] += metrics['cpu_usage']
        path_metrics['avg_cpu'] = path_metrics['total_cpu'] / path_metrics['count']
        
        path_metrics['total_memory'] += metrics['memory_usage']
        path_metrics['avg_memory'] = path_metrics['total_memory'] / path_metrics['count']
        
        if metrics['status_code'] >= 400:
            path_metrics['error_count'] += 1
        
        # Log slow requests
        if metrics['duration'] > 5.0:  # 5 seconds threshold
            current_app.logger.warning(
                f"Slow request detected: {metrics['path']} took {metrics['duration']:.3f}s"
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    def get_slow_endpoints(self, threshold: float = 1.0) -> Dict[str, Any]:
        """Get endpoints that are slower than threshold."""
        slow_endpoints = {}
        
        for path, metrics in self.metrics.items():
            if metrics['avg_duration'] > threshold:
                slow_endpoints[path] = metrics
        
        return slow_endpoints
    
    def get_error_endpoints(self) -> Dict[str, Any]:
        """Get endpoints with errors."""
        error_endpoints = {}
        
        for path, metrics in self.metrics.items():
            if metrics['error_count'] > 0:
                error_endpoints[path] = metrics
        
        return error_endpoints
    
    def reset_metrics(self):
        """Reset all performance metrics."""
        self.metrics.clear()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
