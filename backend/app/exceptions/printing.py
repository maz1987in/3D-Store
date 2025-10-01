"""
3D Printing specific exception classes.
Handles errors related to 3D printing operations, materials, and print jobs.
"""

from typing import Optional, Dict, Any
from .base import BusinessLogicException, APIException

class PrintJobException(BusinessLogicException):
    """Base exception for print job related errors."""
    error_code = "PRINT_JOB_ERROR"
    
    def __init__(
        self, 
        message: str = "Print job error", 
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if job_id:
            self.details['job_id'] = job_id
        if status:
            self.details['current_status'] = status

class PrintJobNotFoundError(PrintJobException):
    """Raised when a print job is not found."""
    status_code = 404
    message = "Print job not found"
    error_code = "PRINT_JOB_NOT_FOUND"

class PrintJobInvalidStatusError(PrintJobException):
    """Raised when trying to perform an invalid operation on a print job status."""
    status_code = 400
    message = "Invalid print job status operation"
    error_code = "PRINT_JOB_INVALID_STATUS"
    
    def __init__(self, current_status: str, attempted_operation: str, **kwargs):
        super().__init__(
            message=f"Cannot perform '{attempted_operation}' on print job with status '{current_status}'",
            status=current_status,
            **kwargs
        )
        self.details['attempted_operation'] = attempted_operation

class PrintJobAlreadyStartedError(PrintJobException):
    """Raised when trying to start a print job that's already started."""
    status_code = 400
    message = "Print job already started"
    error_code = "PRINT_JOB_ALREADY_STARTED"

class PrintJobCannotBeCancelledError(PrintJobException):
    """Raised when trying to cancel a print job that cannot be cancelled."""
    status_code = 400
    message = "Print job cannot be cancelled"
    error_code = "PRINT_JOB_CANNOT_BE_CANCELLED"

class MaterialException(BusinessLogicException):
    """Base exception for material related errors."""
    error_code = "MATERIAL_ERROR"
    
    def __init__(
        self, 
        message: str = "Material error", 
        material_id: Optional[str] = None,
        material_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if material_id:
            self.details['material_id'] = material_id
        if material_type:
            self.details['material_type'] = material_type

class MaterialNotFoundError(MaterialException):
    """Raised when a material is not found."""
    status_code = 404
    message = "Material not found"
    error_code = "MATERIAL_NOT_FOUND"

class MaterialInsufficientError(MaterialException):
    """Raised when there's insufficient material for a print job."""
    status_code = 400
    message = "Insufficient material"
    error_code = "MATERIAL_INSUFFICIENT"
    
    def __init__(self, required_amount: float, available_amount: float, **kwargs):
        super().__init__(
            message=f"Insufficient material: required {required_amount}, available {available_amount}",
            **kwargs
        )
        self.details['required_amount'] = required_amount
        self.details['available_amount'] = available_amount

class MaterialIncompatibleError(MaterialException):
    """Raised when material is incompatible with printer or settings."""
    status_code = 400
    message = "Material incompatible"
    error_code = "MATERIAL_INCOMPATIBLE"
    
    def __init__(self, material_type: str, printer_id: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Material type '{material_type}' is incompatible",
            material_type=material_type,
            **kwargs
        )
        if printer_id:
            self.details['printer_id'] = printer_id

class PrinterException(BusinessLogicException):
    """Base exception for printer related errors."""
    error_code = "PRINTER_ERROR"
    
    def __init__(
        self, 
        message: str = "Printer error", 
        printer_id: Optional[str] = None,
        printer_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if printer_id:
            self.details['printer_id'] = printer_id
        if printer_name:
            self.details['printer_name'] = printer_name

class PrinterNotFoundError(PrinterException):
    """Raised when a printer is not found."""
    status_code = 404
    message = "Printer not found"
    error_code = "PRINTER_NOT_FOUND"

class PrinterUnavailableError(PrinterException):
    """Raised when a printer is unavailable."""
    status_code = 503
    message = "Printer unavailable"
    error_code = "PRINTER_UNAVAILABLE"
    
    def __init__(self, reason: str = "Printer is currently unavailable", **kwargs):
        super().__init__(message=reason, **kwargs)
        self.details['unavailability_reason'] = reason

class PrinterMaintenanceError(PrinterException):
    """Raised when a printer is in maintenance mode."""
    status_code = 503
    message = "Printer in maintenance"
    error_code = "PRINTER_MAINTENANCE"
    
    def __init__(self, maintenance_until: Optional[str] = None, **kwargs):
        super().__init__(message="Printer is currently in maintenance", **kwargs)
        if maintenance_until:
            self.details['maintenance_until'] = maintenance_until

class PrinterCapacityExceededError(PrinterException):
    """Raised when printer capacity is exceeded."""
    status_code = 400
    message = "Printer capacity exceeded"
    error_code = "PRINTER_CAPACITY_EXCEEDED"
    
    def __init__(self, max_capacity: int, current_load: int, **kwargs):
        super().__init__(
            message=f"Printer capacity exceeded: {current_load}/{max_capacity}",
            **kwargs
        )
        self.details['max_capacity'] = max_capacity
        self.details['current_load'] = current_load

class ModelFileException(BusinessLogicException):
    """Base exception for 3D model file related errors."""
    error_code = "MODEL_FILE_ERROR"
    
    def __init__(
        self, 
        message: str = "Model file error", 
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if file_name:
            self.details['file_name'] = file_name
        if file_type:
            self.details['file_type'] = file_type

class ModelFileInvalidError(ModelFileException):
    """Raised when a 3D model file is invalid."""
    status_code = 400
    message = "Invalid model file"
    error_code = "MODEL_FILE_INVALID"
    
    def __init__(self, validation_errors: list, **kwargs):
        super().__init__(
            message=f"Model file validation failed: {', '.join(validation_errors)}",
            **kwargs
        )
        self.details['validation_errors'] = validation_errors

class ModelFileUnsupportedError(ModelFileException):
    """Raised when a 3D model file format is not supported."""
    status_code = 400
    message = "Unsupported model file format"
    error_code = "MODEL_FILE_UNSUPPORTED"
    
    def __init__(self, file_type: str, supported_types: list, **kwargs):
        super().__init__(
            message=f"File type '{file_type}' is not supported. Supported types: {', '.join(supported_types)}",
            file_type=file_type,
            **kwargs
        )
        self.details['supported_types'] = supported_types

class ModelFileTooLargeError(ModelFileException):
    """Raised when a 3D model file is too large."""
    status_code = 413
    message = "Model file too large"
    error_code = "MODEL_FILE_TOO_LARGE"
    
    def __init__(self, file_size: int, max_size: int, **kwargs):
        super().__init__(
            message=f"File size {file_size} bytes exceeds maximum allowed size {max_size} bytes",
            **kwargs
        )
        self.details['file_size'] = file_size
        self.details['max_size'] = max_size

class PrintSettingsException(BusinessLogicException):
    """Base exception for print settings related errors."""
    error_code = "PRINT_SETTINGS_ERROR"
    
    def __init__(
        self, 
        message: str = "Print settings error", 
        settings_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if settings_id:
            self.details['settings_id'] = settings_id

class PrintSettingsNotFoundError(PrintSettingsException):
    """Raised when print settings are not found."""
    status_code = 404
    message = "Print settings not found"
    error_code = "PRINT_SETTINGS_NOT_FOUND"

class PrintSettingsInvalidError(PrintSettingsException):
    """Raised when print settings are invalid."""
    status_code = 400
    message = "Invalid print settings"
    error_code = "PRINT_SETTINGS_INVALID"
    
    def __init__(self, validation_errors: list, **kwargs):
        super().__init__(
            message=f"Print settings validation failed: {', '.join(validation_errors)}",
            **kwargs
        )
        self.details['validation_errors'] = validation_errors

class PackagingException(BusinessLogicException):
    """Base exception for packaging related errors."""
    error_code = "PACKAGING_ERROR"
    
    def __init__(
        self, 
        message: str = "Packaging error", 
        packaging_id: Optional[str] = None,
        packaging_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if packaging_id:
            self.details['packaging_id'] = packaging_id
        if packaging_type:
            self.details['packaging_type'] = packaging_type

class PackagingNotFoundError(PackagingException):
    """Raised when packaging option is not found."""
    status_code = 404
    message = "Packaging option not found"
    error_code = "PACKAGING_NOT_FOUND"

class PackagingUnavailableError(PackagingException):
    """Raised when packaging option is unavailable."""
    status_code = 400
    message = "Packaging option unavailable"
    error_code = "PACKAGING_UNAVAILABLE"
    
    def __init__(self, reason: str = "Packaging option is currently unavailable", **kwargs):
        super().__init__(message=reason, **kwargs)
        self.details['unavailability_reason'] = reason
