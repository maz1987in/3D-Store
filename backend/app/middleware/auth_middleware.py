"""
Authentication Middleware

Handles JWT token validation, user authentication, and authorization.
"""

import jwt
from typing import Optional, Dict, Any
from flask import request, g, jsonify, current_app
from functools import wraps

from .base_middleware import BaseMiddleware
from app.users.service import UserService
from app.exceptions.base import AuthenticationException, AuthorizationException
from config import SecretKey

SECRET_KEY = SecretKey().SECRET_KEY


class AuthMiddleware(BaseMiddleware):
    """Middleware for handling authentication and authorization."""
    
    def __init__(self, app=None):
        self.user_service = UserService()
        super().__init__(app)
    
    def before_request(self) -> Optional[Dict[str, Any]]:
        """Process authentication before request."""
        # Skip authentication for certain paths
        if self._should_skip_auth():
            return None
        
        # Extract token from request
        token = self._extract_token()
        if not token:
            return self._create_error_response('Token is required', 401)
        
        # Validate token and get user
        try:
            user_data = self._validate_token(token)
            user = self._get_user(user_data['id'])
            
            if not user:
                return self._create_error_response('User not found', 401)
            
            # Set user in Flask g object
            g.user = user
            g.user_id = user['id']
            g.user_roles = self._get_user_roles(user['id'])
            
            # Log authentication success
            self._log_auth_success(user['id'], request.path)
            
        except jwt.ExpiredSignatureError:
            return self._create_error_response('Token has expired', 401)
        except jwt.InvalidTokenError:
            return self._create_error_response('Invalid token', 401)
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return self._create_error_response('Authentication failed', 401)
        
        return None
    
    def after_request(self, response):
        """Process response after authentication."""
        return response
    
    def _should_skip_auth(self) -> bool:
        """Check if authentication should be skipped for this request."""
        skip_paths = [
            '/health',
            '/login',
            '/signup',
            '/email',
            '/api/docs',
            '/static',
            '/favicon.ico'
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _extract_token(self) -> Optional[str]:
        """Extract JWT token from request headers or query parameters."""
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # Check x-access-tokens header (legacy)
        token = request.headers.get('x-access-tokens')
        if token:
            return token
        
        # Check query parameter
        return request.args.get('token')
    
    def _validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return payload."""
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    def _get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            user, status = self.user_service.get_user_by_id(user_id)
            return user if status == 200 else None
        except Exception:
            return None
    
    def _get_user_roles(self, user_id: str) -> list:
        """Get user roles."""
        try:
            return self.user_service.get_user_roles_ids(user_id)
        except Exception:
            return []
    
    def _create_error_response(self, message: str, status_code: int) -> Dict[str, Any]:
        """Create error response."""
        return {
            'error': True,
            'message': message,
            'status_code': status_code
        }
    
    def _log_auth_success(self, user_id: str, path: str):
        """Log successful authentication."""
        current_app.logger.info(f"User {user_id} authenticated for {path}")


def require_auth(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': True, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_roles(*roles):
    """Decorator to require specific roles for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'error': True, 'message': 'Authentication required'}), 401
            
            user_roles = getattr(g, 'user_roles', [])
            if not any(role in user_roles for role in roles):
                return jsonify({'error': True, 'message': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_permissions(*permissions):
    """Decorator to require specific permissions for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'error': True, 'message': 'Authentication required'}), 401
            
            user_roles = getattr(g, 'user_roles', [])
            user_service = UserService()
            
            try:
                has_permission = user_service.check_role_permission(list(permissions), user_roles)
                if not has_permission:
                    return jsonify({'error': True, 'message': 'Insufficient permissions'}), 403
            except Exception as e:
                current_app.logger.error(f"Permission check error: {str(e)}")
                return jsonify({'error': True, 'message': 'Permission check failed'}), 500
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
