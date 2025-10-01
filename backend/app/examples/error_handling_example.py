"""
Example demonstrating the new error handling system.
This file shows how to use the comprehensive error handling in business logic.
"""

from app.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    BusinessLogicException,
    handle_database_operation,
    handle_business_operation,
    ErrorContext,
    validate_required_fields,
    safe_execute
)
from app.utilities.db_utils import get_session_with_retries
from app.product.model import Product
from app.order.model import Order
import logging

logger = logging.getLogger(__name__)

class ExampleService:
    """
    Example service demonstrating error handling patterns.
    """
    
    @handle_database_operation("get product by ID")
    def get_product_by_id(self, product_id: str):
        """
        Example of database operation with error handling.
        """
        with get_session_with_retries() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ResourceNotFoundException(
                    message="Product not found",
                    resource_type="Product",
                    resource_id=product_id
                )
            return product
    
    @handle_business_operation("validate product data")
    def validate_product_data(self, data: dict):
        """
        Example of business logic validation with error context.
        """
        context = ErrorContext("product validation")
        
        # Validate required fields
        required_fields = ['name', 'price', 'category_id']
        if not validate_required_fields(data, required_fields, context):
            raise ValidationException(
                message="Product validation failed",
                validation_errors=context.get_error_summary()
            )
        
        # Validate price
        if 'price' in data and data['price'] <= 0:
            context.add_error("Price must be greater than 0", {'price': data['price']})
        
        # Validate category exists
        if 'category_id' in data:
            category_exists = safe_execute(
                lambda: self._check_category_exists(data['category_id']),
                default_return=False
            )
            if not category_exists:
                context.add_error("Category does not exist", {'category_id': data['category_id']})
        
        # Raise exception if there are errors
        context.raise_if_errors(ValidationException)
        
        return True
    
    def _check_category_exists(self, category_id: str) -> bool:
        """Helper method to check if category exists."""
        # This would typically query the database
        return True  # Simplified for example
    
    def create_product_with_validation(self, data: dict):
        """
        Example of creating a product with comprehensive error handling.
        """
        try:
            # Validate input data
            self.validate_product_data(data)
            
            # Create product with database error handling
            with handle_database_errors("create product"):
                with get_session_with_retries() as session:
                    product = Product(**data)
                    session.add(product)
                    session.commit()
                    return product
                    
        except ValidationException as e:
            logger.warning(f"Validation error in create_product: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_product: {str(e)}")
            raise BusinessLogicException(
                message="Failed to create product",
                details={'original_error': str(e)}
            )
    
    def process_order_with_error_context(self, order_data: dict):
        """
        Example of processing an order with error context.
        """
        context = ErrorContext("order processing")
        
        # Validate order data
        required_fields = ['items', 'customer_id', 'total_amount']
        if not validate_required_fields(order_data, required_fields, context):
            raise ValidationException(
                message="Order validation failed",
                validation_errors=context.get_error_summary()
            )
        
        # Check inventory for each item
        for item in order_data.get('items', []):
            if not self._check_inventory(item.get('product_id'), item.get('quantity')):
                context.add_error(
                    f"Insufficient inventory for product {item.get('product_id')}",
                    {'product_id': item['product_id'], 'requested_quantity': item['quantity']}
                )
        
        # Check customer exists
        if not self._check_customer_exists(order_data.get('customer_id')):
            context.add_error(
                "Customer does not exist",
                {'customer_id': order_data.get('customer_id')}
            )
        
        # Raise exception if there are errors
        context.raise_if_errors(BusinessLogicException)
        
        # Process the order
        return self._create_order(order_data)
    
    def _check_inventory(self, product_id: str, quantity: int) -> bool:
        """Check if sufficient inventory exists."""
        # This would typically query the inventory
        return True  # Simplified for example
    
    def _check_customer_exists(self, customer_id: str) -> bool:
        """Check if customer exists."""
        # This would typically query the database
        return True  # Simplified for example
    
    def _create_order(self, order_data: dict):
        """Create the order."""
        # This would typically create the order in the database
        return {"order_id": "12345", "status": "created"}

# Example usage in a route handler
def example_route_handler():
    """
    Example of how to use the error handling in a route handler.
    """
    service = ExampleService()
    
    try:
        # This will automatically handle database errors
        product = service.get_product_by_id("some-product-id")
        return {"success": True, "product": product}
        
    except ResourceNotFoundException as e:
        # This will be automatically converted to a proper API response
        raise  # The error handler will convert this to JSON response
    
    except ValidationException as e:
        # This will be automatically converted to a proper API response
        raise  # The error handler will convert this to JSON response
