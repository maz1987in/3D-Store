# Error Handling System

This package provides a comprehensive error handling system for the 3D Store application, including custom exceptions, error handlers, and utility functions.

## Overview

The error handling system is designed to:
- Provide consistent error responses across all API endpoints
- Handle different types of errors with appropriate HTTP status codes
- Log errors for debugging and monitoring
- Support 3D printing specific error scenarios
- Provide context-aware error handling

## Structure

```
app/exceptions/
├── __init__.py              # Package initialization and exports
├── base.py                  # Base exception classes
├── printing.py              # 3D printing specific exceptions
├── handlers.py              # Flask error handlers
├── context.py               # Error handling utilities and decorators
└── README.md                # This documentation
```

## Base Exception Classes

### APIException
Base class for all API-related errors. Provides:
- Consistent error structure
- Automatic logging
- JSON serialization support

### Specific Exception Types
- `ValidationException` (422) - Input validation errors
- `AuthenticationException` (401) - Authentication failures
- `AuthorizationException` (403) - Permission denied
- `ResourceNotFoundException` (404) - Resource not found
- `BusinessLogicException` (400) - Business rule violations
- `DatabaseException` (500) - Database operation failures
- `ExternalServiceException` (502) - External service failures
- `FileUploadException` (400) - File upload errors
- `PaymentException` (402) - Payment processing errors

## 3D Printing Specific Exceptions

### Print Job Exceptions
- `PrintJobNotFoundError` - Print job not found
- `PrintJobInvalidStatusError` - Invalid status transition
- `PrintJobAlreadyStartedError` - Job already started
- `PrintJobCannotBeCancelledError` - Job cannot be cancelled

### Material Exceptions
- `MaterialNotFoundError` - Material not found
- `MaterialInsufficientError` - Insufficient material
- `MaterialIncompatibleError` - Incompatible material

### Printer Exceptions
- `PrinterNotFoundError` - Printer not found
- `PrinterUnavailableError` - Printer unavailable
- `PrinterMaintenanceError` - Printer in maintenance
- `PrinterCapacityExceededError` - Printer at capacity

### Model File Exceptions
- `ModelFileInvalidError` - Invalid model file
- `ModelFileUnsupportedError` - Unsupported file format
- `ModelFileTooLargeError` - File too large

## Usage Examples

### Basic Exception Usage

```python
from app.exceptions import ResourceNotFoundException, ValidationException

# Raise a resource not found error
raise ResourceNotFoundException(
    message="Product not found",
    resource_type="Product",
    resource_id="123"
)

# Raise a validation error
raise ValidationException(
    message="Invalid product data",
    validation_errors={"name": ["This field is required"]}
)
```

### Using Decorators

```python
from app.exceptions import handle_database_operation, handle_business_operation

@handle_database_operation("get product")
def get_product(product_id):
    # Database operations are automatically wrapped with error handling
    pass

@handle_business_operation("validate order")
def validate_order(order_data):
    # Business logic is automatically wrapped with error handling
    pass
```

### Using Context Managers

```python
from app.exceptions import handle_database_errors, ErrorContext

# Database operations
with handle_database_errors("create product"):
    # Database operations here
    pass

# Error context for complex validation
context = ErrorContext("order validation")
context.add_error("Invalid quantity", {"field": "quantity", "value": -1})
context.raise_if_errors(ValidationException)
```

### Using Error Context

```python
from app.exceptions import ErrorContext, validate_required_fields

def validate_product_data(data):
    context = ErrorContext("product validation")
    
    # Validate required fields
    required_fields = ['name', 'price', 'category_id']
    if not validate_required_fields(data, required_fields, context):
        raise ValidationException(
            message="Product validation failed",
            validation_errors=context.get_error_summary()
        )
    
    # Add custom validations
    if data.get('price', 0) <= 0:
        context.add_error("Price must be greater than 0")
    
    # Raise if there are errors
    context.raise_if_errors(ValidationException)
```

## Error Response Format

All errors are returned in a consistent JSON format:

```json
{
    "error_code": "RESOURCE_NOT_FOUND",
    "message": "Product not found",
    "status_code": 404,
    "details": {
        "resource_type": "Product",
        "resource_id": "123"
    }
}
```

## Error Handler Registration

Error handlers are automatically registered with the Flask application:

```python
from app.exceptions import register_error_handlers

# In your Flask app initialization
register_error_handlers(app)
```

## Best Practices

1. **Use Specific Exceptions**: Use the most specific exception type for your error scenario
2. **Provide Context**: Include relevant details in the exception details
3. **Log Errors**: Exceptions are automatically logged, but add additional context if needed
4. **Use Decorators**: Use the provided decorators for common error handling patterns
5. **Validate Early**: Use the validation utilities to catch errors early
6. **Handle Gracefully**: Use context managers and decorators to handle errors gracefully

## Integration with Existing Code

The error handling system is designed to work with existing code:

1. **Gradual Migration**: You can gradually migrate existing error handling
2. **Backward Compatibility**: Existing error handling continues to work
3. **Enhanced Features**: New features can use the comprehensive error handling
4. **Consistent Responses**: All errors are converted to consistent API responses

## Monitoring and Debugging

- All errors are automatically logged with appropriate log levels
- Error details are included in logs for debugging
- Sentry integration is supported for production monitoring
- Error context provides additional debugging information

## Testing

The error handling system includes utilities for testing:

```python
from app.exceptions import safe_execute

# Safely execute a function that might fail
result = safe_execute(
    lambda: risky_operation(),
    default_return=None,
    exception_types=(ValueError, TypeError)
)
```
