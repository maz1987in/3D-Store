# Inventory Module

The Inventory module manages material stock, ready-made product inventory, and supply chain operations in the 3D Store application.

## Overview

This module handles:
- Material inventory management
- Ready-made product stock tracking
- Supplier management and relationships
- Purchase order processing
- Stock level monitoring and alerts
- Inventory analytics and reporting
- Automated reorder point management

## Module Structure

```
inventory/
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

### Material
3D printing materials and consumables:
- **Basic Info**: `name`, `type`, `color`, `manufacturer`, `sku`
- **Specifications**: `diameter`, `weight_per_meter`, `density`, `melting_point`
- **Pricing**: `cost_per_gram`, `cost_per_roll`, `markup_percentage`
- **Inventory**: `current_stock`, `reorder_point`, `max_stock`, `unit_of_measure`
- **Quality**: `quality_grade`, `batch_number`, `expiry_date`
- **Metadata**: `created_at`, `updated_at`, `is_active`

### ProductInventory
Ready-made product inventory:
- **Product Info**: `product_id`, `variant_id`, `size`, `color`
- **Stock Levels**: `current_stock`, `reserved_stock`, `available_stock`
- **Reorder Management**: `reorder_point`, `reorder_quantity`, `max_stock`
- **Location**: `warehouse_location`, `bin_number`, `shelf_position`
- **Status**: `is_available`, `is_discontinued`, `last_restocked`
- **Metadata**: `created_at`, `updated_at`

### Supplier
Material and product suppliers:
- **Basic Info**: `name`, `contact_person`, `email`, `phone`, `website`
- **Address**: `address`, `city`, `country`, `postal_code`
- **Business**: `tax_id`, `payment_terms`, `delivery_terms`
- **Rating**: `quality_rating`, `delivery_rating`, `overall_rating`
- **Status**: `is_active`, `is_preferred`, `contract_start_date`
- **Metadata**: `created_at`, `updated_at`

### PurchaseOrder
Material and product purchase orders:
- **Order Info**: `order_number`, `supplier_id`, `order_date`, `expected_delivery`
- **Items**: `purchase_order_items` (relationship)
- **Totals**: `subtotal`, `tax_amount`, `shipping_cost`, `total_amount`
- **Status**: `status`, `payment_status`, `delivery_status`
- **Metadata**: `created_at`, `updated_at`, `received_at`

### PurchaseOrderItem
Individual items in purchase orders:
- **Item Info**: `material_id` or `product_id`, `quantity_ordered`, `unit_price`
- **Received**: `quantity_received`, `quantity_damaged`, `quantity_returned`
- **Quality**: `quality_notes`, `batch_number`, `expiry_date`
- **Totals**: `line_total`, `tax_amount`
- **Status**: `status`, `received_date`

### StockMovement
Inventory movement tracking:
- **Movement Info**: `item_type`, `item_id`, `movement_type`, `quantity`
- **Reference**: `reference_type`, `reference_id`, `order_id`
- **Location**: `from_location`, `to_location`, `warehouse_id`
- **User**: `user_id`, `notes`, `reason`
- **Timestamps**: `movement_date`, `created_at`

## Repository Layer

The `InventoryRepository` class provides data access operations for the Inventory module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Inventory]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities (product, branch, store)
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(inventory_id)` - Get inventory item by ID
- `create(inventory_data)` - Create new inventory item
- `update(inventory_id, inventory_data)` - Update existing inventory item
- `delete(inventory_id)` - Delete inventory item
- `get_all(limit, offset)` - Get all inventory items with pagination

#### Advanced Query Methods
- `get_inventory_with_details(inventory_id)` - Inventory with all related details
- `get_inventory_by_product(product_id)` - Inventory records for specific product
- `get_inventory_by_branch(branch_id)` - Inventory records for specific branch
- `get_inventory_by_store(store_id)` - Inventory records for specific store
- `get_inventory_by_product_and_location(product_id, branch_id, store_id)` - Inventory at specific location
- `get_low_stock_items(threshold)` - Items below quantity threshold
- `get_out_of_stock_items()` - Out of stock items
- `get_in_stock_items()` - In stock items only
- `get_inventory_alerts()` - Items with quantity alerts

#### Inventory Management
- `update_quantity(inventory_id, new_quantity)` - Update item quantity
- `adjust_quantity(inventory_id, adjustment)` - Adjust quantity by amount
- `get_total_quantity_by_product(product_id)` - Total quantity across all locations
- `get_inventory_summary_by_location(location_type, location_id)` - Location inventory summary
- `get_inventory_statistics()` - Inventory statistics for dashboard

### Usage Example

```python
from app.inventory.repository import InventoryRepository

# Initialize repository
inventory_repo = InventoryRepository()

# Get inventory by product
product_inventory = inventory_repo.get_inventory_by_product("product-uuid")

# Get low stock items
low_stock = inventory_repo.get_low_stock_items(threshold=10)

# Update quantity
inventory_repo.update_quantity("inventory-uuid", 50)

# Get inventory alerts
alerts = inventory_repo.get_inventory_alerts()

# Get inventory statistics
stats = inventory_repo.get_inventory_statistics()
```

## API Endpoints

### Material Management
- `GET /inventory/materials` - List all materials
- `GET /inventory/materials/{id}` - Get material details
- `POST /inventory/materials` - Add new material
- `PUT /inventory/materials/{id}` - Update material
- `DELETE /inventory/materials/{id}` - Remove material
- `GET /inventory/materials/{id}/stock` - Get material stock levels

### Product Inventory
- `GET /inventory/products` - List product inventory
- `GET /inventory/products/{id}` - Get product inventory details
- `PUT /inventory/products/{id}/stock` - Update product stock
- `GET /inventory/products/low-stock` - Get low stock products
- `POST /inventory/products/{id}/reserve` - Reserve stock
- `POST /inventory/products/{id}/release` - Release reserved stock

### Supplier Management
- `GET /inventory/suppliers` - List all suppliers
- `GET /inventory/suppliers/{id}` - Get supplier details
- `POST /inventory/suppliers` - Add new supplier
- `PUT /inventory/suppliers/{id}` - Update supplier
- `DELETE /inventory/suppliers/{id}` - Remove supplier
- `GET /inventory/suppliers/{id}/materials` - Get supplier materials

### Purchase Orders
- `GET /inventory/purchase-orders` - List purchase orders
- `GET /inventory/purchase-orders/{id}` - Get purchase order details
- `POST /inventory/purchase-orders` - Create purchase order
- `PUT /inventory/purchase-orders/{id}` - Update purchase order
- `POST /inventory/purchase-orders/{id}/receive` - Receive order items
- `POST /inventory/purchase-orders/{id}/close` - Close purchase order

### Stock Movements
- `GET /inventory/movements` - List stock movements
- `GET /inventory/movements/{id}` - Get movement details
- `POST /inventory/movements` - Record stock movement
- `GET /inventory/movements/item/{item_id}` - Get item movement history

### Inventory Reports
- `GET /inventory/reports/stock-levels` - Stock level report
- `GET /inventory/reports/low-stock` - Low stock alert report
- `GET /inventory/reports/movements` - Stock movement report
- `GET /inventory/reports/supplier-performance` - Supplier performance report

## Business Logic

### Stock Management
1. **Stock Updates**: Real-time stock level updates
2. **Reservation System**: Reserve stock for pending orders
3. **Allocation Logic**: First-in-first-out (FIFO) allocation
4. **Stock Validation**: Prevent overselling and negative stock
5. **Automatic Reordering**: Trigger reorders at reorder points

### Purchase Order Processing
1. **Order Creation**: Generate purchase orders based on stock levels
2. **Supplier Selection**: Choose best supplier based on criteria
3. **Price Negotiation**: Track price changes and negotiations
4. **Delivery Tracking**: Monitor delivery status and delays
5. **Quality Control**: Inspect received materials and products

### Inventory Optimization
1. **ABC Analysis**: Categorize items by value and importance
2. **Demand Forecasting**: Predict future demand based on history
3. **Safety Stock**: Maintain optimal safety stock levels
4. **Turnover Analysis**: Monitor inventory turnover rates
5. **Cost Optimization**: Minimize carrying costs and stockouts

### Quality Management
1. **Batch Tracking**: Track materials by batch and lot numbers
2. **Expiry Management**: Monitor and alert on expiring materials
3. **Quality Inspections**: Inspect received materials for defects
4. **Supplier Rating**: Rate suppliers based on quality and delivery
5. **Defect Management**: Handle and track defective materials

## Validation Schemas

### MaterialCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "type": "string (required, enum: PLA|ABS|PETG|TPU|etc)",
    "color": "string (required, max 100 chars)",
    "manufacturer": "string (required, max 255 chars)",
    "sku": "string (required, max 100 chars, unique)",
    "diameter": "float (required, min 0)",
    "weight_per_meter": "float (required, min 0)",
    "density": "float (required, min 0)",
    "cost_per_gram": "decimal (required, min 0)",
    "current_stock": "float (required, min 0)",
    "reorder_point": "float (required, min 0)",
    "max_stock": "float (required, min 0)",
    "unit_of_measure": "string (required, enum: grams|meters|rolls)"
}
```

### ProductInventorySchema
```python
{
    "product_id": "uuid (required)",
    "variant_id": "uuid (optional)",
    "size": "string (optional, max 50 chars)",
    "color": "string (optional, max 50 chars)",
    "current_stock": "integer (required, min 0)",
    "reorder_point": "integer (required, min 0)",
    "reorder_quantity": "integer (required, min 1)",
    "max_stock": "integer (required, min 0)",
    "warehouse_location": "string (optional, max 100 chars)",
    "bin_number": "string (optional, max 50 chars)"
}
```

### PurchaseOrderCreateSchema
```python
{
    "supplier_id": "uuid (required)",
    "order_date": "date (required)",
    "expected_delivery": "date (required)",
    "items": [
        {
            "item_type": "string (required, enum: material|product)",
            "item_id": "uuid (required)",
            "quantity_ordered": "integer (required, min 1)",
            "unit_price": "decimal (required, min 0)",
            "notes": "string (optional)"
        }
    ],
    "notes": "string (optional)"
}
```

### StockMovementSchema
```python
{
    "item_type": "string (required, enum: material|product)",
    "item_id": "uuid (required)",
    "movement_type": "string (required, enum: in|out|transfer|adjustment)",
    "quantity": "float (required)",
    "reference_type": "string (optional, enum: order|purchase|adjustment)",
    "reference_id": "uuid (optional)",
    "from_location": "string (optional)",
    "to_location": "string (optional)",
    "notes": "string (optional)",
    "reason": "string (optional)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When material/product not found
- **BusinessLogicException**: For inventory rule violations
- **InsufficientStockException**: When stock is insufficient
- **InventoryException**: For inventory-specific errors

## Dependencies

- **Product Module**: For product information and relationships
- **Supplier Module**: For supplier management
- **Order Module**: For order processing and stock allocation
- **Notification Module**: For low stock alerts
- **Reporting Module**: For inventory analytics
- **File Storage**: For supplier documents and certificates

## Usage Examples

### Material Management
```python
from app.inventory.service import InventoryService
from app.inventory.schemas import MaterialCreateSchema

service = InventoryService()
material_data = {
    "name": "PLA White 1.75mm",
    "type": "PLA",
    "color": "White",
    "manufacturer": "Polymaker",
    "sku": "PLA-WH-175",
    "diameter": 1.75,
    "weight_per_meter": 2.5,
    "density": 1.24,
    "cost_per_gram": 0.05,
    "current_stock": 1000.0,
    "reorder_point": 200.0,
    "max_stock": 2000.0,
    "unit_of_measure": "grams"
}

material = service.create_material(material_data)
```

### Stock Management
```python
# Update stock levels
service.update_stock(material_id, 500.0, "in", "purchase_order", po_id)

# Reserve stock for order
service.reserve_stock(product_id, 10, order_id)

# Release reserved stock
service.release_stock(product_id, 10, order_id)

# Check stock availability
available = service.check_stock_availability(product_id, 5)
```

### Purchase Order Processing
```python
# Create purchase order
po_data = {
    "supplier_id": "supplier-uuid",
    "order_date": "2024-01-15",
    "expected_delivery": "2024-01-25",
    "items": [
        {
            "item_type": "material",
            "item_id": "material-uuid",
            "quantity_ordered": 1000,
            "unit_price": 0.05
        }
    ]
}

purchase_order = service.create_purchase_order(po_data)

# Receive order items
service.receive_order_items(po_id, {
    "material-uuid": {
        "quantity_received": 1000,
        "quality_notes": "Good quality",
        "batch_number": "BATCH001"
    }
})
```

### Inventory Reports
```python
# Get low stock alerts
low_stock_items = service.get_low_stock_items()

# Get stock movement history
movements = service.get_stock_movements(item_id, start_date, end_date)

# Generate inventory report
report = service.generate_inventory_report(report_type="stock_levels")
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frequently accessed inventory data cached
- **Batch Operations**: Bulk stock updates for performance
- **Real-time Updates**: WebSocket for real-time stock updates
- **Background Processing**: Automated reorder processing

## Security

- **Access Control**: Role-based permissions for inventory management
- **Audit Logging**: All inventory changes logged
- **Data Validation**: Input validation and sanitization
- **Fraud Prevention**: Detect unusual inventory patterns
- **Backup and Recovery**: Regular inventory data backups

## Integration Points

- **ERP Systems**: Integration with enterprise resource planning
- **Supplier Portals**: Direct integration with supplier systems
- **Barcode Scanners**: Support for barcode scanning
- **RFID Systems**: Radio frequency identification support
- **Analytics Platforms**: Business intelligence integration

## Future Enhancements

- **AI-Powered Forecasting**: Machine learning demand prediction
- **IoT Integration**: Smart warehouse sensors and automation
- **Blockchain**: Supply chain transparency and traceability
- **Mobile App**: Mobile inventory management application
- **Advanced Analytics**: Predictive analytics and optimization
