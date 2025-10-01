# Invoices Module

The Invoices module manages invoice generation, billing, and financial documentation in the 3D Store application, providing comprehensive invoice management capabilities.

## Overview

This module handles:
- Invoice generation and management
- Billing and payment tracking
- Invoice templates and customization
- Tax calculation and compliance
- Invoice delivery and notifications
- Invoice analytics and reporting
- Multi-currency support

## Module Structure

```
invoices/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Invoice
Main invoice entity with the following key attributes:
- **Basic Info**: `invoice_id`, `invoice_number`, `order_id`, `customer_id`
- **Invoice Details**: `invoice_date`, `due_date`, `status`, `payment_terms`
- **Amounts**: `subtotal`, `tax_amount`, `discount_amount`, `total_amount`
- **Currency**: `currency_code`, `exchange_rate`, `local_amount`
- **Billing**: `billing_address`, `shipping_address`, `payment_method`
- **Status**: `is_paid`, `paid_at`, `payment_reference`
- **Metadata**: `created_at`, `updated_at`, `sent_at`

### InvoiceItem
Invoice line items and details:
- **Item Info**: `item_id`, `invoice_id`, `product_id`, `description`
- **Quantity**: `quantity`, `unit_price`, `total_price`
- **Tax**: `tax_rate`, `tax_amount`, `tax_type`
- **Discount**: `discount_rate`, `discount_amount`, `discount_type`
- **Metadata**: `created_at`, `updated_at`

### InvoiceTemplate
Invoice template management:
- **Template Info**: `template_id`, `name`, `description`, `template_type`
- **Content**: `header_content`, `footer_content`, `body_template`
- **Styling**: `css_styles`, `logo_url`, `color_scheme`
- **Settings**: `is_default`, `is_active`, `company_id`
- **Metadata**: `created_at`, `updated_at`

### InvoiceTax
Tax calculation and management:
- **Tax Info**: `tax_id`, `invoice_id`, `tax_type`, `tax_rate`
- **Amounts**: `taxable_amount`, `tax_amount`, `tax_description`
- **Compliance**: `tax_code`, `tax_authority`, `tax_period`
- **Metadata**: `created_at`, `updated_at`

### InvoicePayment
Invoice payment tracking:
- **Payment Info**: `payment_id`, `invoice_id`, `payment_method`, `amount`
- **Payment Details**: `payment_date`, `payment_reference`, `transaction_id`
- **Status**: `payment_status`, `is_verified`, `verified_at`
- **Metadata**: `created_at`, `updated_at`

### InvoiceDelivery
Invoice delivery and notifications:
- **Delivery Info**: `delivery_id`, `invoice_id`, `delivery_method`, `recipient`
- **Status**: `delivery_status`, `sent_at`, `delivered_at`, `opened_at`
- **Tracking**: `tracking_number`, `delivery_notes`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Invoice Management
- `GET /invoices` - List invoices with filtering
- `GET /invoices/{id}` - Get invoice details
- `POST /invoices` - Create invoice
- `PUT /invoices/{id}` - Update invoice
- `DELETE /invoices/{id}` - Delete invoice
- `POST /invoices/{id}/send` - Send invoice
- `POST /invoices/{id}/mark-paid` - Mark invoice as paid

### Invoice Items
- `GET /invoices/{id}/items` - List invoice items
- `GET /invoices/{id}/items/{item_id}` - Get item details
- `POST /invoices/{id}/items` - Add item to invoice
- `PUT /invoices/{id}/items/{item_id}` - Update item
- `DELETE /invoices/{id}/items/{item_id}` - Remove item

### Invoice Templates
- `GET /invoices/templates` - List invoice templates
- `GET /invoices/templates/{id}` - Get template details
- `POST /invoices/templates` - Create template
- `PUT /invoices/templates/{id}` - Update template
- `DELETE /invoices/templates/{id}` - Delete template
- `POST /invoices/templates/{id}/set-default` - Set as default template

### Invoice Payments
- `GET /invoices/{id}/payments` - List invoice payments
- `POST /invoices/{id}/payments` - Record payment
- `PUT /invoices/{id}/payments/{payment_id}` - Update payment
- `DELETE /invoices/{id}/payments/{payment_id}` - Delete payment
- `POST /invoices/{id}/payments/verify` - Verify payment

### Invoice Delivery
- `GET /invoices/{id}/delivery` - Get delivery status
- `POST /invoices/{id}/delivery` - Send invoice
- `PUT /invoices/{id}/delivery` - Update delivery method
- `GET /invoices/delivery/status` - Get delivery status

### Invoice Analytics
- `GET /invoices/analytics/overview` - Get invoice overview
- `GET /invoices/analytics/revenue` - Get revenue analytics
- `GET /invoices/analytics/aging` - Get aging analysis
- `GET /invoices/analytics/trends` - Get invoice trends
- `GET /invoices/reports` - Generate invoice reports

## Business Logic

### Invoice Generation
1. **Order Processing**: Process orders for invoice generation
2. **Template Selection**: Select appropriate invoice template
3. **Item Calculation**: Calculate invoice line items
4. **Tax Calculation**: Calculate applicable taxes
5. **Discount Application**: Apply discounts and promotions
6. **Total Calculation**: Calculate final invoice total
7. **Invoice Creation**: Create invoice with all details

### Invoice Management
1. **Status Tracking**: Track invoice status and lifecycle
2. **Payment Processing**: Process invoice payments
3. **Overdue Management**: Handle overdue invoices
4. **Refund Processing**: Process invoice refunds
5. **Credit Notes**: Generate credit notes
6. **Invoice Updates**: Update invoice details and items

### Tax Management
1. **Tax Calculation**: Calculate applicable taxes
2. **Tax Compliance**: Ensure tax compliance
3. **Tax Reporting**: Generate tax reports
4. **Multi-jurisdiction**: Handle multiple tax jurisdictions
5. **Tax Exemptions**: Handle tax exemptions
6. **Tax Auditing**: Support tax auditing

### Invoice Delivery
1. **Delivery Methods**: Support multiple delivery methods
2. **Email Delivery**: Send invoices via email
3. **PDF Generation**: Generate PDF invoices
4. **Delivery Tracking**: Track invoice delivery
5. **Notification System**: Notify customers of invoices
6. **Reminder System**: Send payment reminders

### Invoice Analytics
1. **Revenue Tracking**: Track invoice revenue
2. **Aging Analysis**: Analyze invoice aging
3. **Payment Trends**: Track payment trends
4. **Customer Analysis**: Analyze customer invoicing
5. **Performance Metrics**: Track invoice performance
6. **Reporting**: Generate comprehensive reports

## Validation Schemas

### InvoiceCreateSchema
```python
{
    "order_id": "uuid (required)",
    "customer_id": "uuid (required)",
    "invoice_date": "date (required)",
    "due_date": "date (required)",
    "payment_terms": "string (required, max 100 chars)",
    "currency_code": "string (required, valid currency code)",
    "exchange_rate": "decimal (optional, min 0)",
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
    },
    "payment_method": "string (optional, max 100 chars)",
    "notes": "string (optional, max 1000 chars)"
}
```

### InvoiceItemCreateSchema
```python
{
    "invoice_id": "uuid (required)",
    "product_id": "uuid (required)",
    "description": "string (required, max 500 chars)",
    "quantity": "decimal (required, min 0)",
    "unit_price": "decimal (required, min 0)",
    "tax_rate": "decimal (optional, min 0, max 100)",
    "tax_type": "string (optional, max 100 chars)",
    "discount_rate": "decimal (optional, min 0, max 100)",
    "discount_type": "string (optional, max 100 chars)"
}
```

### InvoiceTemplateCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "template_type": "string (required, enum: standard|proforma|credit_note)",
    "header_content": "string (optional, max 5000 chars)",
    "footer_content": "string (optional, max 5000 chars)",
    "body_template": "string (required, max 10000 chars)",
    "css_styles": "string (optional, max 10000 chars)",
    "logo_url": "string (optional, valid URL)",
    "color_scheme": "string (optional, max 100 chars)",
    "is_default": "boolean (optional, default false)",
    "is_active": "boolean (optional, default true)"
}
```

### InvoicePaymentCreateSchema
```python
{
    "invoice_id": "uuid (required)",
    "payment_method": "string (required, max 100 chars)",
    "amount": "decimal (required, min 0)",
    "payment_date": "datetime (required)",
    "payment_reference": "string (optional, max 255 chars)",
    "transaction_id": "string (optional, max 255 chars)",
    "payment_status": "string (required, enum: pending|completed|failed|refunded)",
    "notes": "string (optional, max 1000 chars)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When invoice not found
- **BusinessLogicException**: For business rule violations
- **PaymentException**: For payment-related errors
- **TaxException**: For tax calculation errors

## Dependencies

- **Order Module**: For order information
- **Customer Module**: For customer information
- **Product Module**: For product information
- **Financial Module**: For financial calculations
- **Tax Module**: For tax calculations
- **Notification Module**: For invoice notifications

## Usage Examples

### Creating an Invoice
```python
from app.invoices.service import InvoiceService
from app.invoices.schemas import InvoiceCreateSchema

service = InvoiceService()
invoice_data = {
    "order_id": "order-uuid",
    "customer_id": "customer-uuid",
    "invoice_date": "2024-01-15",
    "due_date": "2024-02-15",
    "payment_terms": "Net 30 days",
    "currency_code": "OMR",
    "exchange_rate": 1.0,
    "billing_address": {
        "street": "123 Customer Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "shipping_address": {
        "street": "123 Customer Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "payment_method": "Bank Transfer",
    "notes": "Thank you for your business!"
}

invoice = service.create_invoice(invoice_data)
```

### Managing Invoice Items
```python
# Add item to invoice
item_data = {
    "invoice_id": "invoice-uuid",
    "product_id": "product-uuid",
    "description": "Custom 3D Printed Phone Case",
    "quantity": 2.0,
    "unit_price": 25.00,
    "tax_rate": 5.0,
    "tax_type": "VAT",
    "discount_rate": 10.0,
    "discount_type": "Volume Discount"
}

item = service.add_invoice_item(item_data)

# Update invoice item
service.update_invoice_item(invoice_id, item_id, {
    "quantity": 3.0,
    "unit_price": 23.00
})

# Remove invoice item
service.remove_invoice_item(invoice_id, item_id)
```

### Managing Invoice Templates
```python
# Create invoice template
template_data = {
    "name": "Standard Invoice Template",
    "description": "Standard invoice template for 3D Store",
    "template_type": "standard",
    "header_content": "<h1>3D Store Invoice</h1>",
    "footer_content": "<p>Thank you for your business!</p>",
    "body_template": "Invoice body template with placeholders",
    "css_styles": "body { font-family: Arial; }",
    "logo_url": "https://example.com/logo.png",
    "color_scheme": "blue",
    "is_default": True,
    "is_active": True
}

template = service.create_invoice_template(template_data)

# Set as default template
service.set_default_template(template_id)

# Update template
service.update_invoice_template(template_id, {
    "name": "Updated Standard Template",
    "color_scheme": "green"
})
```

### Managing Invoice Payments
```python
# Record payment
payment_data = {
    "invoice_id": "invoice-uuid",
    "payment_method": "Bank Transfer",
    "amount": 50.00,
    "payment_date": "2024-01-20T10:30:00Z",
    "payment_reference": "TXN123456789",
    "transaction_id": "TXN123456789",
    "payment_status": "completed",
    "notes": "Payment received via bank transfer"
}

payment = service.record_payment(payment_data)

# Verify payment
service.verify_payment(payment_id)

# Get invoice payments
payments = service.get_invoice_payments(invoice_id)
```

### Invoice Delivery
```python
# Send invoice
delivery_data = {
    "invoice_id": "invoice-uuid",
    "delivery_method": "email",
    "recipient": "customer@example.com",
    "delivery_notes": "Invoice sent via email"
}

delivery = service.send_invoice(delivery_data)

# Get delivery status
status = service.get_delivery_status(invoice_id)

# Update delivery method
service.update_delivery_method(invoice_id, {
    "delivery_method": "postal",
    "tracking_number": "TRK123456789"
})
```

### Invoice Analytics
```python
# Get invoice overview
overview = service.get_invoice_overview()

# Get revenue analytics
revenue = service.get_revenue_analytics(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Get aging analysis
aging = service.get_aging_analysis()

# Get invoice trends
trends = service.get_invoice_trends(period="monthly")

# Generate invoice report
report = service.generate_invoice_report(
    report_type="revenue",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **PDF Generation**: Efficient PDF generation
- **Email Delivery**: Optimize email delivery
- **Caching**: Cache frequently accessed invoice data
- **Background Processing**: Process invoices in background

## Security

- **Access Control**: Role-based permissions for invoice management
- **Data Privacy**: Protect customer financial information
- **Audit Logging**: Log all invoice operations
- **Payment Security**: Secure payment processing
- **Document Security**: Secure invoice document storage

## Integration Points

- **Payment Gateways**: Payment processing integration
- **Email Services**: Invoice delivery via email
- **PDF Generation**: Invoice PDF generation
- **Tax Services**: Tax calculation and compliance
- **Accounting Systems**: Integration with accounting software
- **Notification Systems**: Invoice notifications and reminders

## Future Enhancements

- **AI-Powered Analytics**: Machine learning invoice insights
- **Automated Invoicing**: Automated invoice generation
- **Blockchain Integration**: Secure invoice verification
- **Mobile App**: Mobile invoice management
- **Advanced Reporting**: Advanced invoice reporting and analytics
- **Multi-language Support**: Multi-language invoice support
