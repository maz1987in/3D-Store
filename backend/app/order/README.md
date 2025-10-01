# Order Module

The Order module manages the complete order lifecycle in the 3D Store application, from order creation to fulfillment and delivery.

## Overview

This module handles:
- Order creation and management
- Print job scheduling and tracking
- Order status management
- Payment processing integration
- Shipping and delivery tracking
- Order history and analytics
- Customer communication

## Module Structure

```
order/
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

### Order
Main order entity with the following key attributes:
- **Basic Info**: `order_number`, `customer_id`, `status`, `total_amount`
- **Items**: `order_items` (relationship to OrderItem)
- **Shipping**: `shipping_address`, `delivery_method`, `tracking_number`
- **Payment**: `payment_status`, `payment_method`, `transaction_id`
- **Timestamps**: `created_at`, `updated_at`, `shipped_at`, `delivered_at`
- **Metadata**: `notes`, `special_instructions`, `priority`

### OrderItem
Individual items within an order:
- **Product Info**: `product_id`, `product_name`, `product_type`
- **Customization**: `custom_design`, `print_settings`, `material_choice`
- **Quantities**: `quantity`, `unit_price`, `total_price`
- **3D Printing**: `file_url`, `print_estimates`, `print_job_id`
- **Status**: `item_status`, `print_status`, `completion_percentage`

### PrintJob
3D printing job details:
- **Job Info**: `job_number`, `printer_id`, `estimated_duration`
- **File Details**: `model_file_url`, `gcode_file_url`, `file_size`
- **Settings**: `layer_height`, `infill_percentage`, `support_enabled`
- **Status**: `status`, `progress_percentage`, `started_at`, `completed_at`
- **Quality**: `quality_checks`, `defects`, `reprint_required`

### OrderStatus
Order status tracking:
- **Status Types**: `pending`, `confirmed`, `in_production`, `shipped`, `delivered`, `cancelled`
- **Timestamps**: `status_changed_at`, `changed_by`
- **Notes**: `status_notes`, `reason_for_change`
- **Notifications**: `customer_notified`, `notification_sent_at`

## Repository Layer

The `OrderRepository` class provides data access operations for the Order module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Order]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities (customer, supplier, items)
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(order_id)` - Get order by ID
- `create(order_data)` - Create new order
- `update(order_id, order_data)` - Update existing order
- `delete(order_id)` - Delete order
- `get_all(limit, offset)` - Get all orders with pagination

#### Advanced Query Methods
- `get_orders_with_supplier(filter_obj)` - Orders with supplier information
- `get_order_with_details(order_id)` - Order with all related details
- `get_orders_by_customer(customer_id)` - Orders for specific customer
- `get_orders_by_status(status)` - Orders by status
- `get_orders_by_type(order_type)` - Orders by type (print_service, ready_made, mixed)
- `get_orders_by_priority(priority)` - Orders by priority level
- `get_orders_by_payment_status(payment_status)` - Orders by payment status
- `get_orders_by_supplier(supplier_id)` - Orders for specific supplier
- `get_orders_by_date_range(start_date, end_date)` - Orders within date range
- `get_orders_by_total_range(min_total, max_total)` - Orders within total range
- `get_recent_orders(limit)` - Most recent orders
- `get_orders_requiring_attention()` - Orders needing attention (high priority, overdue)

#### Order Management
- `update_order_status(order_id, new_status)` - Update order status
- `get_order_statistics()` - Order statistics for dashboard

### Usage Example

```python
from app.order.repository import OrderRepository

# Initialize repository
order_repo = OrderRepository()

# Get orders with filtering and pagination
filter_obj = FilterObj()
result = order_repo.get_orders_with_supplier(filter_obj)

# Get orders by customer
customer_orders = order_repo.get_orders_by_customer("customer-uuid")

# Get orders requiring attention
urgent_orders = order_repo.get_orders_requiring_attention()

# Update order status
order_repo.update_order_status("order-uuid", OrderStatusEnum.IN_PROGRESS)

# Get order statistics
stats = order_repo.get_order_statistics()
```

## API Endpoints

### Order Management
- `GET /orders` - List orders with filtering and pagination
- `GET /orders/{id}` - Get order details
- `POST /orders` - Create new order
- `PUT /orders/{id}` - Update order
- `DELETE /orders/{id}` - Cancel order
- `GET /orders/{id}/status` - Get order status history

### Order Items
- `GET /orders/{id}/items` - Get order items
- `POST /orders/{id}/items` - Add item to order
- `PUT /orders/{id}/items/{item_id}` - Update order item
- `DELETE /orders/{id}/items/{item_id}` - Remove item from order

### Print Jobs
- `GET /orders/{id}/print-jobs` - Get print jobs for order
- `POST /orders/{id}/print-jobs` - Create print job
- `PUT /orders/{id}/print-jobs/{job_id}` - Update print job
- `GET /orders/{id}/print-jobs/{job_id}/status` - Get print job status

### Order Processing
- `POST /orders/{id}/confirm` - Confirm order
- `POST /orders/{id}/start-production` - Start production
- `POST /orders/{id}/ship` - Mark as shipped
- `POST /orders/{id}/deliver` - Mark as delivered
- `POST /orders/{id}/cancel` - Cancel order

## Business Logic

### Order Creation Workflow
1. **Cart Validation**: Validate cart items and availability
2. **Price Calculation**: Calculate total including taxes and shipping
3. **Inventory Check**: Verify stock availability for ready-made products
4. **Customer Validation**: Verify customer information and address
5. **Payment Processing**: Process payment through gateway
6. **Order Generation**: Create order with unique order number
7. **Confirmation**: Send confirmation email to customer

### Print Job Management
1. **Job Creation**: Create print job for custom 3D printing items
2. **Printer Assignment**: Assign to available printer
3. **File Processing**: Generate G-code from 3D model
4. **Quality Checks**: Validate print settings and material compatibility
5. **Scheduling**: Schedule print job based on printer availability
6. **Monitoring**: Track print progress and quality

### Order Status Management
1. **Status Transitions**: Enforce valid status transitions
2. **Notifications**: Send status updates to customers
3. **Logging**: Log all status changes with timestamps
4. **Escalation**: Handle stuck orders and exceptions
5. **Reporting**: Generate status reports and analytics

### Payment Integration
1. **Payment Processing**: Integrate with payment gateways (Thawani, OMPay)
2. **Refund Handling**: Process refunds for cancelled orders
3. **Payment Verification**: Verify payment status
4. **Fraud Detection**: Implement fraud prevention measures
5. **Receipt Generation**: Generate payment receipts

## Validation Schemas

### OrderCreateSchema
```python
{
    "customer_id": "uuid (required)",
    "items": [
        {
            "product_id": "uuid (required)",
            "quantity": "integer (required, min 1)",
            "custom_design": "string (optional)",
            "print_settings": "object (optional)",
            "material_choice": "uuid (optional)"
        }
    ],
    "shipping_address": {
        "street": "string (required)",
        "city": "string (required)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "payment_method": "string (required)",
    "special_instructions": "string (optional)"
}
```

### OrderUpdateSchema
```python
{
    "status": "string (optional)",
    "shipping_address": "object (optional)",
    "special_instructions": "string (optional)",
    "priority": "string (optional)"
}
```

### PrintJobEstimateSchema
```python
{
    "product_id": "uuid (required)",
    "material_id": "uuid (required)",
    "print_settings": {
        "layer_height": "float (required)",
        "infill_percentage": "integer (required)",
        "support_enabled": "boolean (required)"
    },
    "file_url": "string (required)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When order/print job not found
- **BusinessLogicException**: For business rule violations
- **PaymentException**: For payment processing errors
- **PrintJobException**: For 3D printing related errors

## Dependencies

- **Product Module**: For product information and pricing
- **User Module**: For customer information
- **Payment Module**: For payment processing
- **Inventory Module**: For stock management
- **Notification Module**: For customer communications
- **File Storage**: For 3D model files and G-code

## Usage Examples

### Creating an Order
```python
from app.order.service import OrderService
from app.order.schemas import OrderCreateSchema

service = OrderService()
order_data = {
    "customer_id": "customer-uuid",
    "items": [
        {
            "product_id": "product-uuid",
            "quantity": 2,
            "custom_design": "Custom text: 'Happy Birthday'",
            "print_settings": {
                "layer_height": 0.2,
                "infill_percentage": 20
            }
        }
    ],
    "shipping_address": {
        "street": "123 Main St",
        "city": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "payment_method": "thawani"
}

order = service.create_order(order_data)
```

### Managing Print Jobs
```python
# Create print job for order item
print_job = service.create_print_job(order_id, item_id, printer_id)

# Update print job status
service.update_print_job_status(job_id, "in_progress", progress=25)

# Complete print job
service.complete_print_job(job_id, quality_notes="Print completed successfully")
```

### Order Status Management
```python
# Update order status
service.update_order_status(order_id, "in_production")

# Get order status history
status_history = service.get_order_status_history(order_id)

# Send status notification
service.send_status_notification(order_id, "Your order is being printed")
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frequently accessed order data cached
- **Pagination**: Large order lists paginated
- **Background Processing**: Print job processing in background
- **Real-time Updates**: WebSocket for status updates

## Security

- **Input Validation**: All inputs validated using schemas
- **Access Control**: Customers can only access their own orders
- **Payment Security**: PCI DSS compliant payment processing
- **Data Encryption**: Sensitive data encrypted at rest
- **Audit Logging**: All order changes logged

## Integration Points

- **Payment Gateways**: Thawani, OMPay integration
- **Shipping Providers**: Integration with shipping APIs
- **Email Service**: Order notifications and updates
- **SMS Service**: Delivery notifications
- **WebSocket**: Real-time status updates
- **File Storage**: 3D model and G-code storage

## Monitoring and Analytics

- **Order Metrics**: Order volume, revenue, conversion rates
- **Print Job Analytics**: Success rates, failure analysis
- **Customer Insights**: Order patterns, preferences
- **Performance Monitoring**: Response times, error rates
- **Business Intelligence**: Revenue reports, trend analysis

## Future Enhancements

- **AI-Powered Scheduling**: Intelligent print job scheduling
- **Predictive Analytics**: Demand forecasting and capacity planning
- **Mobile App**: Native mobile application for order tracking
- **Blockchain**: Order authenticity and provenance tracking
- **IoT Integration**: Real-time printer monitoring and control
