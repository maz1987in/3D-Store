"""
Base test classes for the 3D Store backend.

This module provides base classes for different types of tests.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from flask import Flask
from app import create_app


class BaseTestCase:
    """Base test case class with common functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_test(self, app, db_session):
        """Set up test environment."""
        self.app = app
        self.db_session = db_session
        self.client = app.test_client()
    
    def assert_response_success(self, response, expected_status=200):
        """Assert that a response is successful."""
        assert response.status_code == expected_status
        assert response.is_json
    
    def assert_response_error(self, response, expected_status=400):
        """Assert that a response is an error."""
        assert response.status_code == expected_status
        assert response.is_json
    
    def assert_response_unauthorized(self, response):
        """Assert that a response is unauthorized."""
        assert response.status_code == 401
        assert response.is_json
    
    def assert_response_forbidden(self, response):
        """Assert that a response is forbidden."""
        assert response.status_code == 403
        assert response.is_json
    
    def assert_response_not_found(self, response):
        """Assert that a response is not found."""
        assert response.status_code == 404
        assert response.is_json
    
    def get_json_response(self, response):
        """Get JSON response data."""
        return response.get_json()
    
    def assert_json_keys(self, data, expected_keys):
        """Assert that JSON data contains expected keys."""
        for key in expected_keys:
            assert key in data, f"Key '{key}' not found in response data"
    
    def assert_json_structure(self, data, expected_structure):
        """Assert that JSON data matches expected structure."""
        if isinstance(expected_structure, dict):
            for key, value_type in expected_structure.items():
                assert key in data, f"Key '{key}' not found in response data"
                assert isinstance(data[key], value_type), f"Key '{key}' should be {value_type.__name__}"
        elif isinstance(expected_structure, list):
            assert isinstance(data, list), "Expected list but got other type"
            if expected_structure:
                for item in data:
                    self.assert_json_structure(item, expected_structure[0])


class BaseUnitTestCase(BaseTestCase):
    """Base class for unit tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        pass


class BaseIntegrationTestCase(BaseTestCase):
    """Base class for integration tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up database after each test
        self.db_session.rollback()


class BaseAPITestCase(BaseTestCase):
    """Base class for API tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        self.auth_headers = {
            'Authorization': 'Bearer test_token',
            'Content-Type': 'application/json'
        }
        self.admin_headers = {
            'Authorization': 'Bearer admin_token',
            'Content-Type': 'application/json'
        }
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up database after each test
        self.db_session.rollback()
    
    def make_request(self, method, url, headers=None, data=None, json_data=None):
        """Make a request with common parameters."""
        if headers is None:
            headers = self.auth_headers
        
        if json_data:
            return self.client.open(
                method=method,
                path=url,
                headers=headers,
                json=json_data
            )
        elif data:
            return self.client.open(
                method=method,
                path=url,
                headers=headers,
                data=data
            )
        else:
            return self.client.open(
                method=method,
                path=url,
                headers=headers
            )
    
    def get(self, url, headers=None):
        """Make a GET request."""
        return self.make_request('GET', url, headers)
    
    def post(self, url, headers=None, data=None, json_data=None):
        """Make a POST request."""
        return self.make_request('POST', url, headers, data, json_data)
    
    def put(self, url, headers=None, data=None, json_data=None):
        """Make a PUT request."""
        return self.make_request('PUT', url, headers, data, json_data)
    
    def delete(self, url, headers=None):
        """Make a DELETE request."""
        return self.make_request('DELETE', url, headers)
    
    def patch(self, url, headers=None, data=None, json_data=None):
        """Make a PATCH request."""
        return self.make_request('PATCH', url, headers, data, json_data)


class BaseDatabaseTestCase(BaseTestCase):
    """Base class for database tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        # Start a transaction
        self.transaction = self.db_session.begin()
    
    def teardown_method(self):
        """Clean up after each test."""
        # Rollback the transaction
        self.transaction.rollback()
    
    def create_test_data(self):
        """Create test data for the test."""
        pass
    
    def cleanup_test_data(self):
        """Clean up test data after the test."""
        pass


class BaseServiceTestCase(BaseTestCase):
    """Base class for service layer tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up database after each test
        self.db_session.rollback()
    
    def mock_dependencies(self):
        """Mock external dependencies for service tests."""
        pass


class BaseRepositoryTestCase(BaseTestCase):
    """Base class for repository tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up database after each test
        self.db_session.rollback()
    
    def create_test_entities(self):
        """Create test entities for repository tests."""
        pass


class BaseModelTestCase(BaseTestCase):
    """Base class for model tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up database after each test
        self.db_session.rollback()
    
    def assert_model_attributes(self, model, expected_attributes):
        """Assert that a model has expected attributes."""
        for attr_name, expected_value in expected_attributes.items():
            assert hasattr(model, attr_name), f"Model missing attribute: {attr_name}"
            actual_value = getattr(model, attr_name)
            assert actual_value == expected_value, f"Attribute {attr_name}: expected {expected_value}, got {actual_value}"
    
    def assert_model_relationships(self, model, expected_relationships):
        """Assert that a model has expected relationships."""
        for rel_name, expected_type in expected_relationships.items():
            assert hasattr(model, rel_name), f"Model missing relationship: {rel_name}"
            # Note: This is a basic check - more sophisticated relationship testing
            # would require actual relationship traversal


class BaseMiddlewareTestCase(BaseTestCase):
    """Base class for middleware tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        pass
    
    def create_mock_request(self, **kwargs):
        """Create a mock request for testing."""
        mock_request = Mock()
        mock_request.headers = kwargs.get('headers', {})
        mock_request.method = kwargs.get('method', 'GET')
        mock_request.path = kwargs.get('path', '/')
        mock_request.remote_addr = kwargs.get('remote_addr', '127.0.0.1')
        mock_request.user_agent = kwargs.get('user_agent', 'test-agent')
        return mock_request
    
    def create_mock_response(self, **kwargs):
        """Create a mock response for testing."""
        mock_response = Mock()
        mock_response.status_code = kwargs.get('status_code', 200)
        mock_response.headers = kwargs.get('headers', {})
        mock_response.data = kwargs.get('data', b'')
        return mock_response


class BaseCacheTestCase(BaseTestCase):
    """Base class for cache tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        pass
    
    def mock_cache_service(self):
        """Mock cache service for testing."""
        with patch('app.caching.cache_service.CacheService') as mock_cache:
            mock_cache.return_value.get.return_value = None
            mock_cache.return_value.set.return_value = True
            mock_cache.return_value.delete.return_value = True
            mock_cache.return_value.clear.return_value = True
            yield mock_cache


class BaseExceptionTestCase(BaseTestCase):
    """Base class for exception handling tests."""
    
    def setup_method(self):
        """Set up method for each test."""
        pass
    
    def teardown_method(self):
        """Clean up after each test."""
        pass
    
    def assert_exception_raised(self, exception_class, callable_obj, *args, **kwargs):
        """Assert that a specific exception is raised."""
        with pytest.raises(exception_class):
            callable_obj(*args, **kwargs)
    
    def assert_exception_message(self, exception_class, expected_message, callable_obj, *args, **kwargs):
        """Assert that a specific exception with message is raised."""
        with pytest.raises(exception_class) as exc_info:
            callable_obj(*args, **kwargs)
        assert expected_message in str(exc_info.value)


# Test decorators
def unit_test(func):
    """Decorator to mark a test as a unit test."""
    func._pytest_mark_unit = True
    return func


def integration_test(func):
    """Decorator to mark a test as an integration test."""
    func._pytest_mark_integration = True
    return func


def api_test(func):
    """Decorator to mark a test as an API test."""
    func._pytest_mark_api = True
    return func


def database_test(func):
    """Decorator to mark a test as a database test."""
    func._pytest_mark_database = True
    return func


def slow_test(func):
    """Decorator to mark a test as slow running."""
    func._pytest_mark_slow = True
    return func
