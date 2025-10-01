# Company Module

The Company module manages company information, settings, and configuration in the 3D Store application, providing comprehensive company management capabilities.

## Overview

This module handles:
- Company profile and information management
- Company settings and configuration
- Business registration and compliance
- Company branding and customization
- Multi-company support and management
- Company analytics and reporting
- Company user management

## Module Structure

```
company/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Company
Main company entity with the following key attributes:
- **Basic Info**: `company_id`, `name`, `legal_name`, `company_code`
- **Business**: `business_type`, `industry`, `registration_number`, `tax_id`
- **Contact**: `email`, `phone`, `website`, `contact_person`
- **Address**: `headquarters_address`, `billing_address`, `shipping_address`
- **Branding**: `logo_url`, `brand_colors`, `theme_settings`
- **Settings**: `timezone`, `currency`, `language`, `date_format`
- **Status**: `is_active`, `is_verified`, `verification_status`
- **Metadata**: `created_at`, `updated_at`, `last_activity`

### CompanySettings
Company-specific settings and configuration:
- **Settings Info**: `company_id`, `setting_key`, `setting_value`, `setting_type`
- **Category**: `category`, `subcategory`, `is_public`
- **Validation**: `validation_rules`, `default_value`
- **Metadata**: `created_at`, `updated_at`, `updated_by`

### CompanyUser
Company user management and roles:
- **User Info**: `company_id`, `user_id`, `role`, `permissions`
- **Access**: `access_level`, `department`, `is_admin`
- **Status**: `is_active`, `joined_at`, `last_activity`
- **Metadata**: `created_at`, `updated_at`

### CompanyBranding
Company branding and customization:
- **Branding Info**: `company_id`, `logo_url`, `favicon_url`, `banner_url`
- **Colors**: `primary_color`, `secondary_color`, `accent_color`
- **Typography**: `font_family`, `font_size`, `heading_font`
- **Layout**: `layout_style`, `sidebar_style`, `theme_mode`
- **Customization**: `custom_css`, `custom_js`, `custom_html`
- **Metadata**: `created_at`, `updated_at`

### CompanyAnalytics
Company analytics and insights:
- **Analytics Info**: `company_id`, `period`, `total_users`, `total_orders`
- **Metrics**: `revenue`, `growth_rate`, `user_engagement`
- **Performance**: `order_fulfillment_rate`, `customer_satisfaction`
- **Trends**: `revenue_trend`, `user_trend`, `order_trend`
- **Metadata**: `calculated_at`, `created_at`



## Repository Layer

The `CompanyRepositoryRepository` class provides data access operations for the Company module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Company]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(entity_id)` - Get entity by ID
- `create(entity_data)` - Create new entity
- `update(entity_id, entity_data)` - Update existing entity
- `delete(entity_id)` - Delete entity
- `get_all(limit, offset)` - Get all entities with pagination

#### Advanced Query Methods
- `get_company_by_name(name)` - Company by name
- `get_company_by_code(code)` - Company by code
- `get_active_companies()` - Active companies only
- `search_companies(search_term)` - Search companies

#### Statistics and Analytics
- `get_company_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.company.repository import CompanyRepositoryRepository

# Initialize repository
company_repo = CompanyRepositoryRepository()

# Get entity by ID
entity = company_repo.get_by_id("entity-uuid")

# Get entities with filtering
filter_obj = FilterObj()
result = company_repo.get_paginated(filter_obj)

# Create new entity
new_entity = company_repo.create(entity_data)

# Update entity
company_repo.update("entity-uuid", update_data)

# Get statistics
stats = company_repo.get_company_statistics()
```


## API Endpoints

### Company Management
- `GET /companies` - List companies
- `GET /companies/{id}` - Get company details
- `POST /companies` - Create company
- `PUT /companies/{id}` - Update company
- `DELETE /companies/{id}` - Deactivate company
- `POST /companies/{id}/verify` - Verify company

### Company Settings
- `GET /companies/{id}/settings` - List company settings
- `GET /companies/{id}/settings/{key}` - Get setting value
- `PUT /companies/{id}/settings/{key}` - Update setting
- `POST /companies/{id}/settings/bulk` - Bulk update settings
- `GET /companies/{id}/settings/categories` - Get setting categories

### Company Users
- `GET /companies/{id}/users` - List company users
- `GET /companies/{id}/users/{user_id}` - Get user details
- `POST /companies/{id}/users` - Add user to company
- `PUT /companies/{id}/users/{user_id}` - Update user role
- `DELETE /companies/{id}/users/{user_id}` - Remove user from company

### Company Branding
- `GET /companies/{id}/branding` - Get company branding
- `PUT /companies/{id}/branding` - Update company branding
- `POST /companies/{id}/branding/logo` - Upload company logo
- `POST /companies/{id}/branding/banner` - Upload company banner
- `GET /companies/{id}/branding/theme` - Get theme settings

### Company Analytics
- `GET /companies/{id}/analytics` - Get company analytics
- `GET /companies/{id}/analytics/overview` - Get company overview
- `GET /companies/{id}/analytics/performance` - Get performance metrics
- `GET /companies/{id}/analytics/trends` - Get company trends
- `GET /companies/{id}/reports` - Generate company reports

### Company Compliance
- `GET /companies/{id}/compliance` - Get compliance status
- `POST /companies/{id}/compliance/verify` - Verify compliance
- `GET /companies/{id}/compliance/documents` - Get compliance documents
- `POST /companies/{id}/compliance/documents` - Upload compliance document

## Business Logic

### Company Creation
1. **Registration Validation**: Validate company registration data
2. **Business Verification**: Verify business registration and tax ID
3. **Domain Validation**: Validate company domain and email
4. **Settings Initialization**: Initialize default company settings
5. **User Assignment**: Assign company admin users
6. **Branding Setup**: Set up default company branding
7. **Compliance Check**: Check regulatory compliance requirements

### Company Settings Management
1. **Setting Validation**: Validate setting values and types
2. **Category Organization**: Organize settings by categories
3. **Access Control**: Control access to sensitive settings
4. **Change Tracking**: Track setting changes and history
5. **Validation Rules**: Apply validation rules to settings
6. **Default Values**: Manage default setting values

### Company User Management
1. **User Invitation**: Invite users to join company
2. **Role Assignment**: Assign appropriate roles and permissions
3. **Access Control**: Control user access to company resources
4. **Department Management**: Organize users by departments
5. **Activity Monitoring**: Monitor user activity and engagement
6. **User Onboarding**: Manage user onboarding process

### Company Branding
1. **Brand Asset Management**: Manage company brand assets
2. **Theme Customization**: Customize company themes and layouts
3. **Color Management**: Manage company color schemes
4. **Typography Settings**: Configure typography and fonts
5. **Custom Styling**: Apply custom CSS and JavaScript
6. **Brand Consistency**: Ensure brand consistency across platform

### Company Analytics
1. **Data Collection**: Collect company performance data
2. **Metric Calculation**: Calculate key performance metrics
3. **Trend Analysis**: Analyze trends and patterns
4. **Benchmarking**: Compare performance against industry standards
5. **Insight Generation**: Generate actionable insights
6. **Report Creation**: Create comprehensive reports

## Validation Schemas

### CompanyCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "legal_name": "string (required, max 255 chars)",
    "company_code": "string (required, max 50 chars, unique)",
    "business_type": "string (required, enum: corporation|llc|partnership|sole_proprietorship)",
    "industry": "string (required, max 100 chars)",
    "registration_number": "string (required, max 100 chars)",
    "tax_id": "string (required, max 100 chars)",
    "email": "string (required, valid email)",
    "phone": "string (required, valid phone number)",
    "website": "string (optional, valid URL)",
    "contact_person": "string (required, max 255 chars)",
    "headquarters_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "timezone": "string (required, valid timezone)",
    "currency": "string (required, valid currency code)",
    "language": "string (required, valid language code)"
}
```

### CompanyUpdateSchema
```python
{
    "name": "string (optional, max 255 chars)",
    "legal_name": "string (optional, max 255 chars)",
    "business_type": "string (optional, enum: corporation|llc|partnership|sole_proprietorship)",
    "industry": "string (optional, max 100 chars)",
    "email": "string (optional, valid email)",
    "phone": "string (optional, valid phone number)",
    "website": "string (optional, valid URL)",
    "contact_person": "string (optional, max 255 chars)",
    "headquarters_address": "object (optional)",
    "timezone": "string (optional, valid timezone)",
    "currency": "string (optional, valid currency code)",
    "language": "string (optional, valid language code)"
}
```

### CompanySettingsSchema
```python
{
    "company_id": "uuid (required)",
    "setting_key": "string (required, max 100 chars)",
    "setting_value": "string (required)",
    "setting_type": "string (required, enum: string|integer|boolean|json)",
    "category": "string (required, max 100 chars)",
    "subcategory": "string (optional, max 100 chars)",
    "is_public": "boolean (optional, default false)",
    "validation_rules": "object (optional)"
}
```

### CompanyBrandingSchema
```python
{
    "company_id": "uuid (required)",
    "logo_url": "string (optional, valid URL)",
    "favicon_url": "string (optional, valid URL)",
    "banner_url": "string (optional, valid URL)",
    "primary_color": "string (optional, hex color)",
    "secondary_color": "string (optional, hex color)",
    "accent_color": "string (optional, hex color)",
    "font_family": "string (optional, max 100 chars)",
    "font_size": "string (optional, max 20 chars)",
    "heading_font": "string (optional, max 100 chars)",
    "layout_style": "string (optional, enum: modern|classic|minimal)",
    "sidebar_style": "string (optional, enum: fixed|collapsible|overlay)",
    "theme_mode": "string (optional, enum: light|dark|auto)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When company not found
- **BusinessLogicException**: For business rule violations
- **ComplianceException**: For compliance-related errors
- **BrandingException**: For branding-related errors

## Dependencies

- **User Module**: For company user management
- **Address Module**: For address validation
- **Settings Module**: For company settings
- **Analytics Module**: For company analytics
- **File Storage**: For company assets
- **Notification Module**: For company notifications

## Usage Examples

### Creating a Company
```python
from app.company.service import CompanyService
from app.company.schemas import CompanyCreateSchema

service = CompanyService()
company_data = {
    "name": "3D Print Solutions LLC",
    "legal_name": "3D Print Solutions Limited Liability Company",
    "company_code": "3DPS001",
    "business_type": "llc",
    "industry": "3D Printing Services",
    "registration_number": "REG123456789",
    "tax_id": "TAX987654321",
    "email": "info@3dprintsolutions.com",
    "phone": "+96812345678",
    "website": "https://3dprintsolutions.com",
    "contact_person": "Ahmed Al-Rashid",
    "headquarters_address": {
        "street": "123 Business Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "timezone": "Asia/Muscat",
    "currency": "OMR",
    "language": "en"
}

company = service.create_company(company_data)
```

### Managing Company Settings
```python
# Update company setting
setting_data = {
    "company_id": "company-uuid",
    "setting_key": "max_file_upload_size",
    "setting_value": "10485760",
    "setting_type": "integer",
    "category": "file_upload",
    "subcategory": "limits",
    "is_public": False,
    "validation_rules": {"min": 1024, "max": 104857600}
}

service.update_company_setting(setting_data)

# Get company settings
settings = service.get_company_settings(company_id)

# Bulk update settings
bulk_settings = [
    {"key": "setting1", "value": "value1"},
    {"key": "setting2", "value": "value2"}
]
service.bulk_update_settings(company_id, bulk_settings)
```

### Company User Management
```python
# Add user to company
user_data = {
    "company_id": "company-uuid",
    "user_id": "user-uuid",
    "role": "manager",
    "permissions": ["user_management", "order_management"],
    "access_level": "full",
    "department": "Operations",
    "is_admin": False
}

company_user = service.add_user_to_company(user_data)

# Update user role
service.update_user_role(company_id, user_id, {
    "role": "admin",
    "permissions": ["full_access"],
    "is_admin": True
})

# Get company users
users = service.get_company_users(company_id)
```

### Company Branding
```python
# Update company branding
branding_data = {
    "company_id": "company-uuid",
    "logo_url": "https://storage.example.com/logos/company-logo.png",
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "accent_color": "#28a745",
    "font_family": "Inter",
    "layout_style": "modern",
    "sidebar_style": "collapsible",
    "theme_mode": "light"
}

service.update_company_branding(branding_data)

# Upload company logo
logo_url = service.upload_company_logo(company_id, logo_file)

# Get company branding
branding = service.get_company_branding(company_id)
```

### Company Analytics
```python
# Get company analytics
analytics = service.get_company_analytics(company_id, period="monthly")

# Get company overview
overview = service.get_company_overview(company_id)

# Get performance metrics
performance = service.get_performance_metrics(
    company_id, 
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Generate company report
report = service.generate_company_report(
    company_id,
    report_type="performance",
    period="monthly"
)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Cache company settings and branding
- **Asset Optimization**: Optimize company assets for web delivery
- **CDN Integration**: Use CDN for company assets
- **Background Processing**: Process analytics in background

## Security

- **Access Control**: Role-based permissions for company management
- **Data Validation**: Validate all company inputs
- **Audit Logging**: Log all company operations
- **Data Encryption**: Encrypt sensitive company data
- **Compliance**: Ensure regulatory compliance

## Integration Points

- **User Management**: Company user management
- **Settings Management**: Company configuration
- **Analytics Platform**: Company analytics and reporting
- **File Storage**: Company asset management
- **Notification Service**: Company notifications
- **Compliance Systems**: Regulatory compliance

## Future Enhancements

- **Multi-tenant Architecture**: Advanced multi-company support
- **White-label Solutions**: Customizable white-label platform
- **Advanced Analytics**: AI-powered company insights
- **Compliance Automation**: Automated compliance management
- **Brand Management**: Advanced brand asset management
- **API Management**: Company-specific API management
