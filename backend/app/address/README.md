# Address Module

The Address module manages customer addresses, shipping locations, and address validation in the 3D Store application, providing comprehensive address management capabilities.

## Overview

This module handles:
- Customer address management
- Shipping address validation
- Address geocoding and mapping
- Delivery area verification
- Address standardization
- Multiple address types (billing, shipping, business)
- Address history and preferences

## Module Structure

```
address/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── schemas.py          # Input validation schemas
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Address
Main address entity with the following key attributes:
- **Basic Info**: `address_id`, `customer_id`, `address_type`, `is_default`
- **Address Details**: `street`, `city`, `state`, `postal_code`, `country`
- **Geographic**: `latitude`, `longitude`, `timezone`, `delivery_zone`
- **Contact**: `contact_name`, `contact_phone`, `contact_email`
- **Validation**: `is_verified`, `verification_status`, `verification_date`
- **Metadata**: `created_at`, `updated_at`, `is_active`

### AddressType
Address type classification:
- **Type Info**: `type_name`, `description`, `is_required`
- **Validation**: `validation_rules`, `required_fields`
- **Display**: `display_name`, `icon`, `sort_order`
- **Metadata**: `created_at`, `updated_at`

### DeliveryZone
Delivery area management:
- **Zone Info**: `zone_id`, `zone_name`, `city`, `country`
- **Coverage**: `coverage_area` (GeoJSON), `service_radius`
- **Delivery**: `delivery_available`, `delivery_time`, `delivery_cost`
- **Restrictions**: `minimum_order`, `maximum_distance`, `restricted_items`
- **Metadata**: `created_at`, `updated_at`

### AddressValidation
Address validation records:
- **Validation Info**: `address_id`, `validation_service`, `validation_result`
- **Details**: `is_valid`, `confidence_score`, `suggestions`
- **Corrections**: `corrected_address`, `correction_notes`
- **Timestamps**: `validated_at`, `created_at`

### AddressHistory
Address change tracking:
- **History Info**: `address_id`, `old_address`, `new_address`
- **Change Details**: `change_type`, `change_reason`, `changed_by`
- **Timestamps**: `changed_at`, `created_at`

## API Endpoints

### Address Management
- `GET /addresses` - List customer addresses
- `GET /addresses/{id}` - Get address details
- `POST /addresses` - Create new address
- `PUT /addresses/{id}` - Update address
- `DELETE /addresses/{id}` - Delete address
- `POST /addresses/{id}/set-default` - Set as default address

### Address Types
- `GET /addresses/types` - List address types
- `GET /addresses/types/{id}` - Get address type details
- `POST /addresses/types` - Create address type
- `PUT /addresses/types/{id}` - Update address type
- `DELETE /addresses/types/{id}` - Delete address type

### Address Validation
- `POST /addresses/validate` - Validate address
- `GET /addresses/{id}/validation` - Get validation status
- `POST /addresses/{id}/verify` - Verify address
- `GET /addresses/validation/suggestions` - Get address suggestions

### Delivery Zones
- `GET /addresses/delivery-zones` - List delivery zones
- `GET /addresses/delivery-zones/{id}` - Get delivery zone details
- `POST /addresses/delivery-zones` - Create delivery zone
- `PUT /addresses/delivery-zones/{id}` - Update delivery zone
- `DELETE /addresses/delivery-zones/{id}` - Delete delivery zone
- `POST /addresses/delivery-zones/check` - Check delivery availability

### Address History
- `GET /addresses/{id}/history` - Get address history
- `GET /addresses/history` - Get all address changes
- `POST /addresses/{id}/restore` - Restore previous address

### Geocoding
- `POST /addresses/geocode` - Geocode address
- `POST /addresses/reverse-geocode` - Reverse geocode coordinates
- `GET /addresses/nearby` - Find nearby addresses

## Business Logic

### Address Creation
1. **Data Validation**: Validate address data and required fields
2. **Format Standardization**: Standardize address format
3. **Geocoding**: Convert address to coordinates
4. **Delivery Zone Check**: Verify delivery availability
5. **Validation Service**: Validate address with external service
6. **Default Setting**: Set as default if specified

### Address Validation
1. **External Service**: Use third-party validation service
2. **Format Check**: Validate address format and completeness
3. **Geocoding Verification**: Verify coordinates accuracy
4. **Delivery Verification**: Check delivery availability
5. **Suggestion Generation**: Provide address suggestions
6. **Confidence Scoring**: Calculate validation confidence

### Delivery Zone Management
1. **Zone Definition**: Define delivery coverage areas
2. **Service Availability**: Check delivery service availability
3. **Cost Calculation**: Calculate delivery costs
4. **Time Estimation**: Estimate delivery times
5. **Restriction Checking**: Check delivery restrictions
6. **Coverage Optimization**: Optimize delivery coverage

### Address Standardization
1. **Format Standardization**: Standardize address format
2. **Abbreviation Handling**: Handle common abbreviations
3. **Case Normalization**: Normalize case and formatting
4. **Field Mapping**: Map fields to standard format
5. **Validation Rules**: Apply validation rules
6. **Error Correction**: Suggest corrections for errors

### Geocoding Services
1. **Forward Geocoding**: Convert address to coordinates
2. **Reverse Geocoding**: Convert coordinates to address
3. **Batch Processing**: Process multiple addresses
4. **Caching**: Cache geocoding results
5. **Fallback Services**: Use multiple geocoding services
6. **Accuracy Validation**: Validate geocoding accuracy

## Validation Schemas

### AddressCreateSchema
```python
{
    "customer_id": "uuid (required)",
    "address_type": "string (required, enum: billing|shipping|business|home)",
    "street": "string (required, max 255 chars)",
    "city": "string (required, max 100 chars)",
    "state": "string (optional, max 100 chars)",
    "postal_code": "string (required, max 20 chars)",
    "country": "string (required, max 100 chars)",
    "contact_name": "string (optional, max 255 chars)",
    "contact_phone": "string (optional, valid phone number)",
    "contact_email": "string (optional, valid email)",
    "is_default": "boolean (optional, default false)",
    "delivery_instructions": "string (optional, max 500 chars)"
}
```

### AddressUpdateSchema
```python
{
    "street": "string (optional, max 255 chars)",
    "city": "string (optional, max 100 chars)",
    "state": "string (optional, max 100 chars)",
    "postal_code": "string (optional, max 20 chars)",
    "country": "string (optional, max 100 chars)",
    "contact_name": "string (optional, max 255 chars)",
    "contact_phone": "string (optional, valid phone number)",
    "contact_email": "string (optional, valid email)",
    "is_default": "boolean (optional)",
    "delivery_instructions": "string (optional, max 500 chars)"
}
```

### AddressValidationSchema
```python
{
    "address": {
        "street": "string (required, max 255 chars)",
        "city": "string (required, max 100 chars)",
        "state": "string (optional, max 100 chars)",
        "postal_code": "string (required, max 20 chars)",
        "country": "string (required, max 100 chars)"
    },
    "validation_service": "string (optional, enum: google|here|mapbox)",
    "include_suggestions": "boolean (optional, default true)"
}
```

### DeliveryZoneCreateSchema
```python
{
    "zone_name": "string (required, max 255 chars)",
    "city": "string (required, max 100 chars)",
    "country": "string (required, max 100 chars)",
    "coverage_area": "object (required, GeoJSON format)",
    "service_radius": "float (required, min 0)",
    "delivery_available": "boolean (required)",
    "delivery_time": "string (optional, max 100 chars)",
    "delivery_cost": "decimal (optional, min 0)",
    "minimum_order": "decimal (optional, min 0)",
    "maximum_distance": "float (optional, min 0)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When address not found
- **BusinessLogicException**: For business rule violations
- **GeocodingException**: For geocoding service errors
- **DeliveryException**: For delivery zone errors

## Dependencies

- **User Module**: For customer information
- **Order Module**: For shipping address usage
- **Geocoding Service**: For address geocoding
- **Validation Service**: For address validation
- **Mapping Service**: For delivery zone management
- **Notification Module**: For address change notifications

## Usage Examples

### Creating an Address
```python
from app.address.service import AddressService
from app.address.schemas import AddressCreateSchema

service = AddressService()
address_data = {
    "customer_id": "customer-uuid",
    "address_type": "shipping",
    "street": "123 Main Street",
    "city": "Muscat",
    "state": "Muscat",
    "postal_code": "12345",
    "country": "Oman",
    "contact_name": "Ahmed Al-Rashid",
    "contact_phone": "+96812345678",
    "contact_email": "ahmed@example.com",
    "is_default": True,
    "delivery_instructions": "Leave at front door"
}

address = service.create_address(address_data)
```

### Address Validation
```python
# Validate address
validation_data = {
    "address": {
        "street": "123 Main Street",
        "city": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "validation_service": "google",
    "include_suggestions": True
}

validation_result = service.validate_address(validation_data)

# Verify address
service.verify_address(address_id)
```

### Delivery Zone Management
```python
# Check delivery availability
delivery_check = service.check_delivery_availability(
    latitude=23.6141,
    longitude=58.5922,
    city="Muscat"
)

# Create delivery zone
zone_data = {
    "zone_name": "Muscat Central",
    "city": "Muscat",
    "country": "Oman",
    "coverage_area": {
        "type": "Polygon",
        "coordinates": [[[58.5, 23.6], [58.7, 23.6], [58.7, 23.8], [58.5, 23.8], [58.5, 23.6]]]
    },
    "service_radius": 10.0,
    "delivery_available": True,
    "delivery_time": "1-2 business days",
    "delivery_cost": 5.00,
    "minimum_order": 50.00
}

zone = service.create_delivery_zone(zone_data)
```

### Geocoding Services
```python
# Geocode address
coordinates = service.geocode_address("123 Main Street, Muscat, Oman")

# Reverse geocode coordinates
address = service.reverse_geocode(23.6141, 58.5922)

# Find nearby addresses
nearby = service.find_nearby_addresses(
    latitude=23.6141,
    longitude=58.5922,
    radius=5.0
)
```

### Address Management
```python
# Get customer addresses
addresses = service.get_customer_addresses(customer_id)

# Set default address
service.set_default_address(customer_id, address_id)

# Get address history
history = service.get_address_history(address_id)

# Restore previous address
service.restore_address(address_id, history_id)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Geocoding Caching**: Cache geocoding results
- **Batch Processing**: Process multiple addresses efficiently
- **Service Optimization**: Optimize external service calls
- **Data Compression**: Compress geographic data

## Security

- **Access Control**: Customers can only access their own addresses
- **Data Privacy**: Protect sensitive address information
- **Validation Security**: Secure address validation
- **Geographic Privacy**: Protect location privacy
- **Audit Logging**: Log address changes

## Integration Points

- **Geocoding Services**: Google Maps, Here, Mapbox
- **Validation Services**: Address validation APIs
- **Mapping Services**: Delivery zone management
- **Shipping APIs**: Integration with shipping providers
- **CRM Systems**: Customer address management
- **Analytics**: Address usage analytics

## Future Enhancements

- **AI-Powered Validation**: Machine learning address validation
- **Real-time Updates**: Live address verification
- **Mobile Integration**: GPS-based address capture
- **Voice Input**: Voice-activated address entry
- **AR Integration**: Augmented reality address verification
- **Blockchain**: Decentralized address verification
