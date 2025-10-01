"""
Context managers and decorators for error handling.
Provides convenient ways to handle errors in business logic.
"""

import functools
import logging
from typing import Callable, Any, Optional, Type, Union, Tuple
from contextlib import contextmanager

from .base import APIException, DatabaseException, BusinessLogicException

logger = logging.getLogger(__name__)

@contextmanager
def handle_database_errors(operation: str = "database operation"):
    """
    Context manager for handling database errors.
    
    Args:
        operation: Description of the database operation being performed
    """
    try:
        yield
    except Exception as e:
        logger.error(f"Database error during {operation}: {str(e)}")
        raise DatabaseException(
            message=f"Database operation failed: {operation}",
            operation=operation,
            details={'original_error': str(e)}
        )

@contextmanager
def handle_business_logic_errors(operation: str = "business operation"):
    """
    Context manager for handling business logic errors.
    
    Args:
        operation: Description of the business operation being performed
    """
    try:
        yield
    except APIException:
        # Re-raise API exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Business logic error during {operation}: {str(e)}")
        raise BusinessLogicException(
            message=f"Business operation failed: {operation}",
            rule=operation,
            details={'original_error': str(e)}
        )

def handle_errors(
    default_message: str = "Operation failed",
    default_status_code: int = 500,
    default_error_code: str = "OPERATION_ERROR",
    log_errors: bool = True,
    reraise_api_exceptions: bool = True
):
    """
    Decorator for handling errors in functions.
    
    Args:
        default_message: Default error message
        default_status_code: Default HTTP status code
        default_error_code: Default error code
        log_errors: Whether to log errors
        reraise_api_exceptions: Whether to re-raise API exceptions
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except APIException as e:
                if reraise_api_exceptions:
                    raise
                if log_errors:
                    logger.error(f"API Exception in {func.__name__}: {e.message}")
                return None
            except Exception as e:
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                
                raise APIException(
                    message=default_message,
                    status_code=default_status_code,
                    error_code=default_error_code,
                    details={'function': func.__name__, 'original_error': str(e)}
                )
        return wrapper
    return decorator

def handle_database_operation(operation: str = "database operation"):
    """
    Decorator specifically for database operations.
    
    Args:
        operation: Description of the database operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with handle_database_errors(operation):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_business_operation(operation: str = "business operation"):
    """
    Decorator specifically for business logic operations.
    
    Args:
        operation: Description of the business operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with handle_business_logic_errors(operation):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def safe_execute(
    func: Callable,
    default_return: Any = None,
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    log_errors: bool = True
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        default_return: Value to return if function fails
        exception_types: Types of exceptions to catch
        log_errors: Whether to log errors
    
    Returns:
        Function result or default_return if error occurs
    """
    try:
        return func()
    except exception_types as e:
        if log_errors:
            logger.error(f"Error in safe_execute: {str(e)}")
        return default_return

class ErrorContext:
    """
    Context class for managing error handling state.
    """
    
    def __init__(self, operation: str = "operation"):
        self.operation = operation
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: str, details: Optional[dict] = None):
        """Add an error to the context."""
        error_info = {'message': error}
        if details:
            error_info['details'] = details
        self.errors.append(error_info)
    
    def add_warning(self, warning: str, details: Optional[dict] = None):
        """Add a warning to the context."""
        warning_info = {'message': warning}
        if details:
            warning_info['details'] = details
        self.warnings.append(warning_info)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> dict:
        """Get a summary of errors and warnings."""
        return {
            'operation': self.operation,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
    
    def raise_if_errors(self, exception_class: Type[APIException] = BusinessLogicException):
        """Raise an exception if there are errors."""
        if self.has_errors():
            raise exception_class(
                message=f"Operation failed: {self.operation}",
                details=self.get_error_summary()
            )

def validate_required_fields(data: dict, required_fields: list, context: Optional[ErrorContext] = None) -> bool:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        context: Optional error context
    
    Returns:
        True if all required fields are present, False otherwise
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        if context:
            context.add_error(error_msg, {'missing_fields': missing_fields})
        else:
            logger.warning(error_msg)
        return False
    
    return True

def validate_field_types(data: dict, field_types: dict, context: Optional[ErrorContext] = None) -> bool:
    """
    Validate that fields have the correct types.
    
    Args:
        data: Data dictionary to validate
        field_types: Dictionary mapping field names to expected types
        context: Optional error context
    
    Returns:
        True if all fields have correct types, False otherwise
    """
    type_errors = []
    
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            type_errors.append(f"{field} should be {expected_type.__name__}, got {type(data[field]).__name__}")
    
    if type_errors:
        error_msg = f"Type validation errors: {'; '.join(type_errors)}"
        if context:
            context.add_error(error_msg, {'type_errors': type_errors})
        else:
            logger.warning(error_msg)
        return False
    
    return True
