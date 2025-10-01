# Cart Module

The Cart module manages shopping cart functionality, item management, and cart persistence in the 3D Store application, providing a seamless shopping experience for customers.

## Overview

This module handles:
- Shopping cart creation and management
- Cart item addition, removal, and updates
- Cart persistence across sessions
- Price calculations and discounts
- Cart validation and checkout preparation
- Cart analytics and abandoned cart recovery

## Module Structure

```
cart/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── schemas.py          # Input validation schemas
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Cart
Main shopping cart entity with the following key attributes:
- **Basic Info**: `cart_id`, `customer_id`, `session_id`, `status`
- **Pricing**: `subtotal`, `tax_amount`, `shipping_cost`, `total_amount`
- **Discounts**: `discount_amount`, `coupon_code`, `promotion_id`
- **Timestamps**: `created_at`, `updated_at`, `expires_at`
- **Metadata**: `notes`, `special_instructions`, `is_abandoned`

### CartItem
Individual items in the shopping cart:
- **Item Info**: `cart_id`, `product_id`, `quantity`, `unit_price`
- **Customization**: `custom_design`, `print_settings`, `material_choice`
- **3D Printing**: `file_url`, `print_estimates`, `is_custom_print`
- **Pricing**: `line_total`, `discount_amount`, `tax_amount`
- **Status**: `is_available`, `validation_status`, `validation_notes`
- **Metadata**: `created_at`, `updated_at`

### CartDiscount
Discount and promotion tracking:
- **Discount Info**: `cart_id`, `discount_type`, `discount_value`
- **Promotion**: `promotion_id`, `coupon_code`, `promotion_name`
- **Conditions**: `minimum_amount`, `maximum_discount`, `valid_until`
- **Status**: `is_applied`, `applied_at`, `expires_at`
- **Metadata**: `created_at`, `updated_at`

### CartSession
Cart session management:
- **Session Info**: `session_id`, `customer_id`, `cart_id`
- **Device**: `device_type`, `user_agent`, `ip_address`
- **Location**: `country`, `city`, `timezone`
- **Activity**: `last_activity`, `page_views`, `time_on_site`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Cart Management
- `GET /cart` - Get current cart
- `POST /cart` - Create new cart
- `PUT /cart` - Update cart
- `DELETE /cart` - Clear cart
- `GET /cart/summary` - Get cart summary
- `POST /cart/validate` - Validate cart items

### Cart Items
- `GET /cart/items` - List cart items
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{id}` - Update cart item
- `DELETE /cart/items/{id}` - Remove cart item
- `POST /cart/items/bulk` - Bulk update cart items

### Cart Customization
- `POST /cart/items/{id}/customize` - Customize cart item
- `POST /cart/items/{id}/upload` - Upload 3D model file
- `GET /cart/items/{id}/preview` - Get item preview
- `POST /cart/items/{id}/estimate` - Get print estimate

### Discounts and Promotions
- `GET /cart/discounts` - List available discounts
- `POST /cart/discounts/apply` - Apply discount code
- `DELETE /cart/discounts/{id}` - Remove discount
- `GET /cart/promotions` - List available promotions
- `POST /cart/promotions/apply` - Apply promotion

### Cart Persistence
- `POST /cart/save` - Save cart for later
- `GET /cart/saved` - Get saved carts
- `POST /cart/restore` - Restore saved cart
- `DELETE /cart/saved/{id}` - Delete saved cart

### Cart Analytics
- `GET /cart/analytics` - Get cart analytics
- `GET /cart/abandoned` - Get abandoned carts
- `POST /cart/abandoned/recover` - Recover abandoned cart
- `GET /cart/trends` - Get cart trends

## Business Logic

### Cart Creation
1. **Session Management**: Create or retrieve cart session
2. **Customer Association**: Link cart to customer if logged in
3. **Initialization**: Initialize cart with default settings
4. **Expiration**: Set cart expiration time
5. **Validation**: Validate cart creation parameters
6. **Persistence**: Save cart to database

### Item Management
1. **Item Addition**: Add products to cart with validation
2. **Quantity Updates**: Update item quantities with stock checks
3. **Customization**: Handle 3D printing customizations
4. **File Upload**: Process 3D model file uploads
5. **Price Calculation**: Calculate item and line totals
6. **Availability Check**: Verify item availability

### Price Calculation
1. **Base Pricing**: Calculate base item prices
2. **Customization Costs**: Add customization and printing costs
3. **Tax Calculation**: Calculate applicable taxes
4. **Shipping Costs**: Calculate shipping based on location
5. **Discount Application**: Apply discounts and promotions
6. **Total Calculation**: Calculate final cart total

### Cart Validation
1. **Item Validation**: Validate all cart items
2. **Stock Check**: Verify item availability
3. **Price Validation**: Ensure prices are current
4. **Customization Check**: Validate 3D printing customizations
5. **Shipping Validation**: Verify shipping options
6. **Error Reporting**: Report validation errors

### Abandoned Cart Recovery
1. **Detection**: Identify abandoned carts
2. **Analysis**: Analyze abandonment patterns
3. **Recovery Campaigns**: Trigger recovery emails
4. **Incentives**: Offer discounts to recover carts
5. **Tracking**: Track recovery success rates
6. **Optimization**: Optimize recovery strategies

## Validation Schemas

### CartCreateSchema
```python
{
    "customer_id": "uuid (optional)",
    "session_id": "string (optional)",
    "notes": "string (optional, max 500 chars)",
    "special_instructions": "string (optional, max 1000 chars)"
}
```

### CartItemCreateSchema
```python
{
    "product_id": "uuid (required)",
    "quantity": "integer (required, min 1)",
    "custom_design": "string (optional, max 1000 chars)",
    "print_settings": {
        "layer_height": "float (optional, min 0.1, max 0.5)",
        "infill_percentage": "integer (optional, min 0, max 100)",
        "support_enabled": "boolean (optional)",
        "material_choice": "uuid (optional)"
    },
    "file_url": "string (optional, valid URL)",
    "is_custom_print": "boolean (optional, default false)"
}
```

### CartItemUpdateSchema
```python
{
    "quantity": "integer (optional, min 1)",
    "custom_design": "string (optional, max 1000 chars)",
    "print_settings": "object (optional)",
    "file_url": "string (optional, valid URL)"
}
```

### CartDiscountSchema
```python
{
    "discount_type": "string (required, enum: percentage|fixed|free_shipping)",
    "discount_value": "decimal (required, min 0)",
    "coupon_code": "string (optional, max 50 chars)",
    "promotion_id": "uuid (optional)",
    "minimum_amount": "decimal (optional, min 0)",
    "maximum_discount": "decimal (optional, min 0)"
}
```

### CartValidationSchema
```python
{
    "validate_stock": "boolean (optional, default true)",
    "validate_pricing": "boolean (optional, default true)",
    "validate_customization": "boolean (optional, default true)",
    "validate_shipping": "boolean (optional, default true)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When cart or item not found
- **BusinessLogicException**: For business rule violations
- **StockException**: For insufficient stock errors
- **PricingException**: For pricing calculation errors

## Dependencies

- **Product Module**: For product information and pricing
- **User Module**: For customer information
- **Order Module**: For checkout processing
- **Payment Module**: For payment processing
- **Notification Module**: For cart recovery emails
- **File Storage**: For 3D model file storage

## Usage Examples

### Creating a Cart
```python
from app.cart.service import CartService
from app.cart.schemas import CartCreateSchema

service = CartService()
cart_data = {
    "customer_id": "customer-uuid",
    "session_id": "session-123",
    "notes": "Birthday gift order",
    "special_instructions": "Please wrap as gift"
}

cart = service.create_cart(cart_data)
```

### Managing Cart Items
```python
# Add item to cart
item_data = {
    "product_id": "product-uuid",
    "quantity": 2,
    "custom_design": "Custom text: 'Happy Birthday'",
    "print_settings": {
        "layer_height": 0.2,
        "infill_percentage": 20,
        "support_enabled": True,
        "material_choice": "material-uuid"
    },
    "is_custom_print": True
}

cart_item = service.add_cart_item(cart_id, item_data)

# Update cart item
service.update_cart_item(cart_item_id, {
    "quantity": 3,
    "custom_design": "Updated design"
})

# Remove cart item
service.remove_cart_item(cart_item_id)
```

### Applying Discounts
```python
# Apply discount code
discount_data = {
    "discount_type": "percentage",
    "discount_value": 10.0,
    "coupon_code": "SAVE10",
    "minimum_amount": 100.0
}

discount = service.apply_discount(cart_id, discount_data)

# Remove discount
service.remove_discount(cart_id, discount_id)
```

### Cart Validation
```python
# Validate cart
validation_result = service.validate_cart(cart_id, {
    "validate_stock": True,
    "validate_pricing": True,
    "validate_customization": True,
    "validate_shipping": True
})

# Get cart summary
summary = service.get_cart_summary(cart_id)
```

### Cart Persistence
```python
# Save cart for later
saved_cart = service.save_cart(cart_id, "My Saved Cart")

# Get saved carts
saved_carts = service.get_saved_carts(customer_id)

# Restore saved cart
service.restore_cart(customer_id, saved_cart_id)
```

### Abandoned Cart Recovery
```python
# Get abandoned carts
abandoned_carts = service.get_abandoned_carts()

# Recover abandoned cart
service.recover_abandoned_cart(cart_id, recovery_email)

# Get cart analytics
analytics = service.get_cart_analytics(start_date, end_date)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frequently accessed cart data cached
- **Session Management**: Efficient session handling
- **Batch Operations**: Bulk operations for cart updates
- **Real-time Updates**: WebSocket for real-time cart updates

## Security

- **Access Control**: Customers can only access their own carts
- **Session Security**: Secure session management
- **Data Validation**: Input validation and sanitization
- **CSRF Protection**: Cross-site request forgery protection
- **Rate Limiting**: API endpoints protected against abuse

## Integration Points

- **Product Catalog**: Integration with product management
- **Pricing Engine**: Dynamic pricing calculation
- **Inventory System**: Real-time stock checking
- **Payment Gateway**: Checkout processing
- **Email Service**: Cart recovery notifications
- **Analytics**: Cart behavior tracking

## Future Enhancements

- **AI Recommendations**: Machine learning product recommendations
- **Social Shopping**: Share carts with friends and family
- **Wishlist Integration**: Convert wishlist items to cart
- **Mobile App**: Native mobile cart management
- **Voice Commands**: Voice-activated cart management
- **AR Integration**: Augmented reality product preview
