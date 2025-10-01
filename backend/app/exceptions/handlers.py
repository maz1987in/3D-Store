"""
Error handlers for the Flask application.
Provides centralized error handling and consistent API responses.
"""

from flask import request, jsonify, current_app
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from .base import APIException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register all error handlers with the Flask application."""
    
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """Handle custom API exceptions."""
        logger.error(f"API Exception: {error.error_code} - {error.message}")
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Marshmallow validation errors."""
        logger.warning(f"Validation Error: {error.messages}")
        return jsonify({
            'error_code': 'VALIDATION_ERROR',
            'message': 'Validation failed',
            'status_code': 422,
            'details': {
                'validation_errors': error.messages
            }
        }), 422
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity constraint violations."""
        logger.error(f"Database Integrity Error: {str(error)}")
        return jsonify({
            'error_code': 'DATABASE_INTEGRITY_ERROR',
            'message': 'Database constraint violation',
            'status_code': 400,
            'details': {
                'constraint': str(error.orig) if hasattr(error, 'orig') else str(error)
            }
        }), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        """Handle general SQLAlchemy errors."""
        logger.error(f"SQLAlchemy Error: {str(error)}")
        return jsonify({
            'error_code': 'DATABASE_ERROR',
            'message': 'Database operation failed',
            'status_code': 500,
            'details': {
                'error_type': type(error).__name__
            }
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle Werkzeug HTTP exceptions."""
        logger.warning(f"HTTP Exception: {error.code} - {error.description}")
        return jsonify({
            'error_code': 'HTTP_ERROR',
            'message': error.description,
            'status_code': error.code
        }), error.code
    
    @app.errorhandler(FileNotFoundError)
    def handle_file_not_found(error):
        """Handle file not found errors."""
        logger.warning(f"File Not Found: {str(error)}")
        return jsonify({
            'error_code': 'FILE_NOT_FOUND',
            'message': 'File not found',
            'status_code': 404,
            'details': {
                'file_path': str(error)
            }
        }), 404
    
    @app.errorhandler(PermissionError)
    def handle_permission_error(error):
        """Handle permission errors."""
        logger.warning(f"Permission Error: {str(error)}")
        return jsonify({
            'error_code': 'PERMISSION_ERROR',
            'message': 'Insufficient permissions',
            'status_code': 403
        }), 403
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle value errors."""
        logger.warning(f"Value Error: {str(error)}")
        return jsonify({
            'error_code': 'VALUE_ERROR',
            'message': 'Invalid value provided',
            'status_code': 400,
            'details': {
                'error': str(error)
            }
        }), 400
    
    @app.errorhandler(TypeError)
    def handle_type_error(error):
        """Handle type errors."""
        logger.warning(f"Type Error: {str(error)}")
        return jsonify({
            'error_code': 'TYPE_ERROR',
            'message': 'Invalid data type',
            'status_code': 400,
            'details': {
                'error': str(error)
            }
        }), 400
    
    @app.errorhandler(KeyError)
    def handle_key_error(error):
        """Handle key errors."""
        logger.warning(f"Key Error: {str(error)}")
        return jsonify({
            'error_code': 'KEY_ERROR',
            'message': 'Required key missing',
            'status_code': 400,
            'details': {
                'missing_key': str(error)
            }
        }), 400
    
    @app.errorhandler(AttributeError)
    def handle_attribute_error(error):
        """Handle attribute errors."""
        logger.warning(f"Attribute Error: {str(error)}")
        return jsonify({
            'error_code': 'ATTRIBUTE_ERROR',
            'message': 'Invalid attribute access',
            'status_code': 400,
            'details': {
                'error': str(error)
            }
        }), 400
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all other unhandled exceptions."""
        logger.error(f"Unhandled Exception: {type(error).__name__} - {str(error)}")
        
        # In development, return detailed error information
        if current_app.config.get('DEBUG', False):
            return jsonify({
                'error_code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'status_code': 500,
                'details': {
                    'error_type': type(error).__name__,
                    'error_message': str(error),
                    'debug_info': True
                }
            }), 500
        
        # In production, return generic error
        return jsonify({
            'error_code': 'INTERNAL_ERROR',
            'message': 'Internal server error',
            'status_code': 500
        }), 500

def log_request_error(error, request_data=None):
    """Log request-related errors with context."""
    error_context = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'request_method': request.method,
        'request_url': request.url,
        'request_headers': dict(request.headers),
        'user_agent': request.headers.get('User-Agent'),
        'remote_addr': request.remote_addr
    }
    
    if request_data:
        error_context['request_data'] = request_data
    
    logger.error(f"Request Error: {error_context}")

def create_error_response(error_code, message, status_code, details=None):
    """Create a standardized error response."""
    response = {
        'error_code': error_code,
        'message': message,
        'status_code': status_code
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code
