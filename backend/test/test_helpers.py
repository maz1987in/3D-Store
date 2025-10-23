"""
Test helper utilities for the 3D Store backend tests.

This module provides reusable utility functions for common test operations.
"""

import io
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from werkzeug.datastructures import FileStorage


def create_test_file(filename='test.txt', content=b'test content', mimetype='text/plain'):
    """
    Create a mock file upload for testing.
    
    Args:
        filename: Name of the file
        content: File content as bytes
        mimetype: MIME type of the file
    
    Returns:
        FileStorage: Mock file object for testing uploads
    """
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type=mimetype
    )


def assert_decimal_equal(actual, expected, places=2):
    """
    Assert that two decimal/float values are equal within specified precision.
    
    Args:
        actual: Actual value
        expected: Expected value
        places: Number of decimal places to compare (default: 2)
    
    Raises:
        AssertionError: If values are not equal within precision
    """
    actual_decimal = Decimal(str(actual)).quantize(Decimal(10) ** -places)
    expected_decimal = Decimal(str(expected)).quantize(Decimal(10) ** -places)
    
    assert actual_decimal == expected_decimal, \
        f"Decimal values not equal: {actual} != {expected} (precision: {places} places)"


def assert_datetime_close(dt1, dt2, tolerance_seconds=5):
    """
    Assert that two datetime values are close within tolerance.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        tolerance_seconds: Maximum allowed difference in seconds (default: 5)
    
    Raises:
        AssertionError: If datetimes differ by more than tolerance
    """
    if isinstance(dt1, str):
        dt1 = datetime.fromisoformat(dt1.replace('Z', '+00:00'))
    if isinstance(dt2, str):
        dt2 = datetime.fromisoformat(dt2.replace('Z', '+00:00'))
    
    diff = abs((dt1 - dt2).total_seconds())
    
    assert diff <= tolerance_seconds, \
        f"Datetimes not close: {dt1} and {dt2} differ by {diff} seconds (tolerance: {tolerance_seconds}s)"


def generate_test_uuid():
    """
    Generate a consistent test UUID.
    
    Returns:
        UUID: A new UUID for testing
    """
    return uuid.uuid4()


def mock_payment_gateway_success(transaction_id='test_txn_12345', amount=100.00):
    """
    Create a mock successful payment gateway response.
    
    Args:
        transaction_id: Transaction ID to return
        amount: Transaction amount
    
    Returns:
        Mock: Mock gateway response object
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'success': True,
        'transaction_id': transaction_id,
        'amount': amount,
        'status': 'completed',
        'message': 'Payment successful'
    }
    return mock_response


def mock_payment_gateway_failure(error_message='Payment declined'):
    """
    Create a mock failed payment gateway response.
    
    Args:
        error_message: Error message to return
    
    Returns:
        Mock: Mock gateway response object
    """
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        'success': False,
        'error': error_message,
        'status': 'failed'
    }
    return mock_response


def create_test_3d_model_data():
    """
    Create test 3D model file data (simplified STL format).
    
    Returns:
        bytes: Mock STL file content
    """
    stl_content = b"""solid test_model
facet normal 0 0 1
  outer loop
    vertex 0 0 0
    vertex 1 0 0
    vertex 0 1 0
  endloop
endfacet
endsolid test_model
"""
    return stl_content


def create_test_image_data():
    """
    Create test image file data (minimal PNG).
    
    Returns:
        bytes: Mock PNG file content
    """
    # Minimal 1x1 PNG image
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return png_data


def assert_response_has_keys(response_data, required_keys):
    """
    Assert that response data contains all required keys.
    
    Args:
        response_data: Response data dictionary
        required_keys: List of required key names
    
    Raises:
        AssertionError: If any required key is missing
    """
    missing_keys = [key for key in required_keys if key not in response_data]
    assert not missing_keys, f"Response missing required keys: {missing_keys}"


def assert_valid_uuid(value):
    """
    Assert that a value is a valid UUID string.
    
    Args:
        value: Value to check
    
    Raises:
        AssertionError: If value is not a valid UUID
    """
    try:
        uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        raise AssertionError(f"Invalid UUID: {value}")


def create_mock_filter(filters=None, sorters=None, page=1, per_page=10, sort=None, sort_order='asc', queries=None):
    """
    Create a mock filter object for testing pagination and filtering.
    
    Args:
        filters: List of filter dictionaries
        sorters: List of sorter dictionaries
        page: Page number
        per_page: Items per page
        sort: Sort field name
        sort_order: Sort order (asc/desc)
        queries: Query parameters dictionary
    
    Returns:
        Mock: Mock filter object
    """
    mock_filter = Mock()
    mock_filter.filters = filters or []
    mock_filter.sorters = sorters or []
    mock_filter.page = page
    mock_filter.per_page = per_page
    mock_filter.sort = sort
    mock_filter.sort_order = sort_order
    mock_filter.queries = queries or {}
    return mock_filter


def assert_pagination_structure(data, expected_keys=None):
    """
    Assert that data has valid pagination structure.
    
    Args:
        data: Response data to validate
        expected_keys: Optional list of additional keys to check
    
    Raises:
        AssertionError: If pagination structure is invalid
    """
    default_keys = ['filters']
    if expected_keys:
        default_keys.extend(expected_keys)
    
    for key in default_keys:
        assert key in data, f"Pagination data missing key: {key}"
    
    # Check filters structure if present
    if 'filters' in data and data['filters']:
        assert isinstance(data['filters'], dict), "Filters should be a dictionary"


def create_test_date_range(days_back=30):
    """
    Create a test date range for queries.
    
    Args:
        days_back: Number of days back from today
    
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


def assert_error_response(response_data, expected_error_key='error'):
    """
    Assert that response data represents an error.
    
    Args:
        response_data: Response data dictionary
        expected_error_key: Key name for error message
    
    Raises:
        AssertionError: If error structure is invalid
    """
    assert expected_error_key in response_data or 'message' in response_data, \
        "Error response missing error/message key"


class MockDBSession:
    """Mock database session for testing without actual DB."""
    
    def __init__(self):
        self.added_objects = []
        self.deleted_objects = []
        self.committed = False
        self.rolled_back = False
    
    def add(self, obj):
        """Mock add operation."""
        self.added_objects.append(obj)
    
    def delete(self, obj):
        """Mock delete operation."""
        self.deleted_objects.append(obj)
    
    def commit(self):
        """Mock commit operation."""
        self.committed = True
    
    def rollback(self):
        """Mock rollback operation."""
        self.rolled_back = True
    
    def query(self, *args):
        """Mock query operation."""
        return MagicMock()
    
    def flush(self):
        """Mock flush operation."""
        pass
    
    def refresh(self, obj):
        """Mock refresh operation."""
        pass


def create_mock_request(method='GET', path='/', json_data=None, form_data=None, headers=None):
    """
    Create a mock Flask request object.
    
    Args:
        method: HTTP method
        path: Request path
        json_data: JSON payload
        form_data: Form data
        headers: Request headers
    
    Returns:
        Mock: Mock request object
    """
    mock_request = Mock()
    mock_request.method = method
    mock_request.path = path
    mock_request.json = json_data
    mock_request.form = form_data or {}
    mock_request.headers = headers or {}
    mock_request.args = {}
    return mock_request

