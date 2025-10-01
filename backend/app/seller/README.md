# Seller Module

The Seller module manages seller accounts, commission tracking, and marketplace operations in the 3D Store application, enabling third-party sellers to offer their products and services.

## Overview

This module handles:
- Seller registration and onboarding
- Commission calculation and tracking
- Seller performance monitoring
- Payment processing for sellers
- Product listing management
- Seller analytics and reporting
- Dispute resolution and support

## Module Structure

```
seller/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── schemas.py          # Input validation schemas
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Seller
Main seller entity with the following key attributes:
- **Basic Info**: `seller_id`, `business_name`, `contact_person`, `email`, `phone`
- **Business Details**: `business_type`, `tax_id`, `registration_number`
- **Address**: `business_address`, `shipping_address`, `billing_address`
- **Status**: `status`, `verification_status`, `is_active`, `is_verified`
- **Commission**: `commission_rate`, `commission_type`, `minimum_payout`
- **Metadata**: `created_at`, `updated_at`, `last_activity`

### SellerCommission
Commission tracking and calculation:
- **Commission Info**: `seller_id`, `order_id`, `product_id`, `commission_amount`
- **Calculation**: `base_amount`, `commission_rate`, `commission_type`
- **Status**: `status`, `is_paid`, `payment_date`
- **Period**: `commission_period`, `month`, `year`
- **Metadata**: `created_at`, `updated_at`

### SellerPayment
Payment processing for sellers:
- **Payment Info**: `seller_id`, `amount`, `currency`, `payment_method`
- **Period**: `payment_period`, `start_date`, `end_date`
- **Status**: `status`, `processed_at`, `payment_reference`
- **Fees**: `platform_fee`, `processing_fee`, `net_amount`
- **Metadata**: `created_at`, `updated_at`, `processed_by`

### SellerProduct
Seller product listings:
- **Product Info**: `seller_id`, `product_id`, `listing_status`
- **Pricing**: `seller_price`, `commission_rate`, `profit_margin`
- **Inventory**: `stock_quantity`, `reserved_quantity`, `available_quantity`
- **Performance**: `views`, `sales`, `conversion_rate`
- **Metadata**: `created_at`, `updated_at`

### SellerDocument
Seller verification documents:
- **Document Info**: `seller_id`, `document_type`, `document_url`
- **Verification**: `is_verified`, `verified_by`, `verified_at`
- **Status**: `status`, `rejection_reason`, `expiry_date`
- **Metadata**: `created_at`, `updated_at`

### SellerPerformance
Seller performance metrics:
- **Performance Info**: `seller_id`, `period`, `total_sales`, `total_orders`
- **Metrics**: `conversion_rate`, `average_rating`, `response_time`
- **Ranking**: `performance_score`, `tier_level`, `badges`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Seller Management
- `GET /sellers` - List all sellers
- `GET /sellers/{id}` - Get seller details
- `POST /sellers` - Register new seller
- `PUT /sellers/{id}` - Update seller information
- `DELETE /sellers/{id}` - Deactivate seller account
- `POST /sellers/{id}/verify` - Verify seller account

### Seller Products
- `GET /sellers/{id}/products` - List seller products
- `POST /sellers/{id}/products` - Add product to seller
- `PUT /sellers/{id}/products/{product_id}` - Update seller product
- `DELETE /sellers/{id}/products/{product_id}` - Remove seller product
- `GET /sellers/{id}/products/performance` - Get product performance

### Commission Management
- `GET /sellers/{id}/commissions` - List seller commissions
- `GET /sellers/{id}/commissions/{id}` - Get commission details
- `POST /sellers/{id}/commissions/calculate` - Calculate commissions
- `GET /sellers/{id}/commissions/summary` - Get commission summary
- `GET /sellers/{id}/commissions/pending` - Get pending commissions

### Payment Processing
- `GET /sellers/{id}/payments` - List seller payments
- `GET /sellers/{id}/payments/{id}` - Get payment details
- `POST /sellers/{id}/payments` - Process seller payment
- `GET /sellers/{id}/payments/summary` - Get payment summary
- `POST /sellers/{id}/payments/request` - Request payment

### Performance Analytics
- `GET /sellers/{id}/performance` - Get seller performance
- `GET /sellers/{id}/analytics` - Get seller analytics
- `GET /sellers/{id}/reports` - Generate seller reports
- `GET /sellers/leaderboard` - Get seller leaderboard
- `GET /sellers/performance/trends` - Get performance trends

### Document Management
- `GET /sellers/{id}/documents` - List seller documents
- `POST /sellers/{id}/documents` - Upload document
- `GET /sellers/{id}/documents/{id}` - Get document
- `PUT /sellers/{id}/documents/{id}/verify` - Verify document
- `DELETE /sellers/{id}/documents/{id}` - Delete document

## Business Logic

### Seller Registration
1. **Account Creation**: Create seller account with basic information
2. **Document Upload**: Collect required verification documents
3. **Identity Verification**: Verify seller identity and business details
4. **Commission Setup**: Set up commission structure and rates
5. **Payment Setup**: Configure payment methods and preferences
6. **Onboarding**: Complete seller onboarding process

### Commission Calculation
1. **Order Processing**: Calculate commission on each order
2. **Rate Application**: Apply appropriate commission rate
3. **Fee Deduction**: Deduct platform and processing fees
4. **Accumulation**: Accumulate commissions over time periods
5. **Validation**: Validate commission calculations
6. **Recording**: Record commission transactions

### Payment Processing
1. **Payment Calculation**: Calculate total payment amount
2. **Fee Deduction**: Deduct applicable fees and taxes
3. **Payment Method**: Process payment through configured method
4. **Status Tracking**: Track payment status and processing
5. **Notification**: Notify seller of payment status
6. **Reconciliation**: Reconcile payments with commissions

### Performance Monitoring
1. **Metrics Collection**: Collect seller performance metrics
2. **Score Calculation**: Calculate performance scores
3. **Tier Management**: Manage seller tier levels
4. **Badge Assignment**: Assign performance badges
5. **Trend Analysis**: Analyze performance trends
6. **Reporting**: Generate performance reports

### Product Management
1. **Product Listing**: Allow sellers to list products
2. **Pricing Control**: Let sellers set their prices
3. **Inventory Management**: Track seller inventory
4. **Performance Tracking**: Monitor product performance
5. **Quality Control**: Ensure product quality standards
6. **Dispute Resolution**: Handle product-related disputes

## Validation Schemas

### SellerCreateSchema
```python
{
    "business_name": "string (required, max 255 chars)",
    "contact_person": "string (required, max 255 chars)",
    "email": "string (required, valid email)",
    "phone": "string (required, valid phone number)",
    "business_type": "string (required, enum: individual|company|partnership)",
    "tax_id": "string (optional, max 100 chars)",
    "registration_number": "string (optional, max 100 chars)",
    "business_address": {
        "street": "string (required)",
        "city": "string (required)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "shipping_address": {
        "street": "string (required)",
        "city": "string (required)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "commission_rate": "decimal (required, min 0, max 1)",
    "commission_type": "string (required, enum: percentage|fixed)",
    "minimum_payout": "decimal (required, min 0)"
}
```

### SellerUpdateSchema
```python
{
    "business_name": "string (optional, max 255 chars)",
    "contact_person": "string (optional, max 255 chars)",
    "phone": "string (optional, valid phone number)",
    "business_type": "string (optional, enum: individual|company|partnership)",
    "tax_id": "string (optional, max 100 chars)",
    "registration_number": "string (optional, max 100 chars)",
    "business_address": "object (optional)",
    "shipping_address": "object (optional)",
    "commission_rate": "decimal (optional, min 0, max 1)",
    "minimum_payout": "decimal (optional, min 0)"
}
```

### SellerCommissionSchema
```python
{
    "seller_id": "uuid (required)",
    "order_id": "uuid (required)",
    "product_id": "uuid (required)",
    "base_amount": "decimal (required, min 0)",
    "commission_rate": "decimal (required, min 0, max 1)",
    "commission_type": "string (required, enum: percentage|fixed)",
    "commission_amount": "decimal (required, min 0)",
    "commission_period": "string (required, enum: monthly|quarterly|yearly)",
    "month": "integer (required, 1-12)",
    "year": "integer (required, current year+)"
}
```

### SellerPaymentSchema
```python
{
    "seller_id": "uuid (required)",
    "amount": "decimal (required, min 0.01)",
    "currency": "string (required, enum: OMR|USD|EUR)",
    "payment_method": "string (required, max 100 chars)",
    "payment_period": "string (required, enum: monthly|quarterly|yearly)",
    "start_date": "date (required)",
    "end_date": "date (required)",
    "platform_fee": "decimal (optional, min 0)",
    "processing_fee": "decimal (optional, min 0)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When seller not found
- **BusinessLogicException**: For business rule violations
- **CommissionException**: For commission calculation errors
- **PaymentException**: For payment processing errors

## Dependencies

- **User Module**: For seller authentication and management
- **Product Module**: For product listing and management
- **Order Module**: For order processing and commission calculation
- **Payment Module**: For payment processing
- **Financial Module**: For financial transaction recording
- **Document Module**: For document management and verification

## Usage Examples

### Seller Registration
```python
from app.seller.service import SellerService
from app.seller.schemas import SellerCreateSchema

service = SellerService()
seller_data = {
    "business_name": "3D Print Solutions",
    "contact_person": "Ahmed Al-Rashid",
    "email": "ahmed@3dprintsolutions.com",
    "phone": "+96812345678",
    "business_type": "company",
    "tax_id": "TAX123456789",
    "registration_number": "REG987654321",
    "business_address": {
        "street": "123 Business Street",
        "city": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "shipping_address": {
        "street": "123 Business Street",
        "city": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "commission_rate": 0.15,
    "commission_type": "percentage",
    "minimum_payout": 100.00
}

seller = service.create_seller(seller_data)
```

### Commission Management
```python
# Calculate commission for order
commission_data = {
    "seller_id": "seller-uuid",
    "order_id": "order-uuid",
    "product_id": "product-uuid",
    "base_amount": 200.00,
    "commission_rate": 0.15,
    "commission_type": "percentage",
    "commission_period": "monthly",
    "month": 1,
    "year": 2024
}

commission = service.calculate_commission(commission_data)

# Get seller commission summary
summary = service.get_commission_summary(seller_id, "2024-01-01", "2024-01-31")
```

### Payment Processing
```python
# Process seller payment
payment_data = {
    "seller_id": "seller-uuid",
    "amount": 1500.00,
    "currency": "OMR",
    "payment_method": "bank_transfer",
    "payment_period": "monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "platform_fee": 50.00,
    "processing_fee": 15.00
}

payment = service.process_seller_payment(payment_data)

# Get payment summary
payment_summary = service.get_payment_summary(seller_id)
```

### Performance Analytics
```python
# Get seller performance
performance = service.get_seller_performance(seller_id, "2024-01-01", "2024-01-31")

# Get seller analytics
analytics = service.get_seller_analytics(seller_id, period="monthly")

# Generate seller report
report = service.generate_seller_report(seller_id, report_type="performance")
```

### Product Management
```python
# Add product to seller
seller_product = service.add_seller_product(seller_id, product_id, {
    "seller_price": 150.00,
    "commission_rate": 0.15,
    "stock_quantity": 100
})

# Update seller product
service.update_seller_product(seller_id, product_id, {
    "seller_price": 160.00,
    "stock_quantity": 90
})

# Get seller product performance
performance = service.get_seller_product_performance(seller_id, product_id)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frequently accessed seller data cached
- **Commission Calculation**: Efficient commission calculation algorithms
- **Payment Processing**: Batch payment processing for efficiency
- **Report Generation**: Pre-generated reports cached

## Security

- **Access Control**: Role-based permissions for seller management
- **Document Security**: Secure storage and access control for documents
- **Payment Security**: Secure payment processing and data encryption
- **Audit Logging**: All seller operations logged
- **Data Privacy**: Compliance with data protection regulations

## Integration Points

- **Payment Gateways**: Integration with payment processors
- **Document Management**: Document storage and verification services
- **Email Service**: Seller notifications and communications
- **Analytics Platforms**: Business intelligence integration
- **CRM Systems**: Customer relationship management integration

## Future Enhancements

- **AI-Powered Insights**: Machine learning seller analytics
- **Advanced Analytics**: Predictive seller performance analysis
- **Mobile App**: Mobile seller management application
- **Automated Payments**: Automated payment processing
- **Seller Tools**: Advanced seller management tools
- **Marketplace Features**: Enhanced marketplace functionality
