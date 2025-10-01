from functools import wraps
from flask import request, jsonify, g
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

def validate_json(schema_class):
    """
    Decorator to validate JSON request data using Marshmallow schemas
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Request must be JSON',
                        'errors': {'content_type': 'Content-Type must be application/json'}
                    }), 400
                
                if not request.json:
                    return jsonify({
                        'success': False,
                        'message': 'Request body cannot be empty',
                        'errors': {'body': 'Request body is required'}
                    }), 400
                
                schema = schema_class()
                validated_data = schema.load(request.json)
                
                # Store validated data in g for use in the route handler
                g.validated_data = validated_data
                
                return f(validated_data, *args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Validation error in {f.__name__}: {e.messages}")
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': e.messages
                }), 400
            except Exception as e:
                logger.error(f"Unexpected error in validation decorator for {f.__name__}: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Internal validation error',
                    'errors': {'internal': 'An unexpected error occurred during validation'}
                }), 500
                
        return decorated_function
    return decorator

def validate_form_data(schema_class):
    """
    Decorator to validate form data using Marshmallow schemas
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Convert form data to dict
                form_data = request.form.to_dict()
                
                # Handle file uploads separately
                files_data = {}
                for key, file in request.files.items():
                    files_data[key] = file
                
                # Merge form data and files
                data = {**form_data, **files_data}
                
                if not data:
                    return jsonify({
                        'success': False,
                        'message': 'Form data cannot be empty',
                        'errors': {'form': 'Form data is required'}
                    }), 400
                
                schema = schema_class()
                validated_data = schema.load(data)
                
                # Store validated data in g for use in the route handler
                g.validated_data = validated_data
                
                return f(validated_data, *args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Form validation error in {f.__name__}: {e.messages}")
                return jsonify({
                    'success': False,
                    'message': 'Form validation failed',
                    'errors': e.messages
                }), 400
            except Exception as e:
                logger.error(f"Unexpected error in form validation decorator for {f.__name__}: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Internal form validation error',
                    'errors': {'internal': 'An unexpected error occurred during form validation'}
                }), 500
                
        return decorated_function
    return decorator

def validate_query_params(schema_class):
    """
    Decorator to validate query parameters using Marshmallow schemas
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                query_params = request.args.to_dict()
                
                schema = schema_class()
                validated_data = schema.load(query_params)
                
                # Store validated data in g for use in the route handler
                g.validated_query = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Query parameter validation error in {f.__name__}: {e.messages}")
                return jsonify({
                    'success': False,
                    'message': 'Query parameter validation failed',
                    'errors': e.messages
                }), 400
            except Exception as e:
                logger.error(f"Unexpected error in query validation decorator for {f.__name__}: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Internal query validation error',
                    'errors': {'internal': 'An unexpected error occurred during query validation'}
                }), 500
                
        return decorated_function
    return decorator
