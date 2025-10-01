# Category Module

The Category module manages product categorization and classification in the 3D Store application, providing a hierarchical structure for organizing products and services.

## Overview

This module handles:
- Hierarchical category management
- Multilingual category support
- Category attributes and metadata
- SEO optimization features
- Category-based product filtering
- Category analytics and reporting

## Module Structure

```
category/
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

### Category
Main category entity with the following key attributes:
- **Basic Info**: `name`, `description`, `slug`, `is_active`
- **Hierarchy**: `parent_id`, `level`, `path` (for tree traversal)
- **Multilingual**: `name_translations`, `description_translations`
- **SEO**: `meta_title`, `meta_description`, `meta_keywords`
- **Visual**: `icon_url`, `image_url`, `color_code`
- **Metadata**: `created_at`, `updated_at`, `sort_order`

### CategoryAttribute
Custom attributes for categories:
- **Attribute Info**: `name`, `type`, `is_required`, `is_filterable`
- **Options**: `attribute_options` (for select/dropdown types)
- **Validation**: `validation_rules`, `min_value`, `max_value`
- **Display**: `display_name`, `help_text`, `sort_order`

### CategoryProduct
Many-to-many relationship between categories and products:
- **Relationships**: `category_id`, `product_id`
- **Metadata**: `is_primary`, `sort_order`, `created_at`

## Repository Layer

The `CategoryRepository` class provides data access operations for the Category module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Category]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(category_id)` - Get category by ID
- `create(category_data)` - Create new category
- `update(category_id, category_data)` - Update existing category
- `delete(category_id)` - Delete category
- `get_all(limit, offset)` - Get all categories with pagination

#### Advanced Query Methods
- `get_categories_with_children()` - Categories with subcategories
- `get_category_with_details(category_id)` - Category with all related details
- `get_root_categories()` - Root categories only
- `get_subcategories(parent_id)` - Subcategories of parent
- `get_categories_by_type(category_type)` - Categories by type
- `get_active_categories()` - Active categories only
- `get_featured_categories()` - Featured categories
- `get_category_by_slug(slug)` - Category by URL slug
- `get_category_by_code(code)` - Category by code
- `get_categories_with_products()` - Categories that have products
- `get_category_hierarchy()` - Complete category hierarchy
- `get_categories_by_commission_rate(min_rate, max_rate)` - Categories by commission rate

#### Statistics and Analytics
- `get_category_statistics()` - Statistics for dashboard/reporting
- `update_category_sort_order(category_id, sort_order)` - Update category sort order

### Usage Example

```python
from app.category.repository import CategoryRepository

# Initialize repository
category_repo = CategoryRepository()

# Get category by ID
category = category_repo.get_by_id("category-uuid")

# Get categories with children
categories_with_children = category_repo.get_categories_with_children()

# Get root categories
root_categories = category_repo.get_root_categories()

# Get category hierarchy
hierarchy = category_repo.get_category_hierarchy()

# Get categories by type
product_categories = category_repo.get_categories_by_type('product')

# Get category statistics
stats = category_repo.get_category_statistics()
```

## API Endpoints

### Category Management
- `GET /categories` - List all categories with tree structure
- `GET /categories/{id}` - Get category details
- `POST /categories` - Create new category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category (soft delete)
- `GET /categories/{id}/children` - Get child categories
- `GET /categories/{id}/products` - Get products in category

### Category Hierarchy
- `GET /categories/tree` - Get full category tree
- `GET /categories/{id}/ancestors` - Get category ancestors
- `GET /categories/{id}/descendants` - Get category descendants
- `POST /categories/{id}/move` - Move category to new parent

### Category Attributes
- `GET /categories/{id}/attributes` - Get category attributes
- `POST /categories/{id}/attributes` - Add attribute to category
- `PUT /categories/{id}/attributes/{attr_id}` - Update category attribute
- `DELETE /categories/{id}/attributes/{attr_id}` - Remove attribute

### Category Analytics
- `GET /categories/{id}/stats` - Get category statistics
- `GET /categories/popular` - Get most popular categories
- `GET /categories/search` - Search categories by name/description

## Business Logic

### Category Creation
1. **Validation**: Validate category data and hierarchy rules
2. **Slug Generation**: Generate URL-friendly slug from name
3. **Path Calculation**: Calculate hierarchical path for tree traversal
4. **Level Assignment**: Assign appropriate level in hierarchy
5. **Sort Order**: Determine sort order among siblings
6. **SEO Setup**: Generate meta tags and descriptions

### Hierarchy Management
1. **Tree Validation**: Ensure valid parent-child relationships
2. **Circular Reference Prevention**: Prevent category loops
3. **Path Updates**: Update paths when moving categories
4. **Level Recalculation**: Recalculate levels after moves
5. **Descendant Updates**: Update all descendants when parent changes

### Multilingual Support
1. **Translation Storage**: Store translations in JSON format
2. **Fallback Logic**: Fallback to default language if translation missing
3. **Translation Validation**: Validate translation completeness
4. **SEO Localization**: Generate localized meta tags

### Category Attributes
1. **Attribute Types**: Support text, number, boolean, select, multi-select
2. **Validation Rules**: Custom validation for each attribute type
3. **Filter Integration**: Make attributes filterable in product search
4. **Inheritance**: Child categories inherit parent attributes

## Validation Schemas

### CategoryCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "parent_id": "uuid (optional)",
    "is_active": "boolean (default true)",
    "icon_url": "string (optional, valid URL)",
    "image_url": "string (optional, valid URL)",
    "color_code": "string (optional, hex color)",
    "meta_title": "string (optional, max 255 chars)",
    "meta_description": "string (optional, max 500 chars)",
    "meta_keywords": "string (optional, max 500 chars)",
    "sort_order": "integer (optional, default 0)"
}
```

### CategoryUpdateSchema
```python
{
    "name": "string (optional, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "is_active": "boolean (optional)",
    "icon_url": "string (optional, valid URL)",
    "image_url": "string (optional, valid URL)",
    "color_code": "string (optional, hex color)",
    "meta_title": "string (optional, max 255 chars)",
    "meta_description": "string (optional, max 500 chars)",
    "meta_keywords": "string (optional, max 500 chars)",
    "sort_order": "integer (optional)"
}
```

### CategoryAttributeSchema
```python
{
    "name": "string (required, max 100 chars)",
    "type": "string (required, enum: text|number|boolean|select|multiselect)",
    "is_required": "boolean (default false)",
    "is_filterable": "boolean (default true)",
    "display_name": "string (required, max 100 chars)",
    "help_text": "string (optional, max 500 chars)",
    "validation_rules": "object (optional)",
    "options": "array of strings (for select/multiselect types)",
    "sort_order": "integer (optional, default 0)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When category not found
- **BusinessLogicException**: For hierarchy rule violations
- **CircularReferenceException**: For invalid parent-child relationships

## Dependencies

- **Product Module**: For category-product relationships
- **Translation Module**: For multilingual support
- **SEO Module**: For meta tag generation
- **File Storage**: For category images and icons
- **Search Module**: For category search functionality

## Usage Examples

### Creating a Category
```python
from app.category.service import CategoryService
from app.category.schemas import CategoryCreateSchema

service = CategoryService()
category_data = {
    "name": "Phone Accessories",
    "description": "3D printed phone cases, stands, and accessories",
    "parent_id": "electronics-uuid",
    "icon_url": "https://example.com/icons/phone.svg",
    "color_code": "#007bff",
    "meta_title": "3D Printed Phone Accessories",
    "meta_description": "Custom 3D printed phone cases and accessories"
}

category = service.create_category(category_data)
```

### Managing Category Hierarchy
```python
# Get category tree
tree = service.get_category_tree()

# Move category to new parent
service.move_category(category_id, new_parent_id)

# Get category ancestors
ancestors = service.get_category_ancestors(category_id)

# Get category descendants
descendants = service.get_category_descendants(category_id)
```

### Category Attributes
```python
# Add attribute to category
attribute_data = {
    "name": "material_type",
    "type": "select",
    "is_required": True,
    "is_filterable": True,
    "display_name": "Material Type",
    "options": ["PLA", "ABS", "PETG", "TPU"]
}

service.add_category_attribute(category_id, attribute_data)

# Get category attributes
attributes = service.get_category_attributes(category_id)
```

### Multilingual Support
```python
# Add translation
service.add_translation(category_id, "ar", {
    "name": "إكسسوارات الهاتف",
    "description": "أغطية هواتف مطبوعة ثلاثية الأبعاد"
})

# Get localized category
category = service.get_category(category_id, locale="ar")
```

## Performance Considerations

- **Tree Caching**: Category tree cached for performance
- **Lazy Loading**: Child categories loaded on demand
- **Database Indexing**: Optimized queries with proper indexes
- **Path Indexing**: Hierarchical path indexed for fast lookups
- **Translation Caching**: Translations cached for quick access

## SEO Features

- **URL Slugs**: SEO-friendly URLs for categories
- **Meta Tags**: Automatic meta tag generation
- **Breadcrumbs**: Hierarchical breadcrumb navigation
- **Sitemap Integration**: Categories included in sitemap
- **Schema Markup**: Structured data for search engines

## Security

- **Input Validation**: All inputs validated using schemas
- **XSS Protection**: User inputs sanitized
- **Access Control**: Role-based permissions for category management
- **SQL Injection Prevention**: Parameterized queries used
- **File Upload Security**: Category images validated and scanned

## Analytics and Reporting

- **Category Statistics**: Product counts, revenue, popularity
- **Hierarchy Analytics**: Category depth, distribution analysis
- **Search Analytics**: Most searched categories
- **Performance Metrics**: Category page load times, conversion rates

## Future Enhancements

- **AI-Powered Categorization**: Automatic product categorization
- **Dynamic Categories**: Rule-based category creation
- **Category Recommendations**: ML-powered category suggestions
- **Visual Category Management**: Drag-and-drop category tree editor
- **Advanced Filtering**: Faceted search with category attributes
