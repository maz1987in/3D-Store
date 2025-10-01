# Product Module

The Product module manages all product-related functionality in the 3D Store application, including both custom 3D printing services and ready-made products.

## Overview

This module handles:
- Product catalog management
- Custom 3D printing services
- Ready-made products
- Product categories and classifications
- Pricing and cost calculations
- Product specifications and attributes
- Inventory tracking for ready-made products

## Module Structure

```
product/
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

### Product
Main product entity with the following key attributes:
- **Basic Info**: `name`, `description`, `price`, `category_id`
- **3D Printing**: `is_custom`, `print_settings`, `materials`, `estimated_print_time`
- **Inventory**: `stock_quantity`, `reorder_level`, `is_available`
- **Media**: `images`, `3d_models`, `thumbnails`
- **Metadata**: `created_at`, `updated_at`, `is_active`

### ProductCategory
Product classification system:
- **Hierarchical**: Supports parent-child relationships
- **Multilingual**: Name and description in multiple languages
- **Attributes**: Custom attributes per category
- **SEO**: Meta tags and URL slugs

### ProductMaterial
3D printing materials and specifications:
- **Material Types**: PLA, ABS, PETG, TPU, etc.
- **Properties**: Color, finish, strength, flexibility
- **Pricing**: Cost per gram/unit
- **Compatibility**: Printer compatibility matrix

### PrintSettings
3D printing configuration:
- **Layer Height**: Print resolution settings
- **Infill**: Density and pattern options
- **Support**: Support structure requirements
- **Temperature**: Nozzle and bed temperature settings

## Repository Layer

The `ProductRepository` class provides data access operations for the Product module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Product]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(product_id)` - Get product by ID
- `create(product_data)` - Create new product
- `update(product_id, product_data)` - Update existing product
- `delete(product_id)` - Delete product
- `get_all(limit, offset)` - Get all products with pagination

#### Advanced Query Methods
- `get_products_with_category(filter_obj)` - Products with category information
- `get_product_with_details(product_id)` - Product with all related details
- `get_products_by_type(product_type)` - Products by type (service, ready_made, material)
- `get_products_by_category(category_id)` - Products in specific category
- `get_products_by_supplier(supplier_id)` - Products from specific supplier
- `get_featured_products(limit)` - Featured products
- `get_active_products()` - Active products only
- `search_products(search_term)` - Search products by title/description
- `get_products_by_price_range(min_price, max_price)` - Products in price range
- `get_digital_products()` - Digital products only
- `get_products_by_availability(in_stock)` - Products by availability

#### Statistics and Analytics
- `get_product_statistics()` - Product statistics for dashboard
- `update_product_rating(product_id, new_rating)` - Update product rating

### Usage Example

```python
from app.product.repository import ProductRepository

# Initialize repository
product_repo = ProductRepository()

# Get products with filtering and pagination
filter_obj = FilterObj()
result = product_repo.get_products_with_category(filter_obj)

# Get products by type
service_products = product_repo.get_products_by_type('service')

# Search products
search_results = product_repo.search_products("3D printer")

# Get featured products
featured = product_repo.get_featured_products(limit=5)
```

## API Endpoints

### Product Management
- `GET /products` - List all products with filtering and pagination
- `GET /products/{id}` - Get product details
- `POST /products` - Create new product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product (soft delete)

### Product Categories
- `GET /products/categories` - List all categories
- `GET /products/categories/{id}` - Get category details
- `POST /products/categories` - Create new category
- `PUT /products/categories/{id}` - Update category
- `DELETE /products/categories/{id}` - Delete category

### Product Materials
- `GET /products/materials` - List available materials
- `GET /products/materials/{id}` - Get material details
- `POST /products/materials` - Add new material
- `PUT /products/materials/{id}` - Update material

### Print Settings
- `GET /products/print-settings` - List print settings
- `GET /products/print-settings/{id}` - Get print settings
- `POST /products/print-settings` - Create print settings
- `PUT /products/print-settings/{id}` - Update print settings

## Business Logic

### Product Creation
1. **Validation**: Validate product data using schemas
2. **Category Assignment**: Ensure category exists and is valid
3. **Material Validation**: Verify material compatibility
4. **Price Calculation**: Calculate base price and markup
5. **Media Upload**: Handle product images and 3D models
6. **Inventory Setup**: Initialize stock levels for ready-made products

### Custom 3D Printing Products
- **File Upload**: Accept 3D model files (STL, OBJ, etc.)
- **Model Validation**: Verify file format and geometry
- **Cost Estimation**: Calculate printing cost based on material and settings
- **Print Time Estimation**: Estimate printing duration
- **Compatibility Check**: Ensure printer compatibility

### Ready-Made Products
- **Inventory Management**: Track stock levels
- **Reorder Alerts**: Notify when stock is low
- **Availability Status**: Real-time availability updates
- **Bulk Operations**: Support for bulk updates

### Pricing Strategy
- **Base Pricing**: Material cost + labor cost + overhead
- **Dynamic Pricing**: Adjust based on demand and complexity
- **Bulk Discounts**: Volume-based pricing tiers
- **Promotional Pricing**: Time-limited offers and discounts

## Validation Schemas

### ProductCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "price": "decimal (required, min 0)",
    "category_id": "uuid (required)",
    "is_custom": "boolean (default false)",
    "materials": "array of material IDs",
    "print_settings": "print settings object",
    "stock_quantity": "integer (for ready-made products)",
    "images": "array of image URLs"
}
```

### ProductUpdateSchema
```python
{
    "name": "string (optional, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "price": "decimal (optional, min 0)",
    "is_active": "boolean (optional)",
    "stock_quantity": "integer (optional)",
    "materials": "array of material IDs (optional)"
}
```

## Error Handling

The module uses the comprehensive error handling system:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When product/category not found
- **BusinessLogicException**: For business rule violations
- **FileUploadException**: For media upload errors

## Dependencies

- **Database**: SQLAlchemy models and queries
- **File Storage**: Media upload and management
- **Validation**: Marshmallow schemas
- **Authentication**: JWT token validation
- **Authorization**: Role-based access control
- **Caching**: Redis for performance optimization

## Usage Examples

### Creating a Custom 3D Printing Product
```python
from app.product.service import ProductService
from app.product.schemas import ProductCreateSchema

service = ProductService()
product_data = {
    "name": "Custom Phone Case",
    "description": "Personalized phone case with custom design",
    "price": 25.99,
    "category_id": "phone-accessories-uuid",
    "is_custom": True,
    "materials": ["pla-white-uuid", "pla-black-uuid"],
    "print_settings": {
        "layer_height": 0.2,
        "infill_percentage": 20,
        "support_enabled": True
    }
}

product = service.create_product(product_data)
```

### Managing Product Inventory
```python
# Update stock quantity
service.update_stock(product_id, new_quantity)

# Check availability
is_available = service.check_availability(product_id, quantity)

# Get low stock alerts
low_stock_products = service.get_low_stock_products()
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frequently accessed products cached in Redis
- **Pagination**: Large product lists paginated for performance
- **Lazy Loading**: Related data loaded on demand
- **Image Optimization**: Compressed and resized product images

## Security

- **Input Validation**: All inputs validated using schemas
- **File Upload Security**: Virus scanning and file type validation
- **Access Control**: Role-based permissions for product management
- **Data Sanitization**: XSS protection for user inputs
- **Rate Limiting**: API endpoints protected against abuse

## Testing

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Load testing for product listings
- **Security Tests**: Input validation and access control testing

## Future Enhancements

- **AI-Powered Recommendations**: Machine learning for product suggestions
- **Dynamic Pricing**: Real-time price adjustments
- **Advanced Search**: Elasticsearch integration for better search
- **Product Variants**: Size, color, and material variations
- **Bulk Import**: CSV/Excel import for large product catalogs
