from flask import jsonify
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class APIResponse:
    """
    Standardized API response wrapper for consistent response format
    """
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", meta: Optional[Dict] = None) -> tuple:
        """
        Create a successful API response
        
        Args:
            data: Response data
            message: Success message
            meta: Additional metadata (pagination, etc.)
            
        Returns:
            Tuple of (json_response, status_code)
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
            "errors": None
        }
        
        if meta:
            response["meta"] = meta
            
        return jsonify(response), 200
    
    @staticmethod
    def created(data: Any = None, message: str = "Resource created successfully") -> tuple:
        """
        Create a 201 Created response
        
        Args:
            data: Created resource data
            message: Success message
            
        Returns:
            Tuple of (json_response, status_code)
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
            "errors": None
        }
        return jsonify(response), 201
    
    @staticmethod
    def error(message: str, errors: Optional[Dict] = None, status_code: int = 400) -> tuple:
        """
        Create an error API response
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code
            
        Returns:
            Tuple of (json_response, status_code)
        """
        response = {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors
        }
        
        logger.warning(f"API Error {status_code}: {message}")
        if errors:
            logger.warning(f"Error details: {errors}")
            
        return jsonify(response), status_code
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> tuple:
        """
        Create a 404 Not Found response
        
        Args:
            message: Error message
            
        Returns:
            Tuple of (json_response, status_code)
        """
        return APIResponse.error(message, status_code=404)
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> tuple:
        """
        Create a 401 Unauthorized response
        
        Args:
            message: Error message
            
        Returns:
            Tuple of (json_response, status_code)
        """
        return APIResponse.error(message, status_code=401)
    
    @staticmethod
    def forbidden(message: str = "Insufficient permissions") -> tuple:
        """
        Create a 403 Forbidden response
        
        Args:
            message: Error message
            
        Returns:
            Tuple of (json_response, status_code)
        """
        return APIResponse.error(message, status_code=403)
    
    @staticmethod
    def validation_error(message: str = "Validation failed", errors: Optional[Dict] = None) -> tuple:
        """
        Create a 422 Validation Error response
        
        Args:
            message: Error message
            errors: Validation error details
            
        Returns:
            Tuple of (json_response, status_code)
        """
        return APIResponse.error(message, errors, status_code=422)
    
    @staticmethod
    def server_error(message: str = "Internal server error") -> tuple:
        """
        Create a 500 Internal Server Error response
        
        Args:
            message: Error message
            
        Returns:
            Tuple of (json_response, status_code)
        """
        logger.error(f"Server Error: {message}")
        return APIResponse.error(message, status_code=500)
    
    @staticmethod
    def paginated(data: List[Any], pagination: Dict, message: str = "Success") -> tuple:
        """
        Create a paginated response
        
        Args:
            data: List of items
            pagination: Pagination metadata
            message: Success message
            
        Returns:
            Tuple of (json_response, status_code)
        """
        meta = {
            "pagination": {
                "page": pagination.get("page", 1),
                "per_page": pagination.get("per_page", 20),
                "total": pagination.get("total", 0),
                "pages": pagination.get("pages", 0),
                "has_next": pagination.get("has_next", False),
                "has_prev": pagination.get("has_prev", False)
            }
        }
        
        return APIResponse.success(data, message, meta)
    
    @staticmethod
    def no_content(message: str = "No content") -> tuple:
        """
        Create a 204 No Content response
        
        Args:
            message: Message (usually not shown in 204 responses)
            
        Returns:
            Tuple of (json_response, status_code)
        """
        return jsonify(None), 204
