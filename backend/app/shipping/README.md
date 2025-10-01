# Shipping Module

The Shipping module manages shipping operations, delivery tracking, and logistics in the 3D Store application, providing comprehensive shipping and delivery management capabilities.

## Overview

This module handles:
- Shipping method management
- Delivery tracking and status updates
- Shipping cost calculation
- Carrier integration and API management
- Delivery scheduling and optimization
- Shipping analytics and reporting
- International shipping support

## Module Structure

```
shipping/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### ShippingMethod
Shipping method configuration:
- **Basic Info**: `method_id`, `name`, `description`, `carrier`
- **Pricing**: `base_cost`, `cost_per_kg`, `cost_per_item`, `free_shipping_threshold`
- **Delivery**: `delivery_time_min`, `delivery_time_max`, `delivery_days`
- **Coverage**: `supported_countries`, `supported_regions`, `restrictions`
- **Status**: `is_active`, `is_express`, `is_international`
- **Metadata**: `created_at`, `updated_at`

### Shipment
Individual shipment tracking:
- **Shipment Info**: `shipment_id`, `order_id`, `tracking_number`, `carrier`
- **Shipping**: `shipping_method_id`, `shipping_cost`, `insurance_value`
- **Address**: `shipping_address`, `delivery_address`, `return_address`
- **Status**: `status`, `current_location`, `delivery_status`
- **Timestamps**: `shipped_at`, `delivered_at`, `created_at`
- **Metadata**: `weight`, `dimensions`, `special_instructions`

### DeliveryTracking
Delivery tracking and status updates:
- **Tracking Info**: `tracking_id`, `shipment_id`, `status`, `location`
- **Details**: `description`, `timestamp`, `carrier_status`
- **Location**: `city`, `state`, `country`, `postal_code`
- **Metadata**: `created_at`, `updated_at`

### ShippingZone
Shipping zone management:
- **Zone Info**: `zone_id`, `name`, `description`, `countries`
- **Pricing**: `base_cost`, `cost_per_kg`, `free_shipping_threshold`
- **Delivery**: `delivery_time_min`, `delivery_time_max`
- **Restrictions**: `weight_limit`, `dimension_limit`, `item_restrictions`
- **Status**: `is_active`, `priority`
- **Metadata**: `created_at`, `updated_at`

### ShippingRate
Dynamic shipping rate calculation:
- **Rate Info**: `rate_id`, `zone_id`, `weight_range`, `cost`
- **Conditions**: `min_weight`, `max_weight`, `min_value`, `max_value`
- **Pricing**: `base_rate`, `per_kg_rate`, `per_item_rate`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Shipping Methods
- `GET /shipping/methods` - List shipping methods
- `GET /shipping/methods/{id}` - Get shipping method details
- `POST /shipping/methods` - Create shipping method
- `PUT /shipping/methods/{id}` - Update shipping method
- `DELETE /shipping/methods/{id}` - Delete shipping method
- `GET /shipping/methods/available` - Get available methods for order

### Shipment Management
- `GET /shipping/shipments` - List shipments
- `GET /shipping/shipments/{id}` - Get shipment details
- `POST /shipping/shipments` - Create shipment
- `PUT /shipping/shipments/{id}` - Update shipment
- `POST /shipping/shipments/{id}/ship` - Mark as shipped
- `POST /shipping/shipments/{id}/deliver` - Mark as delivered

### Delivery Tracking
- `GET /shipping/shipments/{id}/tracking` - Get tracking info
- `POST /shipping/shipments/{id}/tracking` - Add tracking update
- `GET /shipping/tracking/{tracking_number}` - Track by number
- `POST /shipping/tracking/webhook` - Carrier webhook endpoint
- `GET /shipping/tracking/status` - Get tracking status

### Shipping Zones
- `GET /shipping/zones` - List shipping zones
- `GET /shipping/zones/{id}` - Get zone details
- `POST /shipping/zones` - Create shipping zone
- `PUT /shipping/zones/{id}` - Update shipping zone
- `DELETE /shipping/zones/{id}` - Delete shipping zone

### Shipping Rates
- `GET /shipping/rates` - List shipping rates
- `GET /shipping/rates/calculate` - Calculate shipping cost
- `POST /shipping/rates` - Create shipping rate
- `PUT /shipping/rates/{id}` - Update shipping rate
- `DELETE /shipping/rates/{id}` - Delete shipping rate

### Shipping Analytics
- `GET /shipping/analytics/overview` - Get shipping overview
- `GET /shipping/analytics/performance` - Get performance metrics
- `GET /shipping/analytics/costs` - Get shipping cost analysis
- `GET /shipping/analytics/delivery-times` - Get delivery time analysis
- `GET /shipping/reports` - Generate shipping reports

## Business Logic

### Shipping Cost Calculation
1. **Order Analysis**: Analyze order weight, dimensions, and value
2. **Zone Determination**: Determine shipping zone based on address
3. **Method Selection**: Select appropriate shipping methods
4. **Rate Calculation**: Calculate shipping rates based on rules
5. **Discount Application**: Apply shipping discounts and promotions
6. **Final Cost**: Calculate final shipping cost
7. **Validation**: Validate shipping cost and availability

### Shipment Creation
1. **Order Validation**: Validate order and shipping requirements
2. **Method Selection**: Select shipping method based on preferences
3. **Label Generation**: Generate shipping labels
4. **Tracking Setup**: Set up tracking with carrier
5. **Documentation**: Generate shipping documents
6. **Notification**: Notify customer of shipment
7. **Inventory Update**: Update inventory and order status

### Delivery Tracking
1. **Carrier Integration**: Integrate with carrier tracking APIs
2. **Status Updates**: Receive and process status updates
3. **Location Tracking**: Track package location
4. **Exception Handling**: Handle delivery exceptions
5. **Customer Notification**: Notify customer of updates
6. **Analytics**: Update delivery analytics

### Shipping Optimization
1. **Route Optimization**: Optimize delivery routes
2. **Carrier Selection**: Select best carrier for each shipment
3. **Cost Optimization**: Optimize shipping costs
4. **Delivery Time Optimization**: Optimize delivery times
5. **Capacity Planning**: Plan shipping capacity
6. **Performance Monitoring**: Monitor shipping performance

## Validation Schemas

### ShippingMethodCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "description": "string (required, max 1000 chars)",
    "carrier": "string (required, max 100 chars)",
    "base_cost": "decimal (required, min 0)",
    "cost_per_kg": "decimal (optional, min 0)",
    "cost_per_item": "decimal (optional, min 0)",
    "free_shipping_threshold": "decimal (optional, min 0)",
    "delivery_time_min": "integer (required, min 1)",
    "delivery_time_max": "integer (required, min 1)",
    "delivery_days": "array of strings (optional)",
    "supported_countries": "array of strings (required)",
    "supported_regions": "array of strings (optional)",
    "is_active": "boolean (optional, default true)",
    "is_express": "boolean (optional, default false)",
    "is_international": "boolean (optional, default false)"
}
```

### ShipmentCreateSchema
```python
{
    "order_id": "uuid (required)",
    "shipping_method_id": "uuid (required)",
    "shipping_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "delivery_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "weight": "decimal (required, min 0)",
    "dimensions": {
        "length": "decimal (required, min 0)",
        "width": "decimal (required, min 0)",
        "height": "decimal (required, min 0)"
    },
    "insurance_value": "decimal (optional, min 0)",
    "special_instructions": "string (optional, max 1000 chars)"
}
```

### ShippingZoneCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "description": "string (required, max 1000 chars)",
    "countries": "array of strings (required)",
    "base_cost": "decimal (required, min 0)",
    "cost_per_kg": "decimal (optional, min 0)",
    "free_shipping_threshold": "decimal (optional, min 0)",
    "delivery_time_min": "integer (required, min 1)",
    "delivery_time_max": "integer (required, min 1)",
    "weight_limit": "decimal (optional, min 0)",
    "dimension_limit": "object (optional)",
    "is_active": "boolean (optional, default true)",
    "priority": "integer (optional, default 0)"
}
```

### ShippingRateCalculateSchema
```python
{
    "origin_address": {
        "country": "string (required)",
        "postal_code": "string (required)"
    },
    "destination_address": {
        "country": "string (required)",
        "postal_code": "string (required)"
    },
    "weight": "decimal (required, min 0)",
    "dimensions": {
        "length": "decimal (required, min 0)",
        "width": "decimal (required, min 0)",
        "height": "decimal (required, min 0)"
    },
    "value": "decimal (optional, min 0)",
    "shipping_methods": "array of uuids (optional)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When shipment not found
- **BusinessLogicException**: For business rule violations
- **ShippingException**: For shipping-related errors
- **CarrierException**: For carrier API errors

## Dependencies

- **Order Module**: For order information and processing
- **Address Module**: For address validation and management
- **Payment Module**: For shipping cost processing
- **Notification Module**: For shipping notifications
- **Carrier APIs**: Integration with shipping carriers
- **Analytics Module**: For shipping analytics

## Usage Examples

### Creating Shipping Method
```python
from app.shipping.service import ShippingService
from app.shipping.schemas import ShippingMethodCreateSchema

service = ShippingService()
method_data = {
    "name": "Standard Shipping",
    "description": "Standard delivery within 3-5 business days",
    "carrier": "DHL",
    "base_cost": 5.00,
    "cost_per_kg": 2.50,
    "free_shipping_threshold": 50.00,
    "delivery_time_min": 3,
    "delivery_time_max": 5,
    "delivery_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "supported_countries": ["OM", "AE", "SA", "KW", "QA", "BH"],
    "is_active": True,
    "is_express": False,
    "is_international": True
}

shipping_method = service.create_shipping_method(method_data)
```

### Creating Shipment
```python
# Create shipment
shipment_data = {
    "order_id": "order-uuid",
    "shipping_method_id": "method-uuid",
    "shipping_address": {
        "street": "123 Business Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "OM"
    },
    "delivery_address": {
        "street": "456 Customer Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "54321",
        "country": "OM"
    },
    "weight": 0.5,
    "dimensions": {
        "length": 10.0,
        "width": 8.0,
        "height": 2.0
    },
    "insurance_value": 25.00,
    "special_instructions": "Handle with care"
}

shipment = service.create_shipment(shipment_data)
```

### Shipping Cost Calculation
```python
# Calculate shipping cost
cost_data = {
    "origin_address": {
        "country": "OM",
        "postal_code": "12345"
    },
    "destination_address": {
        "country": "AE",
        "postal_code": "54321"
    },
    "weight": 0.5,
    "dimensions": {
        "length": 10.0,
        "width": 8.0,
        "height": 2.0
    },
    "value": 25.00
}

shipping_costs = service.calculate_shipping_cost(cost_data)
```

### Delivery Tracking
```python
# Get tracking information
tracking_info = service.get_tracking_info(shipment_id)

# Add tracking update
tracking_update = {
    "shipment_id": "shipment-uuid",
    "status": "in_transit",
    "location": "Dubai Hub",
    "description": "Package is in transit to destination",
    "city": "Dubai",
    "state": "Dubai",
    "country": "AE",
    "postal_code": "54321"
}

service.add_tracking_update(tracking_update)

# Track by tracking number
tracking = service.track_by_number("DHL123456789")
```

### Shipping Analytics
```python
# Get shipping overview
overview = service.get_shipping_overview()

# Get performance metrics
performance = service.get_performance_metrics(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Get shipping cost analysis
cost_analysis = service.get_shipping_cost_analysis(period="monthly")

# Generate shipping report
report = service.generate_shipping_report(
    report_type="performance",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Performance Considerations

- **Carrier API Caching**: Cache carrier API responses
- **Rate Calculation Caching**: Cache shipping rate calculations
- **Database Indexing**: Optimized queries with proper indexes
- **Background Processing**: Process tracking updates in background
- **CDN Integration**: Cache shipping data for fast delivery

## Security

- **API Security**: Secure carrier API integration
- **Data Validation**: Validate all shipping inputs
- **Access Control**: Role-based permissions for shipping management
- **Audit Logging**: Log all shipping operations
- **Data Encryption**: Encrypt sensitive shipping data

## Integration Points

- **Carrier APIs**: DHL, FedEx, UPS, local carriers
- **Address Services**: Address validation and geocoding
- **Payment Systems**: Shipping cost processing
- **Notification Services**: Shipping status notifications
- **Analytics Platforms**: Shipping analytics and reporting
- **Inventory Systems**: Stock management integration

## Future Enhancements

- **AI-Powered Optimization**: Machine learning shipping optimization
- **Real-time Tracking**: Live package tracking
- **Predictive Analytics**: Delivery time prediction
- **Mobile Integration**: Mobile shipping management
- **IoT Integration**: Smart package tracking
- **Blockchain**: Secure shipping documentation
