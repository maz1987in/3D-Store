# Testing Framework Documentation

This directory contains the comprehensive testing framework for the 3D Store backend application.

## Overview

The testing framework is built on pytest and provides comprehensive test coverage for:
- **Unit Tests**: Individual components and functions
- **Integration Tests**: Component interactions and workflows
- **API Tests**: HTTP endpoints and request/response handling
- **Database Tests**: Data operations and integrity

## Test Structure

```
test/
├── conftest.py                 # Test configuration and fixtures
├── base_test.py               # Base test classes and utilities
├── test_unit/                 # Unit tests
│   ├── test_models.py         # Database model tests
│   ├── test_services.py       # Service layer tests
│   └── test_repositories.py   # Repository layer tests
├── test_integration/          # Integration tests
│   └── test_user_workflow.py  # User workflow tests
├── test_api/                  # API tests
│   ├── test_auth_endpoints.py # Authentication endpoint tests
│   └── test_product_endpoints.py # Product endpoint tests
└── test_database/             # Database tests
    └── (database-specific tests)
```

## Test Categories

### Unit Tests (`test_unit/`)
Test individual components in isolation:
- **Models**: Database model validation, relationships, constraints
- **Services**: Business logic, data processing, validation
- **Repositories**: Data access, queries, CRUD operations

### Integration Tests (`test_integration/`)
Test component interactions and complete workflows:
- **User Workflow**: Registration → Login → Profile Management → Logout
- **Product Workflow**: Creation → Update → Search → Deletion
- **Order Workflow**: Order Creation → Processing → Fulfillment

### API Tests (`test_api/`)
Test HTTP endpoints and API behavior:
- **Authentication**: Login, registration, password reset
- **Product Management**: CRUD operations, search, filtering
- **Order Management**: Order processing, status updates
- **User Management**: Profile management, settings

### Database Tests (`test_database/`)
Test database operations and data integrity:
- **Data Validation**: Constraint enforcement, data types
- **Relationships**: Foreign keys, cascading operations
- **Transactions**: ACID properties, rollback scenarios

## Running Tests

### Basic Commands

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest test/test_unit/
python -m pytest test/test_integration/
python -m pytest test/test_api/
python -m pytest test/test_database/

# Run specific test files
python -m pytest test/test_unit/test_models.py
python -m pytest test/test_api/test_auth_endpoints.py

# Run specific test functions
python -m pytest test/test_unit/test_models.py::TestUserModel::test_user_creation
```

### Using the Test Runner Script

```bash
# Run all tests
python scripts/run_tests.py

# Run specific test categories
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --api
python scripts/run_tests.py --database

# Run with coverage
python scripts/run_tests.py --coverage

# Run specific tests
python scripts/run_tests.py --test test/test_unit/test_models.py
python scripts/run_tests.py --test test/test_unit/test_models.py::TestUserModel::test_user_creation

# Run by markers
python scripts/run_tests.py --marker unit
python scripts/run_tests.py --marker integration
python scripts/run_tests.py --marker api
python scripts/run_tests.py --marker database
python scripts/run_tests.py --marker slow

# Run fast tests (exclude slow)
python scripts/run_tests.py --fast

# Run in parallel
python scripts/run_tests.py --parallel 4

# Run with profiling
python scripts/run_tests.py --profile

# Run in debug mode
python scripts/run_tests.py --debug

# Run in CI mode
python scripts/run_tests.py --ci

# Run with verbose output
python scripts/run_tests.py --verbose

# Run code quality checks
python scripts/run_tests.py --lint
python scripts/run_tests.py --format
python scripts/run_tests.py --type-check
python scripts/run_tests.py --quality

# Run everything (tests + quality checks)
python scripts/run_tests.py --full
```

### Advanced Options

```bash
# Run with coverage and generate HTML report
python -m pytest --cov=app --cov-report=html

# Run with coverage and fail if coverage is below threshold
python -m pytest --cov=app --cov-fail-under=80

# Run tests in parallel
python -m pytest -n 4

# Run only slow tests
python -m pytest -m slow

# Run tests excluding slow tests
python -m pytest -m "not slow"

# Run tests with maximum verbosity
python -m pytest -vv --tb=long

# Run tests in debug mode
python -m pytest --pdb

# Run tests with profiling
python -m pytest --profile --profile-svg
```

## Test Configuration

### Environment Variables

The test framework automatically sets up the testing environment:

```bash
TESTING=True
DATABASE_URL=sqlite:///:memory:
```

### Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test session. This ensures:
- **Isolation**: Each test runs in a clean environment
- **Speed**: In-memory database is faster than file-based
- **Reliability**: No test data persists between test runs

### Fixtures

The test framework provides comprehensive fixtures:

#### Application Fixtures
- `app`: Flask application instance
- `client`: Test client for making HTTP requests
- `db_session`: Database session for testing

#### Authentication Fixtures
- `auth_headers`: Standard authentication headers
- `admin_headers`: Admin authentication headers

#### Data Fixtures
- `sample_user`: Test user with default values
- `sample_admin`: Test admin user
- `sample_customer`: Test customer
- `sample_product`: Test product
- `sample_category`: Test category
- `sample_order`: Test order
- `sample_inventory`: Test inventory record
- `sample_transaction`: Test transaction
- `sample_company`: Test company
- `sample_branch`: Test branch
- `sample_store`: Test store
- `sample_expense`: Test expense
- `sample_fiscal_year`: Test fiscal year
- `sample_rating`: Test rating

#### Mock Fixtures
- `mock_redis`: Mock Redis for caching tests
- `mock_cache`: Mock Flask-Caching
- `mock_jwt`: Mock JWT operations
- `mock_mail`: Mock Flask-Mail
- `mock_limiter`: Mock Flask-Limiter
- `mock_scheduler`: Mock APScheduler
- `mock_depot`: Mock Depot file storage

## Writing Tests

### Unit Test Example

```python
def test_user_creation(self, db_session):
    """Test creating a user."""
    user = User(
        username='testuser',
        phone='+1234567890',
        email='test@example.com',
        user_type=UserTypeEnum.USER,
        language=LanguageEnum.ENGLISH,
        password='testpassword',
        active=True
    )
    
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.phone == '+1234567890'
    assert user.email == 'test@example.com'
    assert user.user_type == UserTypeEnum.USER
    assert user.language == LanguageEnum.ENGLISH
    assert user.active is True
```

### API Test Example

```python
def test_get_products_success(self, db_session, sample_product):
    """Test getting products successfully."""
    with patch('jwt.decode') as mock_jwt_decode:
        mock_jwt_decode.return_value = {'id': 'test_user_id', 'user_type': 'USER'}
        
        response = self.get('/api/products', headers=self.auth_headers)
        
        self.assert_response_success(response)
        data = self.get_json_response(response)
        
        assert 'products' in data
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
        assert len(data['products']) >= 1
```

### Integration Test Example

```python
def test_complete_user_registration_workflow(self, db_session):
    """Test complete user registration workflow."""
    # Step 1: Register new user
    with patch('jwt.encode') as mock_jwt_encode:
        mock_jwt_encode.return_value = 'test_token'
        
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': '+1234567899',
            'password': 'newpassword123',
            'user_type': 'USER',
            'language': 'ENGLISH'
        }
        
        response = self.client.post('/api/auth/register', json=register_data)
        
        self.assert_response_success(response, 201)
        data = self.get_json_response(response)
        
        assert 'token' in data
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
        
        user_id = data['user']['id']
    
    # Step 2: Verify user was created in database
    user = self.db_session.query(User).filter(User.id == user_id).first()
    assert user is not None
    assert user.username == 'newuser'
    assert user.email == 'newuser@example.com'
```

## Test Utilities

### Base Test Classes

The framework provides several base test classes:

- `BaseTestCase`: Common functionality for all tests
- `BaseUnitTestCase`: Base class for unit tests
- `BaseIntegrationTestCase`: Base class for integration tests
- `BaseAPITestCase`: Base class for API tests
- `BaseDatabaseTestCase`: Base class for database tests
- `BaseServiceTestCase`: Base class for service tests
- `BaseRepositoryTestCase`: Base class for repository tests
- `BaseModelTestCase`: Base class for model tests
- `BaseMiddlewareTestCase`: Base class for middleware tests
- `BaseCacheTestCase`: Base class for cache tests
- `BaseExceptionTestCase`: Base class for exception tests

### Test Utilities

- `TestUtils`: Utility functions for common test operations
- `TestDataFactory`: Factory class for creating test data
- `assert_response_success()`: Assert successful HTTP response
- `assert_response_error()`: Assert error HTTP response
- `assert_json_keys()`: Assert JSON response contains expected keys
- `assert_json_structure()`: Assert JSON response matches expected structure

### Test Decorators

- `@unit_test`: Mark test as unit test
- `@integration_test`: Mark test as integration test
- `@api_test`: Mark test as API test
- `@database_test`: Mark test as database test
- `@slow_test`: Mark test as slow running

## Test Data Management

### Test Data Factory

The `TestDataFactory` class provides methods for creating test data:

```python
# Create a user with default values
user = TestDataFactory.create_user()

# Create a user with custom values
user = TestDataFactory.create_user(
    username='customuser',
    email='custom@example.com'
)

# Create a product with default values
product = TestDataFactory.create_product()

# Create a product with custom values
product = TestDataFactory.create_product(
    code='CUSTOM_PROD',
    base_price=150.00
)
```

### Fixture Usage

Use fixtures to get test data:

```python
def test_user_operations(self, sample_user, sample_admin):
    """Test user operations with sample data."""
    # sample_user and sample_admin are automatically available
    assert sample_user.user_type == UserTypeEnum.USER
    assert sample_admin.user_type == UserTypeEnum.ADMIN
```

## Mocking and Patching

### Common Mock Patterns

```python
# Mock JWT operations
with patch('jwt.decode') as mock_jwt_decode:
    mock_jwt_decode.return_value = {'id': 'user_id', 'user_type': 'USER'}
    # Test code here

# Mock external services
with patch('app.external_service.api_call') as mock_api:
    mock_api.return_value = {'status': 'success'}
    # Test code here

# Mock database operations
with patch('app.database.session.query') as mock_query:
    mock_query.return_value.filter.return_value.first.return_value = mock_user
    # Test code here
```

### Mock Fixtures

Use mock fixtures for common mocking needs:

```python
def test_with_mock_redis(self, mock_redis):
    """Test with mocked Redis."""
    # mock_redis is automatically available
    pass

def test_with_mock_cache(self, mock_cache):
    """Test with mocked cache."""
    # mock_cache is automatically available
    pass
```

## Coverage and Quality

### Coverage Requirements

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%
- **Critical Paths**: 100% coverage required

### Quality Checks

The framework includes several quality checks:

- **Code Linting**: Flake8 for code style
- **Code Formatting**: Black for consistent formatting
- **Type Checking**: MyPy for type safety
- **Import Sorting**: isort for import organization

### Running Quality Checks

```bash
# Run all quality checks
python scripts/run_tests.py --quality

# Run specific quality checks
python scripts/run_tests.py --lint
python scripts/run_tests.py --format
python scripts/run_tests.py --type-check
```

## Continuous Integration

### GitHub Actions

The project includes GitHub Actions workflows for:

- **Test Execution**: Run all tests on multiple Python versions
- **Code Quality**: Run linting, formatting, and type checking
- **Coverage Reporting**: Generate and upload coverage reports
- **Security Scanning**: Run security vulnerability scans

### Local CI Simulation

```bash
# Run tests in CI mode
python scripts/run_tests.py --ci

# Run full quality check
python scripts/run_tests.py --full
```

## Best Practices

### Test Organization

1. **Group Related Tests**: Keep related tests in the same file
2. **Use Descriptive Names**: Test names should clearly describe what they test
3. **One Assertion Per Test**: Each test should verify one specific behavior
4. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification

### Test Data

1. **Use Fixtures**: Leverage fixtures for common test data
2. **Isolate Tests**: Each test should be independent
3. **Clean Up**: Tests should clean up after themselves
4. **Realistic Data**: Use realistic test data that matches production

### Mocking

1. **Mock External Dependencies**: Mock external services and APIs
2. **Mock at Boundaries**: Mock at the boundaries of your system
3. **Verify Interactions**: Verify that mocked methods are called correctly
4. **Use Real Objects When Possible**: Only mock when necessary

### Performance

1. **Fast Tests**: Keep unit tests fast (< 1 second)
2. **Slow Tests**: Mark slow tests with `@slow_test` decorator
3. **Parallel Execution**: Use parallel execution for large test suites
4. **Database Optimization**: Use in-memory database for tests

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all imports are correct and paths are set
2. **Database Issues**: Check that test database is properly configured
3. **Mock Issues**: Verify that mocks are set up correctly
4. **Fixture Issues**: Ensure fixtures are properly defined and imported

### Debug Mode

Run tests in debug mode to get more information:

```bash
python scripts/run_tests.py --debug
```

### Verbose Output

Get detailed output for debugging:

```bash
python scripts/run_tests.py --verbose
```

## Contributing

### Adding New Tests

1. **Follow Naming Conventions**: Use descriptive test names
2. **Add Documentation**: Include docstrings for test functions
3. **Use Appropriate Markers**: Mark tests with appropriate pytest markers
4. **Write Clean Code**: Follow the same code quality standards as production code

### Test Review Checklist

- [ ] Test covers the intended functionality
- [ ] Test is isolated and independent
- [ ] Test uses appropriate fixtures
- [ ] Test has clear assertions
- [ ] Test is properly documented
- [ ] Test follows naming conventions
- [ ] Test is marked appropriately

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Mocking in Python](https://docs.python.org/3/library/unittest.mock.html)
