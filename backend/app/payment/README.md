# Payment Module

The Payment module handles all payment processing, transaction management, and financial operations in the 3D Store application, supporting multiple payment gateways and methods.

## Overview

This module handles:
- Payment processing and gateway integration
- Transaction management and tracking
- Refund and chargeback handling
- Payment method management
- Financial reporting and analytics
- Fraud detection and prevention
- Compliance and security

## Module Structure

```
payment/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── schemas.py          # Input validation schemas
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Payment
Main payment entity with the following key attributes:
- **Basic Info**: `payment_id`, `order_id`, `amount`, `currency`, `status`
- **Payment Method**: `payment_method`, `gateway`, `gateway_transaction_id`
- **Customer**: `customer_id`, `billing_address`, `shipping_address`
- **Timestamps**: `created_at`, `processed_at`, `completed_at`, `failed_at`
- **Metadata**: `gateway_response`, `failure_reason`, `retry_count`
- **Security**: `fraud_score`, `risk_level`, `verification_status`

### PaymentMethod
Customer payment methods:
- **Method Info**: `customer_id`, `method_type`, `gateway`, `is_default`
- **Card Details**: `card_last_four`, `card_brand`, `expiry_month`, `expiry_year`
- **Bank Details**: `account_last_four`, `bank_name`, `routing_number`
- **Digital Wallet**: `wallet_type`, `wallet_id`, `wallet_email`
- **Security**: `token`, `is_verified`, `verification_date`
- **Metadata**: `created_at`, `updated_at`, `last_used`

### Transaction
Individual transaction records:
- **Transaction Info**: `transaction_id`, `payment_id`, `type`, `amount`
- **Gateway Details**: `gateway_transaction_id`, `gateway_response`
- **Status**: `status`, `gateway_status`, `processing_status`
- **Fees**: `gateway_fee`, `processing_fee`, `net_amount`
- **Timestamps**: `created_at`, `processed_at`, `settled_at`
- **Metadata**: `reference_id`, `description`, `notes`

### Refund
Refund processing and tracking:
- **Refund Info**: `refund_id`, `payment_id`, `amount`, `reason`
- **Status**: `status`, `gateway_refund_id`, `gateway_response`
- **Approval**: `approved_by`, `approved_at`, `rejection_reason`
- **Processing**: `processed_at`, `settled_at`, `failure_reason`
- **Metadata**: `created_at`, `updated_at`, `notes`

### PaymentGateway
Payment gateway configuration:
- **Gateway Info**: `name`, `type`, `is_active`, `is_test_mode`
- **Configuration**: `api_key`, `secret_key`, `webhook_secret`
- **Endpoints**: `api_url`, `webhook_url`, `redirect_url`
- **Settings**: `supported_currencies`, `supported_methods`, `fees`
- **Metadata**: `created_at`, `updated_at`, `last_sync`

## API Endpoints

### Payment Processing
- `POST /payments/process` - Process payment
- `GET /payments/{id}` - Get payment details
- `POST /payments/{id}/capture` - Capture authorized payment
- `POST /payments/{id}/void` - Void payment
- `POST /payments/{id}/refund` - Process refund
- `GET /payments/{id}/status` - Get payment status

### Payment Methods
- `GET /payments/methods` - List customer payment methods
- `POST /payments/methods` - Add payment method
- `PUT /payments/methods/{id}` - Update payment method
- `DELETE /payments/methods/{id}` - Remove payment method
- `POST /payments/methods/{id}/verify` - Verify payment method

### Transactions
- `GET /payments/transactions` - List transactions
- `GET /payments/transactions/{id}` - Get transaction details
- `POST /payments/transactions/{id}/retry` - Retry failed transaction
- `GET /payments/transactions/search` - Search transactions

### Refunds
- `GET /payments/refunds` - List refunds
- `GET /payments/refunds/{id}` - Get refund details
- `POST /payments/refunds/{id}/approve` - Approve refund
- `POST /payments/refunds/{id}/reject` - Reject refund

### Payment Gateways
- `GET /payments/gateways` - List available gateways
- `GET /payments/gateways/{id}` - Get gateway details
- `POST /payments/gateways/{id}/test` - Test gateway connection
- `PUT /payments/gateways/{id}/config` - Update gateway configuration

### Webhooks
- `POST /payments/webhooks/{gateway}` - Gateway webhook endpoint
- `GET /payments/webhooks/{gateway}/events` - List webhook events
- `POST /payments/webhooks/{gateway}/retry` - Retry webhook processing

## Business Logic

### Payment Processing Flow
1. **Payment Initiation**: Validate payment request and customer
2. **Gateway Selection**: Choose appropriate payment gateway
3. **Fraud Check**: Run fraud detection and risk assessment
4. **Payment Processing**: Send payment to gateway
5. **Response Handling**: Process gateway response
6. **Transaction Recording**: Record transaction details
7. **Status Updates**: Update order and customer status
8. **Notifications**: Send payment confirmation

### Payment Method Management
1. **Method Addition**: Securely store payment method tokens
2. **Verification**: Verify payment method with gateway
3. **Default Selection**: Manage default payment method
4. **Security**: Encrypt sensitive payment data
5. **Expiry Management**: Handle expired payment methods
6. **Customer Control**: Allow customers to manage methods

### Refund Processing
1. **Refund Request**: Validate refund eligibility
2. **Approval Workflow**: Route for approval if required
3. **Gateway Processing**: Process refund through gateway
4. **Status Tracking**: Track refund status and settlement
5. **Customer Notification**: Notify customer of refund status
6. **Inventory Update**: Restore inventory if applicable

### Fraud Detection
1. **Risk Scoring**: Calculate fraud risk score
2. **Pattern Analysis**: Detect suspicious payment patterns
3. **Velocity Checks**: Monitor payment frequency and amounts
4. **Device Fingerprinting**: Track device and location data
5. **Manual Review**: Flag high-risk transactions for review
6. **Blocking**: Block suspicious payment methods

## Validation Schemas

### PaymentProcessSchema
```python
{
    "order_id": "uuid (required)",
    "amount": "decimal (required, min 0.01)",
    "currency": "string (required, enum: OMR|USD|EUR)",
    "payment_method": "string (required, enum: card|bank|wallet|cash)",
    "gateway": "string (required, enum: thawani|ompay|stripe)",
    "customer_id": "uuid (required)",
    "billing_address": {
        "street": "string (required)",
        "city": "string (required)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "return_url": "string (optional, valid URL)",
    "webhook_url": "string (optional, valid URL)"
}
```

### PaymentMethodCreateSchema
```python
{
    "customer_id": "uuid (required)",
    "method_type": "string (required, enum: card|bank|wallet)",
    "gateway": "string (required, enum: thawani|ompay|stripe)",
    "card_details": {
        "number": "string (required, valid card number)",
        "expiry_month": "integer (required, 1-12)",
        "expiry_year": "integer (required, current year+)",
        "cvv": "string (required, 3-4 digits)",
        "holder_name": "string (required, max 100 chars)"
    },
    "billing_address": {
        "street": "string (required)",
        "city": "string (required)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "is_default": "boolean (optional, default false)"
}
```

### RefundCreateSchema
```python
{
    "payment_id": "uuid (required)",
    "amount": "decimal (required, min 0.01)",
    "reason": "string (required, max 500 chars)",
    "refund_type": "string (required, enum: full|partial)",
    "notes": "string (optional, max 1000 chars)"
}
```

### TransactionSearchSchema
```python
{
    "customer_id": "uuid (optional)",
    "order_id": "uuid (optional)",
    "status": "string (optional, enum: pending|completed|failed|refunded)",
    "gateway": "string (optional, enum: thawani|ompay|stripe)",
    "date_from": "date (optional)",
    "date_to": "date (optional)",
    "amount_min": "decimal (optional, min 0)",
    "amount_max": "decimal (optional, min 0)",
    "page": "integer (optional, default 1)",
    "per_page": "integer (optional, default 20)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **PaymentException**: For payment processing errors
- **GatewayException**: For gateway communication errors
- **FraudException**: For fraud detection alerts
- **RefundException**: For refund processing errors

## Dependencies

- **Order Module**: For order information and processing
- **User Module**: For customer information
- **Notification Module**: For payment notifications
- **Audit Module**: For transaction logging
- **Security Module**: For fraud detection
- **External APIs**: Payment gateway integrations

## Usage Examples

### Processing Payment
```python
from app.payment.service import PaymentService
from app.payment.schemas import PaymentProcessSchema

service = PaymentService()
payment_data = {
    "order_id": "order-uuid",
    "amount": 99.99,
    "currency": "OMR",
    "payment_method": "card",
    "gateway": "thawani",
    "customer_id": "customer-uuid",
    "billing_address": {
        "street": "123 Main St",
        "city": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    }
}

payment = service.process_payment(payment_data)
```

### Managing Payment Methods
```python
# Add payment method
method_data = {
    "customer_id": "customer-uuid",
    "method_type": "card",
    "gateway": "thawani",
    "card_details": {
        "number": "4111111111111111",
        "expiry_month": 12,
        "expiry_year": 2025,
        "cvv": "123",
        "holder_name": "John Doe"
    },
    "billing_address": billing_address,
    "is_default": True
}

payment_method = service.add_payment_method(method_data)

# List customer payment methods
methods = service.get_customer_payment_methods(customer_id)
```

### Processing Refunds
```python
# Create refund
refund_data = {
    "payment_id": "payment-uuid",
    "amount": 50.00,
    "reason": "Customer requested refund",
    "refund_type": "partial"
}

refund = service.create_refund(refund_data)

# Approve refund
service.approve_refund(refund_id, approver_id)

# Process refund
service.process_refund(refund_id)
```

### Transaction Management
```python
# Search transactions
search_params = {
    "customer_id": "customer-uuid",
    "status": "completed",
    "date_from": "2024-01-01",
    "date_to": "2024-01-31"
}

transactions = service.search_transactions(search_params)

# Get transaction details
transaction = service.get_transaction(transaction_id)

# Retry failed transaction
service.retry_transaction(transaction_id)
```

## Security Features

### Data Protection
- **PCI DSS Compliance**: Secure handling of card data
- **Tokenization**: Sensitive data replaced with tokens
- **Encryption**: Data encrypted at rest and in transit
- **Access Control**: Role-based access to payment data
- **Audit Logging**: Comprehensive transaction logging

### Fraud Prevention
- **Risk Scoring**: Machine learning-based risk assessment
- **Velocity Checks**: Monitor payment frequency and amounts
- **Device Fingerprinting**: Track device and location data
- **3D Secure**: Additional authentication for card payments
- **Manual Review**: Human review of high-risk transactions

### Compliance
- **PCI DSS**: Payment card industry data security standards
- **GDPR**: General data protection regulation compliance
- **PCI PA-DSS**: Payment application data security standards
- **SOX**: Sarbanes-Oxley compliance for financial reporting
- **Local Regulations**: Compliance with local financial laws

## Performance Considerations

- **Gateway Optimization**: Efficient gateway communication
- **Caching**: Cache frequently accessed payment data
- **Async Processing**: Background processing for non-critical operations
- **Rate Limiting**: Protect against API abuse
- **Connection Pooling**: Efficient database connections

## Integration Points

- **Thawani**: Omani payment gateway integration
- **OMPay**: Local payment processor integration
- **Stripe**: International payment processing
- **Bank APIs**: Direct bank integration
- **Webhook Handlers**: Real-time payment notifications
- **Accounting Systems**: Financial data synchronization

## Future Enhancements

- **Cryptocurrency**: Support for digital currencies
- **Buy Now Pay Later**: Installment payment options
- **Mobile Payments**: Apple Pay, Google Pay integration
- **AI Fraud Detection**: Advanced machine learning models
- **Real-time Analytics**: Live payment monitoring dashboard
- **Multi-currency**: Support for multiple currencies
