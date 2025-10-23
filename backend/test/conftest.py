"""
Test configuration and fixtures for the 3D Store backend.

This module provides shared fixtures and configuration for all tests.
"""

import os
import sys
import pytest
import tempfile
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask
from werkzeug.security import generate_password_hash

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set required environment variables BEFORE importing app modules
# This prevents ValueError when config.py is loaded
os.environ['TESTING'] = 'True'
os.environ['SECRET_KEY'] = 'test_secret_key_for_testing_12345678'
os.environ['SECURITY_PASSWORD_SALT'] = 'test_salt_for_testing_12345678'
os.environ['DB_TYPE'] = 'sqlite'
os.environ['CACHE_ENABLED'] = 'False'
os.environ['SCHEDULER_ENABLED'] = 'False'

# Initialize translation manager BEFORE importing models
from sqlalchemy_i18n import make_translatable
make_translatable(options={
    'locales': ['en', 'ar'],
})

from app import create_app
from database import Base
from app.users.model import User
from app.product.model import Product
from app.category.model import Category
from app.order.model import Order
from app.customers.model import Customer
from app.inventory.model import Inventory
from app.transaction.model import Transaction
from app.branch.model import Branch
from app.company.model import Company
from app.store.model import Store
from app.expense.model import Expense, ExpenseCategory
from app.financial.model import FiscalYear, FiscalPeriod
from app.rating.model import Rating
from app.medias.model import Media
from app.address.model import ShippingAddress
from app.staff.model import Staff
from app.users.model import Role, Permission, UserRoles, RolePermission
from app.common.enum import UserTypeEnum, LanguageEnum, OrderStatusEnum, TransactionType


@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure test database path (other env vars already set at module level)
    os.environ['DB_DATABASE_NAME'] = db_path
    
    # Import engine from database module
    from database import engine, Base as DatabaseBase
    
    # Create app without parameters (create_app doesn't accept parameters)
    app = create_app()
    
    with app.app_context():
        # Create all tables
        DatabaseBase.metadata.create_all(bind=engine)
        yield app
        # Clean up
        DatabaseBase.metadata.drop_all(bind=engine)
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session for testing."""
    from database import Session
    with app.app_context():
        session = Session()
        yield session
        session.close()


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    return {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_headers():
    """Create admin authentication headers for testing."""
    return {
        'Authorization': 'Bearer admin_token',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username='testuser',
        phone='+1234567890',
        email='test@example.com',
        user_type=UserTypeEnum.USER,
        language=LanguageEnum.ENGLISH,
        password='Test@1234',  # Plain text password (model will hash it)
        active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_admin(db_session):
    """Create a sample admin user for testing."""
    admin = User(
        username='admin',
        phone='+1234567891',
        email='admin@example.com',
        user_type=UserTypeEnum.ADMIN,
        language=LanguageEnum.ENGLISH,
        password='Admin@1234',  # Plain text password (model will hash it)
        active=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def sample_customer(db_session, sample_user):
    """Create a sample customer for testing."""
    customer = Customer(
        user_id=sample_user.id,
        email='customer@example.com',
        mobile='+1234567890',
        customer_type='individual',
        status='active'
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def sample_company(db_session):
    """Create a sample company for testing."""
    company = Company(
        name='Test Company',
        email='company@example.com',
        phone='+1234567890',
        country='US',
        is_active=True
    )
    db_session.add(company)
    db_session.commit()
    return company


@pytest.fixture
def sample_branch(db_session, sample_company):
    """Create a sample branch for testing."""
    branch = Branch(
        company_id=sample_company.id,
        name='Test Branch',
        address='123 Test Street',
        city='Test City',
        country='US',
        is_active=True
    )
    db_session.add(branch)
    db_session.commit()
    return branch


@pytest.fixture
def sample_store(db_session, sample_branch):
    """Create a sample store for testing."""
    store = Store(
        branch_id=sample_branch.id,
        name='Test Store',
        address='456 Store Street',
        city='Store City',
        country='US',
        is_active=True
    )
    db_session.add(store)
    db_session.commit()
    return store


@pytest.fixture
def sample_category(db_session):
    """Create a sample category for testing."""
    category = Category(
        code='TEST_CAT',
        slug='test-category',
        is_active=True,
        is_featured=False
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_product(db_session, sample_category):
    """Create a sample product for testing."""
    from app.common.enum import ProductUnitEnum
    product = Product(
        code='TEST_PROD',
        sku='TEST-SKU-001',
        product_type='service',
        category_id=sample_category.id,
        base_price=100.00,
        currency='USD',
        is_dynamic_pricing=False,
        unit=ProductUnitEnum.PIECE
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture
def sample_order(db_session, sample_customer):
    """Create a sample order for testing."""
    order = Order(
        order_number='ORD-001',
        customer_id=sample_customer.id,
        status=OrderStatusEnum.PENDING,
        order_type='print_service',
        subtotal=100.00,
        total_amount=100.00,
        currency='USD',
        payment_status='pending'
    )
    db_session.add(order)
    db_session.commit()
    return order


@pytest.fixture
def sample_inventory(db_session, sample_product, sample_branch):
    """Create a sample inventory record for testing."""
    inventory = Inventory(
        product_id=sample_product.id,
        branch_id=sample_branch.id,
        quantity=100,
        quantity_alert=10
    )
    db_session.add(inventory)
    db_session.commit()
    return inventory


@pytest.fixture
def sample_transaction(db_session, sample_product, sample_branch):
    """Create a sample transaction for testing."""
    transaction = Transaction(
        product_id=sample_product.id,
        from_location_id=sample_branch.id,
        to_location_id=sample_branch.id,
        quantity=10,
        transaction_type=TransactionType.IN
    )
    db_session.add(transaction)
    db_session.commit()
    return transaction


@pytest.fixture
def sample_expense_category(db_session):
    """Create a sample expense category for testing."""
    category = ExpenseCategory(
        name='Test Expense Category',
        description='Test category for expenses',
        is_active=True
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_expense(db_session, sample_expense_category, sample_branch):
    """Create a sample expense for testing."""
    expense = Expense(
        category_id=sample_expense_category.id,
        branch_id=sample_branch.id,
        amount=500.00,
        currency='USD',
        status='pending',
        description='Test expense'
    )
    db_session.add(expense)
    db_session.commit()
    return expense


@pytest.fixture
def sample_fiscal_year(db_session):
    """Create a sample fiscal year for testing."""
    fiscal_year = FiscalYear(
        name='2024',
        start_date='2024-01-01',
        end_date='2024-12-31',
        is_active=True
    )
    db_session.add(fiscal_year)
    db_session.commit()
    return fiscal_year


@pytest.fixture
def sample_rating(db_session, sample_user, sample_product, sample_order):
    """Create a sample rating for testing."""
    rating = Rating(
        user_id=sample_user.id,
        product_id=sample_product.id,
        order_id=sample_order.id,
        rating=5,
        comment='Great product!'
    )
    db_session.add(rating)
    db_session.commit()
    return rating


@pytest.fixture
def sample_role(db_session):
    """Create a sample role for testing."""
    role = Role(
        name='test_role',
        description='Test role for testing',
        is_active=True
    )
    db_session.add(role)
    db_session.commit()
    return role


@pytest.fixture
def sample_permission(db_session):
    """Create a sample permission for testing."""
    permission = Permission(
        name='test_permission',
        resource='test_resource',
        action='test_action',
        description='Test permission for testing'
    )
    db_session.add(permission)
    db_session.commit()
    return permission


@pytest.fixture
def sample_supplier(db_session):
    """Create a sample supplier for testing."""
    from app.supplier.model import Supplier
    import uuid
    supplier = Supplier(
        id=uuid.uuid4(),
        code='SUP-001',
        contact_person='John Doe',
        phone='+96812345678',
        email='supplier@test.com',
        active=True
    )
    db_session.add(supplier)
    db_session.commit()
    return supplier


@pytest.fixture
def sample_quotation(db_session, sample_user, sample_product):
    """Create a sample quotation for testing."""
    from app.quotation.model import Quotation
    import uuid
    from datetime import datetime, timezone
    quotation = Quotation(
        id=uuid.uuid4(),
        customer_id=sample_user.id,
        product_id=sample_product.id,
        quantity=5,
        base_price=100.00,
        total_price=125.00,
        status='draft',
        valid_until=datetime.now(timezone.utc),
        create_date=datetime.now(timezone.utc),
        modified_date=datetime.now(timezone.utc)
    )
    db_session.add(quotation)
    db_session.commit()
    return quotation


@pytest.fixture
def sample_invoice(db_session, sample_order, sample_customer, sample_branch):
    """Create a sample invoice for testing."""
    from app.invoices.model import Invoice
    import uuid
    from datetime import datetime, timezone, date
    invoice = Invoice(
        id=uuid.uuid4(),
        number='INV-001',
        total_amount=100.00,
        tax=15.00,
        discount=0.00,
        delivery_amount=10.00,
        grand_total=125.00,
        customer_id=sample_customer.id,
        branch_id=sample_branch.id,
        user_id=sample_order.user_id,
        payment_status='pending',
        date=date.today(),
        create_date=datetime.now(timezone.utc),
        modified_date=datetime.now(timezone.utc)
    )
    db_session.add(invoice)
    db_session.commit()
    return invoice


@pytest.fixture
def sample_shipping(db_session, sample_order):
    """Create a sample shipping record for testing."""
    from app.shipping.model import Shipping
    import uuid
    from datetime import datetime, timezone
    shipping = Shipping(
        id=uuid.uuid4(),
        order_id=sample_order.id,
        carrier='DHL',
        tracking_number='TRACK123',
        cost=10.00,
        status='pending',
        create_date=datetime.now(timezone.utc),
        modified_date=datetime.now(timezone.utc)
    )
    db_session.add(shipping)
    db_session.commit()
    return shipping


@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    with patch('redis.Redis') as mock_redis:
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.get.return_value = None
        mock_redis.return_value.set.return_value = True
        mock_redis.return_value.delete.return_value = True
        mock_redis.return_value.keys.return_value = []
        yield mock_redis


@pytest.fixture
def mock_cache():
    """Mock Flask-Caching for testing."""
    with patch('flask_caching.Cache') as mock_cache:
        mock_cache.return_value.get.return_value = None
        mock_cache.return_value.set.return_value = True
        mock_cache.return_value.delete.return_value = True
        mock_cache.return_value.clear.return_value = True
        yield mock_cache


@pytest.fixture
def mock_jwt():
    """Mock JWT for testing."""
    with patch('jwt.decode') as mock_jwt:
        mock_jwt.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
        yield mock_jwt


@pytest.fixture
def mock_mail():
    """Mock Flask-Mail for testing."""
    with patch('flask_mail.Mail') as mock_mail:
        yield mock_mail


@pytest.fixture
def mock_limiter():
    """Mock Flask-Limiter for testing."""
    with patch('flask_limiter.Limiter') as mock_limiter:
        yield mock_limiter


@pytest.fixture
def mock_scheduler():
    """Mock APScheduler for testing."""
    with patch('flask_apscheduler.APScheduler') as mock_scheduler:
        yield mock_scheduler


@pytest.fixture
def mock_depot():
    """Mock Depot for file storage testing."""
    with patch('depot.fields.sqlalchemy.UploadedFileField') as mock_depot:
        yield mock_depot


# Test data factories
class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_user(**kwargs):
        """Create a user with default values."""
        defaults = {
            'username': 'testuser',
            'phone': '+1234567890',
            'email': 'test@example.com',
            'user_type': UserTypeEnum.USER,
            'language': LanguageEnum.ENGLISH,
            'password': generate_password_hash('testpassword'),
            'active': True
        }
        defaults.update(kwargs)
        return User(**defaults)
    
    @staticmethod
    def create_product(**kwargs):
        """Create a product with default values."""
        defaults = {
            'code': 'TEST_PROD',
            'sku': 'TEST-SKU-001',
            'product_type': 'service',
            'base_price': 100.00,
            'currency': 'USD',
            'is_dynamic_pricing': False
        }
        defaults.update(kwargs)
        return Product(**defaults)
    
    @staticmethod
    def create_category(**kwargs):
        """Create a category with default values."""
        defaults = {
            'code': 'TEST_CAT',
            'slug': 'test-category',
            'is_active': True,
            'is_featured': False
        }
        defaults.update(kwargs)
        return Category(**defaults)
    
    @staticmethod
    def create_order(**kwargs):
        """Create an order with default values."""
        defaults = {
            'order_number': 'ORD-001',
            'status': OrderStatusEnum.PENDING,
            'order_type': 'print_service',
            'subtotal': 100.00,
            'total_amount': 100.00,
            'currency': 'USD',
            'payment_status': 'pending'
        }
        defaults.update(kwargs)
        return Order(**defaults)


@pytest.fixture
def test_data_factory():
    """Provide access to the test data factory."""
    return TestDataFactory


# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def assert_response_success(response, expected_status=200):
        """Assert that a response is successful."""
        assert response.status_code == expected_status
        assert response.is_json
    
    @staticmethod
    def assert_response_error(response, expected_status=400):
        """Assert that a response is an error."""
        assert response.status_code == expected_status
        assert response.is_json
    
    @staticmethod
    def assert_response_unauthorized(response):
        """Assert that a response is unauthorized."""
        assert response.status_code == 401
        assert response.is_json
    
    @staticmethod
    def assert_response_forbidden(response):
        """Assert that a response is forbidden."""
        assert response.status_code == 403
        assert response.is_json
    
    @staticmethod
    def assert_response_not_found(response):
        """Assert that a response is not found."""
        assert response.status_code == 404
        assert response.is_json
    
    @staticmethod
    def get_json_response(response):
        """Get JSON response data."""
        return response.get_json()
    
    @staticmethod
    def assert_json_keys(data, expected_keys):
        """Assert that JSON data contains expected keys."""
        for key in expected_keys:
            assert key in data, f"Key '{key}' not found in response data"
    
    @staticmethod
    def assert_json_structure(data, expected_structure):
        """Assert that JSON data matches expected structure."""
        if isinstance(expected_structure, dict):
            for key, value_type in expected_structure.items():
                assert key in data, f"Key '{key}' not found in response data"
                assert isinstance(data[key], value_type), f"Key '{key}' should be {value_type.__name__}"
        elif isinstance(expected_structure, list):
            assert isinstance(data, list), "Expected list but got other type"
            if expected_structure:
                for item in data:
                    TestUtils.assert_json_structure(item, expected_structure[0])


@pytest.fixture
def test_utils():
    """Provide access to test utilities."""
    return TestUtils


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as a database test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to tests in test_unit directory
        if "test_unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in test_integration directory
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add API marker to tests in test_api directory
        if "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        # Add database marker to tests that use database
        if "test_database" in str(item.fspath) or "db_session" in item.fixturenames:
            item.add_marker(pytest.mark.database)
