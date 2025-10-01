"""
Base exception classes for the 3D Store application.
Provides a comprehensive error handling system with custom exceptions.
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    """
    Base exception class for all API-related errors.
    Provides consistent error handling across the application.
    """
    status_code = 500
    message = "Internal server error"
    error_code = "INTERNAL_ERROR"
    
    def __init__(
        self, 
        message: Optional[str] = None, 
        status_code: Optional[int] = None, 
        error_code: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__()
        
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
            
        self.payload = payload or {}
        self.details = details or {}
        
        # Log the error
        logger.error(f"API Exception: {self.error_code} - {self.message}")
        if self.details:
            logger.error(f"Error details: {self.details}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        result = {
            'error_code': self.error_code,
            'message': self.message,
            'status_code': self.status_code
        }
        
        if self.payload:
            result['payload'] = self.payload
        if self.details:
            result['details'] = self.details
            
        return result

class ValidationException(APIException):
    """Raised when input validation fails."""
    status_code = 422
    message = "Validation error"
    error_code = "VALIDATION_ERROR"
    
    def __init__(self, message: str = "Validation failed", validation_errors: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, **kwargs)
        if validation_errors:
            self.details['validation_errors'] = validation_errors

class AuthenticationException(APIException):
    """Raised when authentication fails."""
    status_code = 401
    message = "Authentication required"
    error_code = "AUTHENTICATION_ERROR"
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)

class AuthorizationException(APIException):
    """Raised when user lacks permission to access resource."""
    status_code = 403
    message = "Insufficient permissions"
    error_code = "AUTHORIZATION_ERROR"
    
    def __init__(self, message: str = "Access denied", required_permission: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if required_permission:
            self.details['required_permission'] = required_permission

class ResourceNotFoundException(APIException):
    """Raised when a requested resource is not found."""
    status_code = 404
    message = "Resource not found"
    error_code = "RESOURCE_NOT_FOUND"
    
    def __init__(self, message: str = "Resource not found", resource_type: Optional[str] = None, resource_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if resource_type:
            self.details['resource_type'] = resource_type
        if resource_id:
            self.details['resource_id'] = resource_id

class BusinessLogicException(APIException):
    """Raised when business logic validation fails."""
    status_code = 400
    message = "Business logic error"
    error_code = "BUSINESS_LOGIC_ERROR"
    
    def __init__(self, message: str = "Business rule violation", rule: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if rule:
            self.details['violated_rule'] = rule

class DatabaseException(APIException):
    """Raised when database operations fail."""
    status_code = 500
    message = "Database error"
    error_code = "DATABASE_ERROR"
    
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if operation:
            self.details['operation'] = operation

class ExternalServiceException(APIException):
    """Raised when external service calls fail."""
    status_code = 502
    message = "External service error"
    error_code = "EXTERNAL_SERVICE_ERROR"
    
    def __init__(self, message: str = "External service unavailable", service_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if service_name:
            self.details['service_name'] = service_name

class FileUploadException(APIException):
    """Raised when file upload operations fail."""
    status_code = 400
    message = "File upload error"
    error_code = "FILE_UPLOAD_ERROR"
    
    def __init__(self, message: str = "File upload failed", file_name: Optional[str] = None, file_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if file_name:
            self.details['file_name'] = file_name
        if file_type:
            self.details['file_type'] = file_type

class PaymentException(APIException):
    """Raised when payment processing fails."""
    status_code = 402
    message = "Payment error"
    error_code = "PAYMENT_ERROR"
    
    def __init__(self, message: str = "Payment processing failed", payment_method: Optional[str] = None, transaction_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if payment_method:
            self.details['payment_method'] = payment_method
        if transaction_id:
            self.details['transaction_id'] = transaction_id

# 3D Printing specific exceptions
class PrintJobException(BusinessLogicException):
    """Raised when print job operations fail."""
    error_code = "PRINT_JOB_ERROR"
    
    def __init__(self, message: str = "Print job error", job_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if job_id:
            self.details['job_id'] = job_id

class MaterialException(BusinessLogicException):
    """Raised when material-related operations fail."""
    error_code = "MATERIAL_ERROR"
    
    def __init__(self, message: str = "Material error", material_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if material_id:
            self.details['material_id'] = material_id

class PrinterException(BusinessLogicException):
    """Raised when printer-related operations fail."""
    error_code = "PRINTER_ERROR"
    
    def __init__(self, message: str = "Printer error", printer_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if printer_id:
            self.details['printer_id'] = printer_id

class InventoryException(BusinessLogicException):
    """Raised when inventory operations fail."""
    error_code = "INVENTORY_ERROR"
    
    def __init__(self, message: str = "Inventory error", product_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if product_id:
            self.details['product_id'] = product_id
