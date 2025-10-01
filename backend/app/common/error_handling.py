from flask import jsonify, current_app
from marshmallow import ValidationError
import traceback


# Custom Exceptions
class ResourceNotFoundError(Exception):
    """
    Exception raised when a requested resource is not found.
    """
    def __init__(self, resource_name):
        self.resource_name = resource_name
        super().__init__(f"{resource_name} not found")


class QueryValidationError(Exception):
    """
    Exception raised for query validation errors.
    """
    pass


# Error Handlers
def register_error_handlers(app):
    """
    Register error handlers for the Flask application.
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        """
        Handle validation errors from Marshmallow.
        """
        return jsonify({
            'error': 'Validation error',
            'details': err.messages
        }), 400

    @app.errorhandler(ResourceNotFoundError)
    def handle_resource_not_found_error(err):
        """
        Handle ResourceNotFoundError exceptions.
        """
        return jsonify({
            'error': 'Resource not found',
            'details': str(err)
        }), 404

    @app.errorhandler(QueryValidationError)
    def handle_query_validation_error(err):
        """
        Handle QueryValidationError exceptions.
        """
        return jsonify({
            'error': 'Query validation error',
            'details': str(err)
        }), 400

    @app.errorhandler(404)
    def handle_not_found_error(err):
        """
        Handle 404 Not Found errors.
        """
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def handle_internal_server_error(err):
        """
        Handle unexpected server errors.
        """
        tb = traceback.format_exc()  # Get the full traceback
        current_app.logger.error(f"Internal server error: {err}\n{tb}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

    @app.errorhandler(Exception)
    def handle_generic_exception(err):
        """
        Handle all other uncaught exceptions.
        """
        tb = traceback.format_exc()  # Get the full traceback
        current_app.logger.error(f"Unhandled exception: {err}\n{tb}")  # Log the error and traceback
        return jsonify({'error': 'An unexpected error occurred'}), 500