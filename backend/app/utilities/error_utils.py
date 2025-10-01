from functools import wraps
from flask import current_app

from app.common.error_handling import ResourceNotFoundError
import traceback

def handle_errors(resource_name):
    """
    Decorator to handle errors in service methods.
    :param resource_name: The name of the resource being handled.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ResourceNotFoundError as e:
                current_app.logger.warning(e)
                return {'error': f'{resource_name} not found'}, 404
            except Exception as e:
                tb = traceback.format_exc()  # Get the full traceback
                current_app.logger.error(f"{e}\n{tb}")
                #current_app.logger.error(e)
                return {'error': 'An unexpected error occurred'}, 500
        return wrapper
    return decorator