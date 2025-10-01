# Store Module

The Store module manages retail store locations, store operations, and store-specific inventory in the 3D Store application, providing comprehensive store management capabilities.

## Overview

This module handles:
- Store location management
- Store-specific inventory tracking
- Store performance monitoring
- Store staff management
- Store operations and scheduling
- Multi-store support and coordination

## Module Structure

```
store/
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

### Store
Main store entity with the following key attributes:
- **Basic Info**: `id`, `location`, `manager`
- **Timestamps**: `create_date`, `modified_date`
- **Metadata**: `is_active`, `store_code`

## Repository Layer

The `StoreRepository` class provides data access operations for the Store module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Store]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(store_id)` - Get store by ID
- `create(store_data)` - Create new store
- `update(store_id, store_data)` - Update existing store
- `delete(store_id)` - Delete store
- `get_all(limit, offset)` - Get all stores with pagination

#### Advanced Query Methods
- `get_store_by_location(location)` - Store by location
- `get_store_by_manager(manager)` - Store by manager
- `search_stores(search_term)` - Search stores

#### Statistics and Analytics
- `get_store_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.store.repository import StoreRepository

# Initialize repository
store_repo = StoreRepository()

# Get store by ID
store = store_repo.get_by_id("store-uuid")

# Get store by location
store = store_repo.get_store_by_location("Mall Location")

# Search stores
search_results = store_repo.search_stores("mall")

# Get store statistics
stats = store_repo.get_store_statistics()
```

## API Endpoints

### Store Management
- `GET /stores` - List all stores
- `GET /stores/{id}` - Get store details
- `POST /stores` - Create new store
- `PUT /stores/{id}` - Update store
- `DELETE /stores/{id}` - Deactivate store

### Store Operations
- `GET /stores/{id}/inventory` - Get store inventory
- `GET /stores/{id}/staff` - Get store staff
- `GET /stores/{id}/performance` - Get store performance metrics

## Business Logic

### Store Creation
1. **Validation**: Validate store data and location
2. **Manager Assignment**: Assign store manager
3. **Inventory Setup**: Initialize store inventory
4. **Staff Assignment**: Assign initial staff members
5. **Configuration**: Set up store-specific configurations

### Store Operations
1. **Inventory Management**: Track store-specific inventory
2. **Staff Management**: Manage store staff assignments
3. **Performance Tracking**: Monitor store performance metrics
4. **Reporting**: Generate store-specific reports

## Integration Points

- **Inventory Module**: Manages store-specific inventory
- **Staff Module**: Handles store staff assignments
- **Branch Module**: Coordinates with branch operations
- **Reporting Module**: Provides store performance data

## Security Considerations

- **Access Control**: Role-based access to store operations
- **Data Privacy**: Protect sensitive store information
- **Audit Trail**: Track all store-related changes
- **Multi-tenancy**: Support for multiple store locations
