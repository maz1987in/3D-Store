# Transaction Module

The Transaction module manages inventory movements, stock transfers, and transaction tracking in the 3D Store application, providing comprehensive transaction management capabilities.

## Overview

This module handles:
- Inventory movement tracking
- Stock transfers between locations
- Transaction history and audit trails
- Financial year integration
- Transaction analytics and reporting
- Movement validation and approval

## Module Structure

```
transaction/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── repository.py       # Data access layer (Repository pattern)
├── schemas.py          # Input validation schemas
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Transaction
Main transaction entity with the following key attributes:
- **Basic Info**: `id`, `product_id`, `quantity`, `transaction_type`
- **Locations**: `from_location_id`, `to_location_id`
- **Timestamps**: `transaction_date`, `create_date`, `modified_date`
- **Financial**: `financial_year_id`
- **Metadata**: `notes`, `reference_number`

## Repository Layer

The `TransactionRepository` class provides data access operations for the Transaction module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Transaction]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities (product, locations, fiscal year)
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(transaction_id)` - Get transaction by ID
- `create(transaction_data)` - Create new transaction
- `update(transaction_id, transaction_data)` - Update existing transaction
- `delete(transaction_id)` - Delete transaction
- `get_all(limit, offset)` - Get all transactions with pagination

#### Advanced Query Methods
- `get_transactions_with_details(transaction_id)` - Transaction with all related details
- `get_transactions_by_product(product_id)` - Transactions by product
- `get_transactions_by_type(transaction_type)` - Transactions by type
- `get_transactions_by_location(location_id, location_type)` - Transactions by location
- `get_transactions_by_fiscal_year(fiscal_year_id)` - Transactions by fiscal year
- `get_transactions_by_date_range(start_date, end_date)` - Transactions by date range
- `get_transactions_by_quantity_range(min_quantity, max_quantity)` - Transactions by quantity range
- `get_recent_transactions(limit)` - Recent transactions
- `get_product_movement_summary(product_id)` - Product movement summary
- `get_location_movement_summary(location_id, location_type)` - Location movement summary

#### Statistics and Analytics
- `get_transaction_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.transaction.repository import TransactionRepository

# Initialize repository
transaction_repo = TransactionRepository()

# Get transactions by product
product_transactions = transaction_repo.get_transactions_by_product("product-uuid")

# Get transactions by type
in_transactions = transaction_repo.get_transactions_by_type(TransactionType.IN)

# Get transactions by date range
from datetime import datetime, timezone, timedelta
start_date = datetime.now(timezone.utc) - timedelta(days=30)
end_date = datetime.now(timezone.utc)
recent_transactions = transaction_repo.get_transactions_by_date_range(start_date, end_date)

# Get product movement summary
movement_summary = transaction_repo.get_product_movement_summary("product-uuid")

# Get transaction statistics
stats = transaction_repo.get_transaction_statistics()
```

## API Endpoints

### Transaction Management
- `GET /transactions` - List transactions with filtering
- `GET /transactions/{id}` - Get transaction details
- `POST /transactions` - Create new transaction
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

### Transaction Analytics
- `GET /transactions/statistics` - Get transaction statistics
- `GET /transactions/product/{id}/movement` - Get product movement summary
- `GET /transactions/location/{id}/movement` - Get location movement summary

## Business Logic

### Transaction Creation
1. **Validation**: Validate transaction data and business rules
2. **Location Verification**: Ensure source and destination locations exist
3. **Product Verification**: Verify product exists and is available
4. **Quantity Validation**: Ensure sufficient quantity for outbound transactions
5. **Financial Year**: Associate with current fiscal year
6. **Audit Trail**: Create audit trail for tracking

### Movement Processing
1. **Inventory Update**: Update inventory levels at both locations
2. **Stock Validation**: Ensure stock availability before processing
3. **Location Tracking**: Track movement between branches/stores
4. **Notification**: Notify relevant parties of movement
5. **Documentation**: Generate movement documents

### Reporting and Analytics
1. **Movement Reports**: Generate movement reports by product/location
2. **Trend Analysis**: Analyze movement patterns and trends
3. **Performance Metrics**: Calculate key performance indicators
4. **Audit Reports**: Generate audit reports for compliance

## Integration Points

- **Inventory Module**: Updates inventory levels
- **Financial Module**: Integrates with fiscal year tracking
- **Branch/Store Modules**: Tracks movement between locations
- **Product Module**: Associates with product information
- **Reporting Module**: Provides data for analytics

## Security Considerations

- **Access Control**: Role-based access to transaction operations
- **Audit Trail**: Complete audit trail for all transactions
- **Data Integrity**: Validation to prevent data corruption
- **Approval Workflow**: Multi-level approval for high-value transactions
- **Encryption**: Sensitive data encryption at rest and in transit
