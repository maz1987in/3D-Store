# 3D Store Backend

A comprehensive Flask-based backend application for a 3D printing store management system.

## Features

### Core Functionality
- **User Management**: Authentication, authorization, and user profiles
- **Product Catalog**: 3D printing services, ready-made products, and materials
- **Order Management**: Order processing, tracking, and fulfillment
- **Inventory Management**: Stock tracking and material management
- **Payment Processing**: Multiple payment gateway integration
- **Financial Management**: Invoicing, reporting, and analytics

### Technical Features
- **RESTful API**: Comprehensive REST API with proper HTTP status codes
- **Database Optimization**: Advanced indexing strategy for performance
- **Caching System**: Redis-based caching with optional enable/disable
- **Middleware System**: Authentication, logging, CORS, rate limiting
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Input Validation**: Marshmallow-based validation schemas
- **Repository Pattern**: Clean data access layer separation
- **Service Layer**: Business logic with single responsibility principle
- **Monitoring & Observability**: Comprehensive logging, metrics, health monitoring, and alerting

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis (optional, for caching)
- Node.js 18+ (for frontend)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 3D-Store/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis settings
   ```

5. **Initialize database**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create initial data (optional)
   python scripts/create_initial_data.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## Configuration

### Environment Variables

#### Database Configuration
```bash
DB_TYPE=postgresql
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DATABASE_NAME=store3d
DB_HOST=localhost:5432
```

#### Cache Configuration
```bash
# Enable/disable caching
CACHE_ENABLED=True

# Redis configuration (when CACHE_ENABLED=True)
CACHE_REDIS_HOST=localhost
CACHE_REDIS_PORT=6379
CACHE_REDIS_PASSWORD=your_redis_password
```

#### Security Configuration
```bash
SECRET_KEY=your_secret_key
SECURITY_PASSWORD_SALT=your_salt
```

### Configuration Files

- **`.env`**: Environment variables
- **`config.py`**: Application configuration
- **`alembic.ini`**: Database migration configuration

## Database Optimization

### Indexing Strategy

The application includes a comprehensive database indexing strategy for optimal performance:

#### High Priority Indexes
- User authentication and filtering
- Product catalog search and filtering
- Order management and tracking
- Inventory management
- Transaction tracking

#### Performance Monitoring

Use the provided scripts to monitor and optimize database performance:

```bash
# Analyze current indexes
python scripts/analyze_indexes.py

# Apply performance indexes
python scripts/apply_indexes.py

# Monitor performance
python scripts/monitor_performance.py
```

For detailed information, see [Database Optimization Scripts](scripts/README.md).

## API Documentation

### Authentication
- **POST** `/api/auth/login` - User login
- **POST** `/api/auth/register` - User registration
- **POST** `/api/auth/logout` - User logout
- **GET** `/api/auth/profile` - Get user profile

### Products
- **GET** `/api/products` - List products
- **GET** `/api/products/{id}` - Get product details
- **POST** `/api/products` - Create product
- **PUT** `/api/products/{id}` - Update product
- **DELETE** `/api/products/{id}` - Delete product

### Orders
- **GET** `/api/orders` - List orders
- **GET** `/api/orders/{id}` - Get order details
- **POST** `/api/orders` - Create order
- **PUT** `/api/orders/{id}` - Update order
- **DELETE** `/api/orders/{id}` - Delete order

### Inventory
- **GET** `/api/inventory` - List inventory
- **GET** `/api/inventory/{id}` - Get inventory details
- **POST** `/api/inventory` - Create inventory record
- **PUT** `/api/inventory/{id}` - Update inventory
- **DELETE** `/api/inventory/{id}` - Delete inventory record

### Complete API Documentation
For complete API documentation, see the individual module README files in the `app/` directory.

## Architecture

### Project Structure
```
backend/
├── app/                    # Application code
│   ├── caching/           # Caching system
│   ├── middleware/        # Middleware components
│   ├── exceptions/        # Error handling
│   ├── users/            # User management
│   ├── product/          # Product management
│   ├── order/            # Order management
│   ├── inventory/        # Inventory management
│   └── ...               # Other business modules
├── migrations/           # Database migrations
├── scripts/             # Utility scripts
├── docs/               # Documentation
└── tests/              # Test files
```

### Design Patterns

#### Repository Pattern
- Clean separation of data access logic
- Consistent interface for database operations
- Easy testing and mocking

#### Service Layer Pattern
- Business logic encapsulation
- Single responsibility principle
- Facade pattern for complex operations

#### Middleware Pattern
- Cross-cutting concerns
- Request/response processing
- Authentication and authorization

## Caching System

The application includes a comprehensive caching system with Redis integration:

### Features
- **Optional Caching**: Can be enabled/disabled via configuration
- **Multiple Strategies**: TTL, LRU, Write-Through, Write-Behind
- **Entity-Specific Managers**: Dedicated cache managers for each entity
- **Pattern-Based Invalidation**: Smart cache invalidation
- **Health Monitoring**: Cache health checks and metrics

### Usage
```python
from app.caching import cache_result, cache_invalidate

@cache_result(timeout=3600)
def get_products():
    return Product.query.all()

@cache_invalidate(pattern="product|*")
def update_product(product_id):
    # Update product logic
    pass
```

For detailed information, see [Caching System Documentation](app/caching/README.md).

## Middleware System

The application includes a comprehensive middleware system:

### Components
- **Authentication Middleware**: JWT token validation
- **Logging Middleware**: Request/response logging
- **CORS Middleware**: Cross-origin resource sharing
- **Rate Limiting Middleware**: API rate limiting
- **Security Middleware**: Security headers and threat detection
- **Performance Middleware**: Response time monitoring

For detailed information, see [Middleware System Documentation](app/middleware/README.md).

## Error Handling

The application includes a comprehensive error handling system:

### Features
- **Custom Exception Hierarchy**: Structured exception classes
- **Flask Error Handlers**: Automatic error response formatting
- **Context Managers**: Simplified error handling in business logic
- **Logging Integration**: Detailed error logging

For detailed information, see [Error Handling Documentation](app/exceptions/README.md).

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_users.py

# Run with coverage
python -m pytest --cov=app
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@host:port/db
   export REDIS_URL=redis://host:port
   ```

2. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Apply performance indexes
   python scripts/apply_indexes.py
   ```

3. **Application Deployment**
   ```bash
   # Using Gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   
   # Using Docker
   docker build -t store3d-backend .
   docker run -p 5000:5000 store3d-backend
   ```

### Performance Optimization

1. **Database Indexes**
   - Apply performance indexes
   - Monitor index usage
   - Remove unused indexes

2. **Caching**
   - Enable Redis caching
   - Configure appropriate TTLs
   - Monitor cache hit rates

3. **Monitoring**
   - Set up performance monitoring
   - Configure alerts
   - Regular performance reviews

## Monitoring and Maintenance

### Performance Monitoring
```bash
# Generate performance report
python scripts/monitor_performance.py

# Continuous monitoring
python scripts/monitor_performance.py --continuous --duration 3600
```

### Database Maintenance
```bash
# Analyze database performance
python scripts/analyze_indexes.py

# Apply optimizations
python scripts/apply_indexes.py
```

### Health Checks
- **Application**: `GET /health`
- **Database**: `GET /health/database`
- **Cache**: `GET /cache/health`

## Testing Framework

The project includes a comprehensive testing framework built on pytest:

### Test Categories

- **Unit Tests**: Individual components and functions
- **Integration Tests**: Component interactions and workflows  
- **API Tests**: HTTP endpoints and request/response handling
- **Database Tests**: Data operations and integrity

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest test/test_unit/
python -m pytest test/test_integration/
python -m pytest test/test_api/
python -m pytest test/test_database/

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run tests in parallel
python -m pytest -n 4
```

### Test Configuration

- **Test Database**: In-memory SQLite for fast, isolated testing
- **Fixtures**: Comprehensive fixtures for all major entities
- **Mocking**: Built-in mocks for external dependencies
- **Coverage**: Minimum 80% coverage requirement

### Quality Checks

```bash
# Run all quality checks
python scripts/run_tests.py --quality

# Run specific checks
python scripts/run_tests.py --lint
python scripts/run_tests.py --format
python scripts/run_tests.py --type-check
```

For detailed testing documentation, see [test/README.md](test/README.md).

## Monitoring and Observability

The application includes a comprehensive monitoring and observability system:

### Monitoring Components

- **Structured Logging**: Multi-output logging with JSON formatting
- **Metrics Collection**: System and application performance metrics
- **Health Monitoring**: Comprehensive health checks and status monitoring
- **Performance Tracking**: Request timing and resource usage tracking
- **Error Tracking**: Error aggregation and categorization
- **Alerting**: Multi-channel notification system (Email, Slack, Webhook, SMS)
- **Insights**: Business intelligence and analytics

### Monitoring Endpoints

- **Health**: `GET /health` - Basic health check
- **Metrics**: `GET /monitoring/metrics` - All metrics
- **Performance**: `GET /monitoring/performance` - Performance summary
- **Errors**: `GET /monitoring/errors` - Error summary
- **Alerts**: `GET /monitoring/alerts` - Recent alerts
- **Insights**: `GET /monitoring/insights` - Recent insights
- **Dashboard**: `GET /monitoring/dashboard` - Comprehensive dashboard

### Configuration

```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_CONSOLE_ENABLED=True
LOG_FILE_ENABLED=True

# Alert Configuration
ALERT_EMAIL_SMTP_SERVER=smtp.gmail.com
ALERT_EMAIL_TO=admin@store3d.com,ops@store3d.com
ALERT_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Demo

Run the monitoring demo to see all features in action:

```bash
python app/examples/monitoring_demo.py
```

For detailed monitoring documentation, see [app/monitoring/README.md](app/monitoring/README.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Document new features
- Update README files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Contact the development team

## Changelog

### v1.0.0
- Initial release
- Core functionality implementation
- Database optimization
- Caching system
- Middleware system
- Error handling system
