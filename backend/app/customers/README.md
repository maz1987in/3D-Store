# Customers Module

The Customers module manages customer accounts, profiles, and customer-specific functionality in the 3D Store application, providing comprehensive customer management capabilities.

## Overview

This module handles:
- Customer account management
- Customer profile and preferences
- Customer order history and tracking
- Customer communication and support
- Customer analytics and insights
- Customer loyalty and rewards
- Customer segmentation and targeting

## Module Structure

```
customers/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Customer
Main customer entity with the following key attributes:
- **Basic Info**: `customer_id`, `username`, `email`, `phone`, `first_name`, `last_name`
- **Profile**: `avatar_url`, `date_of_birth`, `gender`, `preferred_language`
- **Address**: `billing_address`, `shipping_address`, `addresses`
- **Preferences**: `preferences`, `notifications`, `privacy_settings`
- **Status**: `is_active`, `is_verified`, `verification_status`
- **Loyalty**: `loyalty_points`, `loyalty_tier`, `total_orders`
- **Metadata**: `created_at`, `updated_at`, `last_activity`

### CustomerAddress
Customer address management:
- **Address Info**: `customer_id`, `address_type`, `is_default`
- **Address Details**: `street`, `city`, `state`, `postal_code`, `country`
- **Contact**: `contact_name`, `contact_phone`, `delivery_instructions`
- **Validation**: `is_verified`, `verification_status`
- **Metadata**: `created_at`, `updated_at`

### CustomerPreference
Customer preferences and settings:
- **Preference Info**: `customer_id`, `preference_key`, `preference_value`
- **Category**: `category`, `subcategory`, `is_public`
- **Type**: `preference_type`, `validation_rules`
- **Metadata**: `created_at`, `updated_at`

### CustomerOrder
Customer order history:
- **Order Info**: `customer_id`, `order_id`, `order_number`, `order_date`
- **Order Details**: `total_amount`, `status`, `payment_status`
- **Items**: `item_count`, `product_categories`
- **Metadata**: `created_at`, `updated_at`

### CustomerLoyalty
Customer loyalty and rewards:
- **Loyalty Info**: `customer_id`, `loyalty_points`, `loyalty_tier`
- **Rewards**: `available_rewards`, `used_rewards`, `expired_rewards`
- **History**: `points_earned`, `points_redeemed`, `points_expired`
- **Status**: `is_active`, `tier_expires_at`
- **Metadata**: `created_at`, `updated_at`

### CustomerSegment
Customer segmentation:
- **Segment Info**: `segment_id`, `name`, `description`, `criteria`
- **Customers**: `customer_count`, `segment_rules`
- **Targeting**: `targeting_rules`, `campaign_rules`
- **Status**: `is_active`, `created_by`
- **Metadata**: `created_at`, `updated_at`



## Repository Layer

The `CustomersRepositoryRepository` class provides data access operations for the Customers module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Customers]` for common CRUD operations
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
- `get_customer_by_user_id(user_id)` - Customer by associated user
- `get_customer_by_email(email)` - Customer by email address
- `get_customer_by_mobile(mobile)` - Customer by mobile number
- `get_customer_by_code(customer_code)` - Customer by code
- `get_customers_by_type(customer_type)` - Customers by type
- `get_active_customers()` - Active customers only
- `get_verified_customers()` - Verified customers
- `get_customers_by_city(city)` - Customers by city
- `get_customers_by_country(country)` - Customers by country
- `get_business_customers()` - Business customers only
- `search_customers(search_term)` - Search customers
- `get_customers_by_registration_date(start_date, end_date)` - Customers by registration date
- `get_recent_customers(limit)` - Recent customers
- `verify_customer(customer_id)` - Verify customer account
- `update_customer_status(customer_id, status)` - Update customer status

#### Statistics and Analytics
- `get_customers_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.customers.repository import CustomersRepositoryRepository

# Initialize repository
customers_repo = CustomersRepositoryRepository()

# Get entity by ID
entity = customers_repo.get_by_id("entity-uuid")

# Get entities with filtering
filter_obj = FilterObj()
result = customers_repo.get_paginated(filter_obj)

# Create new entity
new_entity = customers_repo.create(entity_data)

# Update entity
customers_repo.update("entity-uuid", update_data)

# Get statistics
stats = customers_repo.get_customers_statistics()
```


## API Endpoints

### Customer Management
- `GET /customers` - List customers with filtering
- `GET /customers/{id}` - Get customer details
- `POST /customers` - Create customer account
- `PUT /customers/{id}` - Update customer profile
- `DELETE /customers/{id}` - Deactivate customer account
- `POST /customers/{id}/verify` - Verify customer account

### Customer Profile
- `GET /customers/{id}/profile` - Get customer profile
- `PUT /customers/{id}/profile` - Update customer profile
- `POST /customers/{id}/profile/avatar` - Upload customer avatar
- `GET /customers/{id}/preferences` - Get customer preferences
- `PUT /customers/{id}/preferences` - Update customer preferences

### Customer Addresses
- `GET /customers/{id}/addresses` - List customer addresses
- `GET /customers/{id}/addresses/{address_id}` - Get address details
- `POST /customers/{id}/addresses` - Add customer address
- `PUT /customers/{id}/addresses/{address_id}` - Update address
- `DELETE /customers/{id}/addresses/{address_id}` - Delete address
- `POST /customers/{id}/addresses/{address_id}/set-default` - Set default address

### Customer Orders
- `GET /customers/{id}/orders` - Get customer order history
- `GET /customers/{id}/orders/{order_id}` - Get order details
- `GET /customers/{id}/orders/summary` - Get order summary
- `GET /customers/{id}/orders/analytics` - Get order analytics

### Customer Loyalty
- `GET /customers/{id}/loyalty` - Get loyalty information
- `GET /customers/{id}/loyalty/points` - Get loyalty points
- `POST /customers/{id}/loyalty/redeem` - Redeem loyalty points
- `GET /customers/{id}/loyalty/rewards` - Get available rewards
- `GET /customers/{id}/loyalty/history` - Get loyalty history

### Customer Segmentation
- `GET /customers/segments` - List customer segments
- `GET /customers/segments/{id}` - Get segment details
- `POST /customers/segments` - Create customer segment
- `PUT /customers/segments/{id}` - Update segment
- `DELETE /customers/segments/{id}` - Delete segment
- `GET /customers/segments/{id}/customers` - Get segment customers

### Customer Analytics
- `GET /customers/analytics/overview` - Get customer overview
- `GET /customers/analytics/segments` - Get segment analytics
- `GET /customers/analytics/behavior` - Get behavior analytics
- `GET /customers/analytics/retention` - Get retention analytics
- `GET /customers/reports` - Generate customer reports

## Business Logic

### Customer Registration
1. **Account Creation**: Create customer account with basic information
2. **Email Verification**: Send verification email and verify account
3. **Profile Setup**: Set up customer profile and preferences
4. **Address Management**: Manage customer addresses
5. **Loyalty Setup**: Initialize customer loyalty program
6. **Welcome Communication**: Send welcome email and onboarding
7. **Preference Collection**: Collect customer preferences and interests

### Customer Profile Management
1. **Profile Updates**: Allow customers to update their profiles
2. **Avatar Management**: Handle customer avatar uploads
3. **Preference Management**: Manage customer preferences
4. **Privacy Settings**: Handle customer privacy preferences
5. **Notification Preferences**: Manage notification settings
6. **Account Security**: Handle account security settings

### Customer Segmentation
1. **Segmentation Rules**: Define customer segmentation rules
2. **Behavioral Analysis**: Analyze customer behavior patterns
3. **Demographic Segmentation**: Segment customers by demographics
4. **Purchase History**: Segment based on purchase history
5. **Engagement Level**: Segment based on engagement
6. **Loyalty Status**: Segment based on loyalty tier

### Customer Loyalty Management
1. **Points Earning**: Track and award loyalty points
2. **Tier Management**: Manage customer loyalty tiers
3. **Rewards System**: Manage rewards and redemptions
4. **Expiration Handling**: Handle point expiration
5. **Promotional Campaigns**: Run loyalty campaigns
6. **Analytics**: Track loyalty program performance

### Customer Analytics
1. **Behavior Tracking**: Track customer behavior and interactions
2. **Purchase Analysis**: Analyze customer purchase patterns
3. **Engagement Metrics**: Measure customer engagement
4. **Retention Analysis**: Analyze customer retention
5. **Lifetime Value**: Calculate customer lifetime value
6. **Predictive Analytics**: Predict customer behavior

## Validation Schemas

### CustomerCreateSchema
```python
{
    "username": "string (required, min 3, max 50, unique)",
    "email": "string (required, valid email, unique)",
    "password": "string (required, min 8, max 128)",
    "first_name": "string (required, max 100)",
    "last_name": "string (required, max 100)",
    "phone": "string (optional, valid phone number)",
    "date_of_birth": "date (optional)",
    "gender": "string (optional, enum: male|female|other)",
    "preferred_language": "string (optional, default: en)",
    "billing_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "shipping_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    }
}
```

### CustomerUpdateSchema
```python
{
    "first_name": "string (optional, max 100)",
    "last_name": "string (optional, max 100)",
    "phone": "string (optional, valid phone number)",
    "date_of_birth": "date (optional)",
    "gender": "string (optional, enum: male|female|other)",
    "preferred_language": "string (optional)",
    "avatar_url": "string (optional, valid URL)"
}
```

### CustomerAddressSchema
```python
{
    "address_type": "string (required, enum: billing|shipping|both)",
    "street": "string (required, max 255)",
    "city": "string (required, max 100)",
    "state": "string (optional, max 100)",
    "postal_code": "string (required, max 20)",
    "country": "string (required, max 100)",
    "contact_name": "string (optional, max 255)",
    "contact_phone": "string (optional, valid phone number)",
    "delivery_instructions": "string (optional, max 500)",
    "is_default": "boolean (optional, default false)"
}
```

### CustomerPreferenceSchema
```python
{
    "preference_key": "string (required, max 100)",
    "preference_value": "string (required)",
    "category": "string (required, max 100)",
    "subcategory": "string (optional, max 100)",
    "is_public": "boolean (optional, default false)",
    "preference_type": "string (required, enum: string|integer|boolean|json)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When customer not found
- **BusinessLogicException**: For business rule violations
- **LoyaltyException**: For loyalty-related errors
- **SegmentationException**: For segmentation errors

## Dependencies

- **User Module**: For user authentication and management
- **Order Module**: For order history and tracking
- **Address Module**: For address validation
- **Loyalty Module**: For loyalty program management
- **Analytics Module**: For customer analytics
- **Notification Module**: For customer communications

## Usage Examples

### Creating a Customer
```python
from app.customers.service import CustomerService
from app.customers.schemas import CustomerCreateSchema

service = CustomerService()
customer_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+96812345678",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "preferred_language": "en",
    "billing_address": {
        "street": "123 Main Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "shipping_address": {
        "street": "123 Main Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    }
}

customer = service.create_customer(customer_data)
```

### Managing Customer Profile
```python
# Update customer profile
profile_data = {
    "first_name": "John",
    "last_name": "Smith",
    "phone": "+96887654321",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "preferred_language": "ar"
}

service.update_customer_profile(customer_id, profile_data)

# Upload customer avatar
avatar_url = service.upload_customer_avatar(customer_id, avatar_file)

# Get customer preferences
preferences = service.get_customer_preferences(customer_id)

# Update customer preferences
service.update_customer_preferences(customer_id, {
    "newsletter": True,
    "sms_notifications": False,
    "email_notifications": True
})
```

### Managing Customer Addresses
```python
# Add customer address
address_data = {
    "address_type": "shipping",
    "street": "456 New Street",
    "city": "Muscat",
    "state": "Muscat",
    "postal_code": "54321",
    "country": "Oman",
    "contact_name": "John Smith",
    "contact_phone": "+96812345678",
    "delivery_instructions": "Leave at front door",
    "is_default": True
}

address = service.add_customer_address(customer_id, address_data)

# Update customer address
service.update_customer_address(customer_id, address_id, {
    "street": "789 Updated Street",
    "city": "Muscat"
})

# Set default address
service.set_default_address(customer_id, address_id)
```

### Customer Loyalty Management
```python
# Get customer loyalty information
loyalty = service.get_customer_loyalty(customer_id)

# Redeem loyalty points
redemption = service.redeem_loyalty_points(customer_id, {
    "points": 1000,
    "reward_type": "discount",
    "reward_value": 10.00
})

# Get available rewards
rewards = service.get_available_rewards(customer_id)

# Get loyalty history
history = service.get_loyalty_history(customer_id)
```

### Customer Segmentation
```python
# Create customer segment
segment_data = {
    "name": "High Value Customers",
    "description": "Customers with high purchase value",
    "criteria": {
        "min_total_orders": 5,
        "min_total_spent": 500.00,
        "loyalty_tier": "gold"
    },
    "targeting_rules": {
        "email_campaigns": True,
        "sms_campaigns": True,
        "personalized_offers": True
    }
}

segment = service.create_customer_segment(segment_data)

# Get segment customers
customers = service.get_segment_customers(segment_id)

# Update segment
service.update_customer_segment(segment_id, {
    "criteria": {
        "min_total_orders": 10,
        "min_total_spent": 1000.00
    }
})
```

### Customer Analytics
```python
# Get customer overview
overview = service.get_customer_overview()

# Get customer analytics
analytics = service.get_customer_analytics(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Get behavior analytics
behavior = service.get_behavior_analytics(customer_id)

# Get retention analytics
retention = service.get_retention_analytics(period="monthly")

# Generate customer report
report = service.generate_customer_report(
    report_type="segmentation",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Cache customer data and preferences
- **Segmentation Caching**: Cache customer segments
- **Analytics Processing**: Process analytics in background
- **CDN Integration**: Cache customer assets

## Security

- **Access Control**: Role-based permissions for customer management
- **Data Privacy**: Protect customer personal information
- **Audit Logging**: Log all customer operations
- **Data Encryption**: Encrypt sensitive customer data
- **GDPR Compliance**: Ensure data protection compliance

## Integration Points

- **User Management**: Customer authentication and authorization
- **Order Management**: Customer order history and tracking
- **Loyalty Programs**: Customer loyalty and rewards
- **Analytics Platforms**: Customer analytics and insights
- **Marketing Tools**: Customer segmentation and targeting
- **Communication Systems**: Customer notifications and support

## Future Enhancements

- **AI-Powered Insights**: Machine learning customer insights
- **Predictive Analytics**: Customer behavior prediction
- **Personalization Engine**: Advanced personalization
- **Social Integration**: Social media integration
- **Mobile App**: Mobile customer management
- **Voice Interface**: Voice-activated customer service
