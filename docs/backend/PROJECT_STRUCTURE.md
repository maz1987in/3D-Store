# 3D Store Backend - Project Structure Documentation

## Overview

3D Store Backend is a Flask-based REST API application designed for managing 3D home printing services. The application follows a modular architecture with clear separation of concerns, supporting multiple languages (Arabic/English), payment gateways, and comprehensive business logic for 3D printing project management, order processing, customer service, and print job administration.

The system enables customers to upload 3D models, request printing services, track print jobs, and manage their printing projects while providing administrators with tools to manage printers, materials, pricing, and service operations.

## Project Architecture

### Core Technologies
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM with support for SQLite, MySQL, and PostgreSQL
- **Migrations**: Alembic
- **Authentication**: JWT-based with role-based access control
- **Internationalization**: SQLAlchemy-i18n for multi-language support
- **File Storage**: Depot for 3D model files, print images, and documents
- **Caching**: Flask-Caching with Redis support
- **Task Scheduling**: APScheduler for print job queuing and notifications
- **API Documentation**: Swagger UI
- **3D File Processing**: Support for STL, OBJ, 3MF file formats
- **Print Job Management**: Queue-based print job processing

## Directory Structure

```
3d-store-backend/
├── app/                          # Main application modules
│   ├── __init__.py              # Flask app factory and configuration
│   ├── address/                 # Address management
│   ├── admin/                   # Admin functionality
│   ├── branch/                  # Printing facility management
│   ├── cart/                    # Shopping cart functionality
│   ├── category/                # Product/service categories
│   ├── city/                    # City management
│   ├── common/                  # Shared utilities and constants
│   ├── company/                 # Company information
│   ├── config/                  # Configuration management
│   ├── customers/               # Customer management
│   ├── dashboard/               # Dashboard analytics
│   ├── expense/                 # Expense management (tools, printers, repairs)
│   ├── faq/                     # FAQ management
│   ├── favorite/                # User favorites
│   ├── financial/               # Financial operations
│   ├── inventory/               # Material & ready-product inventory
│   ├── invoices/                # Invoice generation
│   ├── labor/                   # Labor management
│   ├── medias/                  # 3D model files and media handling
│   ├── ompay/                   # OMPay payment gateway
│   ├── order/                   # Print job & order management
│   ├── payment/                 # Payment processing
│   ├── payment_transaction/     # Payment transaction tracking
│   ├── product/                 # Product management (services + ready-made)
│   ├── quotation/               # Quotation system
│   ├── rating/                  # Product/service ratings
│   ├── security/                # Authentication and authorization
│   ├── seller/                  # Seller management & commissions
│   ├── setting/                 # Application settings
│   ├── shipping/                # Shipping management
│   ├── slider/                  # Banner/slider management
│   ├── staff/                   # Staff management
│   ├── store/                   # Store management
│   ├── supplier/                # Material & packaging suppliers
│   ├── templates/               # Email templates
│   ├── templates_content/       # Template content management
│   ├── thawani/                 # Thawani payment gateway
│   ├── transaction/             # Transaction management
│   ├── user_notification/       # User notifications
│   ├── users/                   # User management
│   └── utilities/               # Utility functions
├── alembic/                     # Database migrations
│   ├── versions/                # Migration files
│   ├── env.py                   # Alembic environment
│   └── script.py.mako           # Migration template
```

**Note**: Each business module (e.g., `product/`, `order/`, `category/`, etc.) contains its own `schemas.py` file for input validation. Schemas are co-located with their respective business logic rather than in a central schemas directory.

### 📋 **Critical File Naming Requirements**

**⚠️ IMPORTANT**: The Flask application uses automatic module discovery with strict naming conventions:

1. **Database Models**: Must be in a file named exactly `model.py` (not `models.py`, `print_models.py`, etc.)
2. **API Routes**: Must be in a file named exactly `routes.py` (not `print_routes.py`, `api_routes.py`, etc.)
3. **Business Logic**: Should be in `service.py` (optional but recommended)
4. **API Documentation**: Should be in `swagger.yaml` (optional but recommended)
5. **Input Validation Schemas**: Should be in `schemas.py` (optional but recommended)

The application automatically scans for these files and registers them as Flask blueprints.

### 📋 **Schema Organization Guidelines**

**✅ CORRECT**: Schemas should be co-located with their respective business modules:

```
app/product/
├── model.py          # Database models
├── routes.py         # API endpoints
├── service.py        # Business logic
├── schemas.py        # ✅ Input validation schemas
└── swagger.yaml      # API documentation
```

**❌ WRONG**: Do not create a central schemas directory:

```
app/
├── schemas/          # ❌ AVOID - Central schemas directory
│   ├── product.py
│   ├── order.py
│   └── category.py
```

**✅ CORRECT**: Each module has its own schemas:

```
app/
├── product/
│   └── schemas.py    # ✅ Product validation schemas
├── order/
│   └── schemas.py    # ✅ Order validation schemas
├── category/
│   └── schemas.py    # ✅ Category validation schemas
└── users/
    └── schemas.py    # ✅ User validation schemas
```

#### **Module Structure Example**
```
app/product/
├── model.py          # ✅ REQUIRED - Contains all product-related database models
├── routes.py         # ✅ REQUIRED - Contains all product-related API endpoints
├── service.py        # ✅ RECOMMENDED - Contains business logic
├── schemas.py        # ✅ RECOMMENDED - Contains input validation schemas
└── swagger.yaml      # ✅ RECOMMENDED - Contains API documentation
```

#### **What NOT to do**
```
app/product/
├── models.py         # ❌ WRONG - Will not be auto-discovered
├── print_models.py   # ❌ WRONG - Will not be auto-discovered
├── api_routes.py     # ❌ WRONG - Will not be auto-discovered
├── print_routes.py   # ❌ WRONG - Will not be auto-discovered
└── product_api.py    # ❌ WRONG - Will not be auto-discovered
```
├── logs/                        # Application logs
├── requirements/                # Python dependencies
│   ├── common.txt               # Common dependencies
│   ├── dev.txt                  # Development dependencies
│   ├── prod.txt                 # Production dependencies
│   └── stag.txt                 # Staging dependencies
├── test/                        # Test files
├── config.py                    # Application configuration
├── database.py                  # Database initialization
├── extensions.py                # Flask extensions
├── run.py                       # Application entry point
├── requirements.txt             # Main requirements file
├── alembic.ini                  # Alembic configuration
├── docker-compose.yml           # Docker composition
├── Dockerfile                   # Docker configuration
└── README.md                    # Project documentation
```

## Directory Structure Adaptation

The directory structure is designed to be **modular and adaptable** based on the specific services and features required for your 3D printing business. Here's how it can be customized:

### **Core Required Modules** (Essential for 3D printing business)
- `product/` - Product management (services + ready-made products)
- `order/` - Print job & order management
- `inventory/` - Material & ready-product inventory
- `users/` - User management (customers, staff, sellers)
- `payment/` - Payment processing
- `financial/` - Financial operations
- `expense/` - Expense management (tools, printers, repairs)
- `seller/` - Seller management & commissions

### **Optional Modules** (Based on business needs)
- `quotation/` - If you need quotation system
- `rating/` - If you want customer ratings
- `faq/` - If you need FAQ management
- `slider/` - If you want banner/slider management
- `labor/` - If you need detailed labor tracking

### **Service-Specific Adaptations**

#### **For Basic 3D Printing Service:**
```
Required: product/, order/, inventory/, users/, payment/, financial/
Optional: expense/, seller/, rating/
```

#### **For Full-Service 3D Printing Business:**
```
All modules included for complete business management
```

#### **For Marketplace Model (with sellers):**
```
Required: product/, order/, inventory/, users/, payment/, financial/, seller/
Optional: expense/, rating/, quotation/
```

#### **For Manufacturing Focus:**
```
Required: product/, order/, inventory/, users/, payment/, financial/, expense/, labor/
Optional: seller/, rating/
```

## Module Structure Pattern

Each business module follows a consistent structure:

```
module_name/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask routes/endpoints
├── service.py          # Business logic layer
├── repository.py       # Data access layer (Repository pattern)
├── schemas.py          # Input validation schemas (Marshmallow)
├── swagger.yaml        # API documentation
├── test.py             # Unit Test
└── README.md           # Module-specific documentation
```

### Repository Implementation Guidelines

**File Location**: Each module should have its own `repository.py` file containing the data access layer for that module.

**Base Repository**: All repositories extend `BaseRepository[T]` from `app.repositories.base` which provides common CRUD operations.

**Import Pattern**: Repositories are imported from their respective modules:
```python
from app.product.repository import ProductRepository
from app.order.repository import OrderRepository
```

### Schema Implementation Guidelines

**File Location**: Each module should have its own `schemas.py` file containing all validation schemas for that module.

**Schema Types**:
- **Create Schemas**: For validating data when creating new resources (e.g., `ProductCreateSchema`)
- **Update Schemas**: For validating data when updating existing resources (e.g., `ProductUpdateSchema`)
- **Query Schemas**: For validating query parameters and filters (e.g., `ProductQuerySchema`)
- **Response Schemas**: For standardizing API response formats (e.g., `ProductResponseSchema`)

**Schema Naming Conventions**:
- Use descriptive names that clearly indicate the purpose
- Follow the pattern: `{EntityName}{Action}Schema`
- Examples: `UserCreateSchema`, `OrderUpdateSchema`, `ProductQuerySchema`
- For specialized schemas, use descriptive suffixes: `PrintJobEstimateSchema`, `SellerCommissionSchema`

**Example Schema Structure**:
```python
# app/product/schemas.py
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class ProductCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    category_id = fields.UUID(required=True)
    
    @validates_schema
    def validate_name(self, data, **kwargs):
        if not data.get('name') or not data['name'].strip():
            raise ValidationError('Product name is required', 'name')

class ProductUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    price = fields.Decimal(validate=validate.Range(min=0))
    # ... other fields
```

**Import Pattern in Routes**:
```python
# app/product/routes.py
from .schemas import ProductCreateSchema, ProductUpdateSchema
from app.decorators.validation import validate_json, validate_form_data

@products.route('/', methods=['POST'])
@validate_json(ProductCreateSchema)
def create_product(validated_data):
    # Use validated_data instead of request.json
    pass
```

**Benefits of Co-located Schemas**:
- **Better Maintainability**: Schemas are located with their related business logic
- **Easier Navigation**: Developers can find validation rules in the same folder as the functionality
- **Reduced Coupling**: Each module is self-contained with its own validation
- **Scalability**: New modules can easily add their own schemas without affecting others
- **Clear Ownership**: Each team member can work on their module's schemas independently
- **Consistent Organization**: Follows the same pattern as models, routes, and services

## Core Components

### 1. Application Factory (`app/__init__.py`)

The Flask application is created using the factory pattern with the following key features:

- **Configuration Management**: Loads configuration from multiple sources (environment variables, database)
- **Extension Registration**: Initializes Flask extensions (logging, caching, mail, rate limiting, scheduler)
- **Blueprint Registration**: Dynamically registers all module blueprints
- **Database Initialization**: Sets up database connections and models
- **Error Handling**: Global error handlers for consistent API responses
- **Internationalization**: Multi-language support setup
- **Security**: CORS, JWT authentication, and permission-based access control

### 2. Configuration System (`config.py`)

Comprehensive configuration management with multiple configuration classes:

- **BaseConfig**: Database connections, timezone, JWT settings
- **SecretKey**: Security keys and salts
- **FileUploadConfig**: File upload settings and storage
- **MailConfig**: Email service configuration
- **LogConfig**: Logging configuration
- **SchedulerConfig**: Task scheduling configuration
- **CachingConfig**: Cache configuration (Redis, Memcached)
- **LimiterConfig**: Rate limiting configuration
- **OAuthConfig**: OAuth providers (Google, Twitter, Apple)
- **ThawaniConfig**: Thawani payment gateway
- **OMPayConfig**: OMPay payment gateway

### 3. Database Layer (`database.py`)

- **Session Management**: Scoped sessions for thread safety
- **Model Initialization**: Automatic model discovery and registration
- **Connection Pooling**: Configurable connection pooling
- **Multi-database Support**: SQLite, MySQL, PostgreSQL

### 4. Security System (`app/security/`)

- **Authentication**: JWT-based authentication with token validation
- **Authorization**: Role-based access control (RBAC)
- **Permissions**: Granular permission system
- **OAuth Integration**: Google, Twitter, Apple OAuth support

## Key Business Modules

### 1. User Management (`app/users/`)

**Models:**
- `User`: Core user entity with authentication, profile, and preferences
- `Role`: User roles for access control (Customer, Printer Operator, Admin, Manager)
- `Permission`: Granular permissions for 3D printing operations
- `UserRoles`: Many-to-many relationship between users and roles
- `RolePermission`: Many-to-many relationship between roles and permissions
- `Tracking`: Login tracking and audit trail

**Features:**
- User registration and authentication for customers and staff
- OAuth integration (Google, Twitter, Apple)
- Role-based access control for different user types
- User profile management with printing preferences
- Password management and account verification
- Customer printing history and preferences tracking

### 2. Product Management (`app/product/`)

**Models:**
- `Product`: 3D printing services and ready-made products with pricing
- `ProductTranslation`: Multi-language product information
- `ProductShippingCity`: Service-specific shipping costs by city
- `PrintMaterial`: Available printing materials (PLA, ABS, PETG, etc.)
- `PrintSettings`: Print quality and material settings
- `ProductPackaging`: Packaging options and costs (keychain, wrapper, tag)
- `ReadyProduct`: Ready-made printed items inventory
- `ProductCostBreakdown`: Detailed cost analysis (print + packaging + finishing)

**Features:**
- 3D printing service catalog management
- Ready-made product inventory management
- Multi-language service and product descriptions
- Service categorization by complexity and material
- Material inventory and availability tracking
- Service and product ratings and customer reviews
- Dynamic pricing based on material, complexity, and packaging
- Print time estimation
- Packaging cost calculation and tracking
- Ready-made product stock management
- Complete product lifecycle tracking

### 3. Print Job & Order Management (`app/order/`)

**Models:**
- `Order`: Print job entity with status tracking and printer assignments
- `PrintJob`: Individual print job details with 3D model files
- `PrintJobStatus`: Status tracking (Uploaded, Queued, Printing, Completed, Failed)
- `PrintJobMaterial`: Material specifications for each print job
- `OrderItem`: Order line items (custom prints, ready-made products)
- `OrderPackaging`: Packaging requirements and costs per order
- `OrderFulfillment`: Complete order fulfillment tracking

**Features:**
- Print job creation and management
- 3D model file upload and validation
- Print job status tracking and notifications
- Printer assignment and queue management
- Print job history and reporting
- Real-time print progress updates
- Print quality control and feedback
- Ready-made product order processing
- Packaging and finishing workflow
- Complete order fulfillment tracking

### 4. Material & Printer Management (`app/inventory/`)

**Models:**
- `Inventory`: Material inventory tracking across printing locations
- `Printer`: 3D printer specifications and status
- `PrinterMaterial`: Available materials for each printer
- `MaterialUsage`: Material consumption tracking per print job

**Features:**
- Multi-location material inventory tracking
- Material quantity alerts and reorder notifications
- Printer status monitoring and maintenance tracking
- Material consumption tracking per print job
- Printer capacity and availability management
- Material waste and cost tracking

### 5. Payment Processing

**Modules:**
- `app/payment/`: Core payment processing for print services
- `app/payment_transaction/`: Transaction tracking for print jobs
- `app/thawani/`: Thawani payment gateway integration
- `app/ompay/`: OMPay payment gateway integration

**Features:**
- Multiple payment gateway support for print service payments
- Transaction tracking and history for print jobs
- Payment status management with print job status integration
- Webhook handling for payment confirmations
- Deposit and final payment processing for large print jobs
- Refund processing for failed or cancelled prints

### 6. Seller Management (`app/seller/`)

**Models:**
- `Seller`: Seller profile and business information
- `SellerCommission`: Commission rates and agreements per seller
- `SellerPerformance`: Sales performance and statistics
- `SellerPayment`: Commission payments and settlements
- `SellerDocument`: Business documents and agreements

**Features:**
- Seller registration and profile management
- Commission rate configuration and agreements
- Seller dashboard with sales analytics
- Commission calculation and tracking
- Flexible settlement periods (Weekly, Bi-weekly, Monthly, Quarterly)
- Payment processing for seller commissions
- Seller performance monitoring and reporting
- Document management for agreements and contracts
- Seller verification and approval workflow
- Minimum payout threshold configuration
- Automated settlement processing

### 7. Expense Management (`app/expense/`)

**Models:**
- `Expense`: Core expense entity with categorization and approval
- `ExpenseCategory`: Expense categories (Equipment, Maintenance, Materials, etc.)
- `ExpenseApproval`: Multi-level approval workflow for expenses
- `ExpenseAttachment`: Receipts and supporting documents
- `ExpenseBudget`: Budget allocation and tracking per category

**Features:**
- Comprehensive expense tracking and categorization
- Multi-level approval workflow for different expense amounts
- Receipt and document attachment management
- Budget tracking and alerts
- Expense reporting and analytics
- Integration with financial management system
- Mobile receipt capture and upload
- Automated expense categorization using AI/ML

### 8. Financial Management (`app/financial/`)

**Features:**
- Financial reporting for print service revenue
- Transaction management for print job payments
- Invoice generation for completed print jobs
- Expense tracking for materials, maintenance, and operational costs
- Profit margin analysis per print job
- Cost calculation based on material usage and print time
- Seller commission tracking and payments
- Expense budget management and reporting

## Database Schema

### Core Tables

1. **Users & Authentication**
   - `users`: User accounts and profiles
   - `roles`: User roles
   - `permissions`: System permissions
   - `user_roles`: User-role relationships
   - `role_permissions`: Role-permission relationships
   - `login_tracking`: Authentication audit trail

2. **Products & Services**
   - `product`: 3D printing services and ready-made products catalog
   - `product_translations`: Multi-language service and product descriptions
   - `category`: Service categories (Prototyping, Production, Art, etc.)
   - `category_translations`: Multi-language category data
   - `print_material`: Available printing materials
   - `print_settings`: Print quality and material settings
   - `product_packaging`: Packaging options and costs
   - `ready_product`: Ready-made printed items inventory
   - `product_cost_breakdown`: Detailed cost analysis per product
   - `supplier`: Material and packaging suppliers

3. **Print Jobs & Materials**
   - `inventory`: Material and ready-product stock levels by location
   - `order`: Print job and product orders
   - `print_job`: Individual print job details
   - `print_job_status`: Print job status tracking
   - `order_item`: Order line items (custom prints, ready products)
   - `order_packaging`: Packaging requirements and costs
   - `transaction`: Material usage and product sales transactions
   - `printer`: 3D printer specifications and status
   - `branch`: Printing facility locations
   - `store`: Service locations

4. **Seller Management**
   - `seller`: Seller profiles and business information
   - `seller_commission`: Commission rates and agreements
   - `seller_performance`: Sales performance and statistics
   - `seller_payment`: Commission payments and settlements
   - `seller_document`: Business documents and agreements
   - `seller_verification`: Seller verification status and documents

5. **Financial**
   - `invoices`: Generated invoices for print services
   - `payment_transaction`: Payment records for print jobs
   - `expense`: Material and operational expense tracking
   - `print_job_costing`: Cost calculation per print job
   - `seller_commission_transaction`: Commission payment transactions

6. **Expense Management**
   - `expense`: Core expense records with categorization
   - `expense_category`: Expense categories and subcategories
   - `expense_approval`: Multi-level approval workflow
   - `expense_attachment`: Receipts and supporting documents
   - `expense_budget`: Budget allocation and tracking
   - `expense_vendor`: Vendor/supplier information for expenses

7. **System**
   - `app_setting`: Application configuration
   - `media`: 3D model files and print image storage metadata
   - `user_notification`: Print job status notifications
   - `templates_content`: Email/SMS templates for print job updates
   - `print_queue`: Print job queue management
   - `print_logs`: Print job execution logs

## API Architecture

### URL Structure
- Base URL: `/3dstore/api/v1/`
- Module-specific endpoints: `/3dstore/api/v1/{module}/`
- Authentication: JWT tokens in headers (`x-access-tokens`)
- Print job endpoints: `/3dstore/api/v1/print-jobs/`
- 3D model upload: `/3dstore/api/v1/upload/model/`
- Seller endpoints: `/3dstore/api/v1/sellers/`
- Seller dashboard: `/3dstore/api/v1/sellers/dashboard/`
- Commission management: `/3dstore/api/v1/sellers/commissions/`
- Expense management: `/3dstore/api/v1/expenses/`
- Expense approval: `/3dstore/api/v1/expenses/approval/`
- Budget management: `/3dstore/api/v1/expenses/budget/`

### Response Format
```json
{
  "data": {...},
  "message": "Success",
  "status": 200
}
```

### Error Handling
- Consistent error response format
- HTTP status codes for different error types
- Detailed error messages for debugging

## Internationalization

- **Supported Languages**: Arabic (default), English
- **Implementation**: SQLAlchemy-i18n for database translations
- **Translation Tables**: `{table}_translations` for each translatable entity
- **Locale Management**: Configurable default locale and available locales

## 3D Printing Workflow

### Customer Journey
1. **Product Selection**: Choose between custom 3D printing service or ready-made products
2. **Custom Print Process**:
   - Model Upload: Customers upload 3D model files (STL, OBJ, 3MF)
   - Service Selection: Choose printing service, material, and quality settings
   - Packaging Selection: Choose packaging options (keychain, wrapper, tag, etc.)
   - Quote Generation: System calculates pricing based on material, complexity, print time, and packaging
3. **Order Placement**: Customer places order with payment
4. **Production Process**:
   - Print Job Creation: System creates print job and assigns to available printer
   - Print Monitoring: Real-time status updates during printing process
   - Quality Control: Post-print inspection and customer approval
   - Packaging & Finishing: Apply selected packaging and finishing touches
5. **Delivery/Shipping**: Completed products are packaged and shipped

### Ready-Made Product Workflow
1. **Product Creation**: Design and print products for inventory
2. **Packaging & Finishing**: Apply standard packaging and quality control
3. **Inventory Management**: Track stock levels and reorder points
4. **Customer Purchase**: Direct purchase from ready-made inventory
5. **Order Fulfillment**: Pick, pack, and ship ready-made products

### Print Job Lifecycle
- **Uploaded**: 3D model file uploaded and validated
- **Queued**: Print job added to printer queue
- **Preparing**: Printer preparation and material loading
- **Printing**: Active printing process with progress tracking
- **Post-Processing**: Cleaning, support removal, finishing
- **Quality Check**: Inspection and quality control
- **Packaging**: Apply selected packaging (keychain, wrapper, tag)
- **Completed**: Print job finished and ready for pickup/shipping
- **Failed**: Print job failed due to technical issues

### Product Cost Breakdown
- **Printing Costs**: Material usage, print time, electricity
- **Packaging Costs**: Keychain, wrapper, tag, box, labels
- **Finishing Costs**: Post-processing, cleaning, quality control
- **Labor Costs**: Setup, monitoring, packaging, quality control
- **Overhead Costs**: Equipment depreciation, facility costs
- **Total Product Cost**: Sum of all cost components
- **Profit Margin**: Selling price minus total cost

### Seller Workflow & Commission Management
1. **Seller Registration**:
   - Business information submission
   - Document verification (business license, tax ID)
   - Commission agreement setup
   - Account approval process

2. **Commission Configuration**:
   - Base commission rate setup
   - Performance-based tier adjustments
   - Special agreement terms
   - Payment schedule configuration

3. **Sales Process**:
   - Seller refers customers to platform
   - Customer places print orders
   - System tracks seller attribution
   - Commission calculation in real-time

4. **Commission Processing**:
   - Flexible settlement periods (Weekly, Bi-weekly, Monthly, Quarterly)
   - Automated commission calculations based on selected period
   - Performance review and tier adjustments
   - Payment processing and settlement
   - Detailed reporting and analytics
   - Minimum payout thresholds to reduce transaction costs

### Expense Management Workflow
1. **Expense Categories**:
   - **Equipment**: New printers, tools, hardware upgrades
   - **Maintenance**: Printer repairs, calibration, parts replacement
   - **Materials**: Filaments, resins, support materials, cleaning supplies
   - **Utilities**: Electricity, internet, facility maintenance
   - **Software**: 3D modeling software, slicing software, licenses
   - **Marketing**: Advertising, promotional materials, website maintenance
   - **Professional Services**: Legal, accounting, consulting fees
   - **Travel**: Business travel, conferences, training
   - **Office Supplies**: Stationery, furniture, general supplies

2. **Expense Submission**:
   - Mobile receipt capture and upload
   - Manual expense entry with categorization
   - Vendor information and invoice details
   - Project/job association for tracking

3. **Approval Workflow**:
   - **Small Expenses** (< $100): Manager approval
   - **Medium Expenses** ($100 - $500): Department head approval
   - **Large Expenses** ($500 - $2000): Director approval
   - **Major Expenses** (> $2000): CEO/owner approval
   - **Emergency Expenses**: Expedited approval process

4. **Budget Management**:
   - Monthly/quarterly budget allocation per category
   - Real-time budget tracking and alerts
   - Budget variance reporting
   - Approval required for over-budget expenses

## File Storage

- **Storage Backend**: Depot with support for local and cloud storage
- **File Types**: 3D model files (STL, OBJ, 3MF), print images, documents, attachments
- **Upload Configuration**: Configurable file size limits and allowed 3D file types
- **Media Management**: Centralized media handling in `app/medias/`
- **3D Model Processing**: File validation, mesh repair, and optimization

## Caching Strategy

- **Cache Backend**: Redis (production), SimpleCache (development)
- **Cache Keys**: Prefixed with configurable prefix
- **Cache TTL**: Configurable timeout values
- **Cached Data**: User permissions, frequently accessed data, print job status, material availability

## Task Scheduling

- **Scheduler**: APScheduler with Redis backend
- **Job Storage**: Redis for distributed scheduling
- **Task Types**: Background jobs, periodic tasks, print job processing, status notifications
- **Configuration**: Configurable timezone and job stores

## Logging

- **Log Levels**: Configurable (DEBUG, INFO, WARNING, ERROR)
- **Log Formats**: JSON and text formats
- **Log Rotation**: Configurable file size and retention
- **Log Types**: Application logs, access logs, error logs, print job logs, printer status logs

## Development Workflow

### Environment Setup
1. Create virtual environment: `python -m venv env`
2. Activate environment: `source env/bin/activate` (Linux/Mac) or `.\env\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start application: `python run.py`

### Database Migrations
- **Migration Tool**: Alembic
- **Migration Location**: `alembic/versions/`
- **Migration Commands**: 
  - Create: `alembic revision --autogenerate -m "description"`
  - Apply: `alembic upgrade head`
  - Rollback: `alembic downgrade -1`

### Docker Support
- **Dockerfile**: Multi-stage build for production
- **Docker Compose**: Development environment setup
- **Containerization**: Application and database containers

## Security Features

1. **Authentication**
   - JWT-based authentication
   - Token expiration and refresh
   - OAuth integration

2. **Authorization**
   - Role-based access control
   - Permission-based endpoint protection
   - Resource-level permissions

3. **Data Protection**
   - Password hashing with PBKDF2
   - Input validation and sanitization
   - SQL injection prevention

4. **Rate Limiting**
   - Configurable rate limits
   - IP-based limiting
   - API endpoint protection

## Monitoring and Observability

1. **Logging**
   - Structured logging with configurable formats
   - Request/response logging
   - Error tracking and reporting

2. **Error Tracking**
   - Sentry integration for error monitoring
   - Custom error handlers
   - Error reporting and alerting

3. **Performance Monitoring**
   - Database query optimization
   - Cache performance monitoring
   - API response time tracking

## Deployment

### Production Considerations
- **Environment Variables**: Secure configuration management
- **Database**: Production-grade database (MySQL/PostgreSQL)
- **Caching**: Redis for session and data caching
- **File Storage**: Cloud storage for media files
- **SSL/TLS**: HTTPS enforcement
- **Load Balancing**: Multiple application instances

### Scaling
- **Horizontal Scaling**: Multiple application instances
- **Database Scaling**: Read replicas, connection pooling
- **Cache Scaling**: Redis cluster
- **File Storage**: CDN integration

## API Documentation

- **Swagger UI**: Available at `/api/docs`
- **OpenAPI Specification**: Generated from code annotations
- **Interactive Documentation**: Test endpoints directly from browser
- **Module Documentation**: Individual Swagger files per module

## Testing

- **Test Structure**: `test/` directory
- **Test Types**: Unit tests, integration tests
- **Test Database**: Separate test database configuration
- **Test Coverage**: Comprehensive test coverage for critical paths

## Maintenance

### Regular Tasks
- **Database Maintenance**: Regular backups, index optimization
- **Log Rotation**: Automated log file management
- **Security Updates**: Regular dependency updates
- **Performance Monitoring**: Regular performance audits

### Backup Strategy
- **Database Backups**: Automated daily backups
- **File Backups**: Media file backup to cloud storage
- **Configuration Backups**: Environment configuration backup

## 3D Printing Service Features

### Core 3D Printing Capabilities
- **Multi-Material Support**: PLA, ABS, PETG, TPU, Wood-filled, Metal-filled filaments
- **Print Quality Options**: Draft, Standard, High Quality, Ultra High Quality
- **Build Volume Management**: Support for various printer sizes and capabilities
- **Print Time Estimation**: Accurate time calculations based on model complexity
- **Cost Calculation**: Dynamic pricing based on material usage, print time, complexity, and packaging
- **File Format Support**: STL, OBJ, 3MF with automatic validation and repair
- **Print Preview**: 3D visualization of print jobs before processing
- **Packaging Options**: Keychain, wrapper, tag, custom packaging solutions
- **Ready-Made Products**: Pre-printed inventory for immediate sale

### Quality Control & Monitoring
- **Real-time Print Monitoring**: Live status updates during printing
- **Quality Inspection**: Post-print quality checks and customer approval
- **Print Failure Detection**: Automatic detection of print failures
- **Material Usage Tracking**: Precise tracking of material consumption
- **Printer Maintenance**: Scheduled maintenance and status monitoring

### Customer Experience
- **Model Upload Interface**: Easy 3D model file upload and validation
- **Quote System**: Instant pricing based on model analysis and packaging options
- **Order Tracking**: Real-time order and print job status updates
- **Print Gallery**: Showcase of completed prints and customer projects
- **Ready-Made Store**: Browse and purchase pre-printed products
- **Packaging Selection**: Choose from various packaging options (keychain, wrapper, tag)
- **Customer Support**: Integrated support system for print-related queries

### Seller Management & Commission System
- **Seller Registration**: Complete seller onboarding with business verification
- **Commission Configuration**: Flexible commission rates based on agreement terms
- **Seller Dashboard**: Comprehensive analytics and performance tracking
- **Commission Tracking**: Real-time commission calculation and payment processing
- **Performance Analytics**: Sales metrics, customer acquisition, and revenue tracking
- **Document Management**: Agreement storage and verification document handling
- **Payment Processing**: Automated commission payments and settlement tracking
- **Multi-tier Commission**: Support for different commission rates based on performance levels

### Settlement Options for Sellers
- **Weekly Settlement**: Every Friday for high-volume sellers
- **Bi-weekly Settlement**: Every other Friday for regular sellers
- **Monthly Settlement**: First business day of each month (most common)
- **Quarterly Settlement**: Every 3 months for low-volume sellers
- **Minimum Payout Threshold**: Configurable minimum amount (e.g., $50, $100) before settlement
- **Settlement Methods**: Bank transfer, PayPal, or other payment gateways
- **Settlement Reports**: Detailed breakdown of commissions earned and paid

### Expense Management & Analytics
- **Real-time Expense Tracking**: Live monitoring of all business expenses
- **Category-wise Analysis**: Detailed breakdown by expense categories
- **Budget vs Actual Reporting**: Monthly/quarterly budget variance analysis
- **Vendor Management**: Track expenses by supplier/vendor
- **Project Cost Allocation**: Associate expenses with specific print jobs/projects
- **Expense Trends**: Historical analysis and forecasting
- **Approval Status Tracking**: Monitor pending and approved expenses
- **Receipt Management**: Digital storage and retrieval of all receipts
- **Tax Reporting**: Generate reports for tax purposes and compliance
- **Cost Center Analysis**: Track expenses by department/location

### Product & Packaging Management
- **Complete Cost Tracking**: Print + packaging + finishing costs per product
- **Packaging Options**: Keychain, wrapper, tag, custom packaging solutions
- **Ready-Made Inventory**: Pre-printed product stock management
- **Cost Breakdown Analysis**: Detailed cost analysis for pricing optimization
- **Packaging Cost Calculator**: Dynamic packaging cost calculation
- **Product Lifecycle Management**: From design to print to packaging to sale
- **Inventory Reorder Points**: Automated alerts for low stock levels
- **Product Performance Analytics**: Track best-selling products and trends

This documentation provides a comprehensive overview of the 3D Store Backend project structure, architecture, and implementation details. The modular design allows for easy maintenance, scaling, and feature additions while maintaining code quality and consistency for 3D printing service management.
