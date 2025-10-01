# Exceptions package for custom error handling
from .base import (
    APIException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    BusinessLogicException,
    DatabaseException,
    ExternalServiceException,
    FileUploadException,
    PaymentException,
    PrintJobException,
    MaterialException,
    PrinterException,
    InventoryException
)

from .printing import (
    PrintJobNotFoundError,
    PrintJobInvalidStatusError,
    PrintJobAlreadyStartedError,
    PrintJobCannotBeCancelledError,
    MaterialNotFoundError,
    MaterialInsufficientError,
    MaterialIncompatibleError,
    PrinterNotFoundError,
    PrinterUnavailableError,
    PrinterMaintenanceError,
    PrinterCapacityExceededError,
    ModelFileException,
    ModelFileInvalidError,
    ModelFileUnsupportedError,
    ModelFileTooLargeError,
    PrintSettingsException,
    PrintSettingsNotFoundError,
    PrintSettingsInvalidError,
    PackagingException,
    PackagingNotFoundError,
    PackagingUnavailableError
)

from .handlers import register_error_handlers
from .context import (
    handle_database_errors,
    handle_business_logic_errors,
    handle_errors,
    handle_database_operation,
    handle_business_operation,
    safe_execute,
    ErrorContext,
    validate_required_fields,
    validate_field_types
)

__all__ = [
    # Base exceptions
    'APIException',
    'ValidationException',
    'AuthenticationException',
    'AuthorizationException',
    'ResourceNotFoundException',
    'BusinessLogicException',
    'DatabaseException',
    'ExternalServiceException',
    'FileUploadException',
    'PaymentException',
    'PrintJobException',
    'MaterialException',
    'PrinterException',
    'InventoryException',
    
    # 3D Printing specific exceptions
    'PrintJobNotFoundError',
    'PrintJobInvalidStatusError',
    'PrintJobAlreadyStartedError',
    'PrintJobCannotBeCancelledError',
    'MaterialNotFoundError',
    'MaterialInsufficientError',
    'MaterialIncompatibleError',
    'PrinterNotFoundError',
    'PrinterUnavailableError',
    'PrinterMaintenanceError',
    'PrinterCapacityExceededError',
    'ModelFileException',
    'ModelFileInvalidError',
    'ModelFileUnsupportedError',
    'ModelFileTooLargeError',
    'PrintSettingsException',
    'PrintSettingsNotFoundError',
    'PrintSettingsInvalidError',
    'PackagingException',
    'PackagingNotFoundError',
    'PackagingUnavailableError',
    
    # Error handlers and utilities
    'register_error_handlers',
    'handle_database_errors',
    'handle_business_logic_errors',
    'handle_errors',
    'handle_database_operation',
    'handle_business_operation',
    'safe_execute',
    'ErrorContext',
    'validate_required_fields',
    'validate_field_types'
]
