# Database Indexing Strategy

This document outlines the comprehensive database indexing strategy implemented for the 3D Store application to optimize query performance.

## Overview

Database indexes are crucial for query performance, especially as the application scales. This strategy covers all major tables and their frequently queried columns, including single-column indexes, composite indexes, and specialized indexes for common query patterns.

## Index Categories

### 1. Primary Key Indexes
All tables have UUID primary keys with automatic indexes.

### 2. Foreign Key Indexes
All foreign key columns have indexes for efficient joins.

### 3. Unique Constraint Indexes
Columns with unique constraints automatically have indexes.

### 4. Performance Indexes
Additional indexes added for common query patterns and filtering.

## Table-Specific Indexing Strategy

### Users Table (`users`)

**Purpose**: User authentication, profile management, and user type filtering.

**Indexes**:
- `idx_users_active` - Filter active/inactive users
- `idx_users_user_type` - Filter by user type (USER, ADMIN, etc.)
- `idx_users_language` - Filter by language preference
- `idx_users_create_date` - Sort by registration date
- `idx_users_modified_date` - Sort by last modification
- `idx_users_phone_email` - Composite index for phone/email lookups
- `idx_users_active_type` - Composite index for active users by type

**Common Queries**:
```sql
-- Active users by type
SELECT * FROM users WHERE active = 1 AND user_type = 'USER';

-- Users by language
SELECT * FROM users WHERE language = 'ARABIC';

-- Recent users
SELECT * FROM users ORDER BY create_date DESC;
```

### Product Table (`product`)

**Purpose**: Product catalog, search, and filtering.

**Indexes**:
- `idx_product_type` - Filter by product type (service, ready_made, material)
- `idx_product_category_type` - Filter by category and type
- `idx_product_price` - Sort by price
- `idx_product_currency` - Filter by currency
- `idx_product_dynamic_pricing` - Filter dynamic pricing products
- `idx_product_category_price` - Filter by category and sort by price
- `idx_product_type_price` - Filter by type and sort by price
- `idx_product_sku` - Lookup by SKU
- `idx_product_subcategory` - Filter by subcategory

**Common Queries**:
```sql
-- Products by category and type
SELECT * FROM product WHERE category_id = ? AND product_type = 'service';

-- Price range filtering
SELECT * FROM product WHERE base_price BETWEEN ? AND ?;

-- Products by category, sorted by price
SELECT * FROM product WHERE category_id = ? ORDER BY base_price ASC;
```

### Category Table (`category`)

**Purpose**: Category hierarchy and filtering.

**Indexes**:
- `idx_category_parent` - Filter by parent category
- `idx_category_active` - Filter active categories
- `idx_category_featured` - Filter featured categories
- `idx_category_active_featured` - Composite for active featured categories
- `idx_category_slug` - Lookup by URL slug
- `idx_category_parent_active` - Filter by parent and active status

**Common Queries**:
```sql
-- Active categories by parent
SELECT * FROM category WHERE parent_id = ? AND is_active = 1;

-- Featured categories
SELECT * FROM category WHERE is_featured = 1 AND is_active = 1;

-- Category by slug
SELECT * FROM category WHERE slug = ?;
```

### Customer Table (`customer`)

**Purpose**: Customer management and filtering.

**Indexes**:
- `idx_customer_user_id` - Link to user account
- `idx_customer_mobile` - Lookup by mobile number
- `idx_customer_phone` - Lookup by phone number
- `idx_customer_city` - Filter by city
- `idx_customer_country` - Filter by country
- `idx_customer_customer_type` - Filter by customer type
- `idx_customer_status` - Filter by status
- `idx_customer_create_date` - Sort by registration date
- `idx_customer_modified_date` - Sort by last modification
- `idx_customer_user_status` - Composite for user and status

**Common Queries**:
```sql
-- Customers by city and status
SELECT * FROM customer WHERE city = ? AND status = 'active';

-- Customer by mobile
SELECT * FROM customer WHERE mobile = ?;

-- Recent customers
SELECT * FROM customer ORDER BY create_date DESC;
```

### Order Table (`order`)

**Purpose**: Order management, tracking, and reporting.

**Indexes**:
- `idx_order_customer` - Filter orders by customer
- `idx_order_status` - Filter by order status
- `idx_order_type` - Filter by order type
- `idx_order_priority` - Filter by priority
- `idx_order_payment_status` - Filter by payment status
- `idx_order_payment_method` - Filter by payment method
- `idx_order_expected_delivery` - Filter by delivery date
- `idx_order_estimated_completion` - Filter by completion date
- `idx_order_currency` - Filter by currency
- `idx_order_customer_status` - Composite for customer and status
- `idx_order_status_date` - Composite for status and date
- `idx_order_customer_date` - Composite for customer and date
- `idx_order_type_status` - Composite for type and status
- `idx_order_payment_status_date` - Composite for payment status and date
- `idx_order_total_amount` - Sort by total amount
- `idx_order_priority_status` - Composite for priority and status

**Common Queries**:
```sql
-- Orders by customer and status
SELECT * FROM order WHERE customer_id = ? AND status = 'pending';

-- Orders by date range and status
SELECT * FROM order WHERE order_date BETWEEN ? AND ? AND status = 'completed';

-- High priority pending orders
SELECT * FROM order WHERE priority = 'high' AND status = 'pending';
```

### Order Item Table (`order_item`)

**Purpose**: Order line items and product tracking.

**Indexes**:
- `idx_order_item_order` - Filter items by order
- `idx_order_item_product` - Filter items by product
- `idx_order_item_order_product` - Composite for order and product

**Common Queries**:
```sql
-- Items for specific order
SELECT * FROM order_item WHERE order_id = ?;

-- Orders containing specific product
SELECT * FROM order_item WHERE product_id = ?;
```

### Inventory Table (`inventory`)

**Purpose**: Stock management and tracking.

**Indexes**:
- `idx_inventory_product_branch` - Filter by product and branch
- `idx_inventory_branch_store` - Filter by branch and store
- `idx_inventory_quantity` - Filter by quantity
- `idx_inventory_quantity_alert` - Filter by alert threshold
- `idx_inventory_product_quantity` - Composite for product and quantity
- `idx_inventory_branch_quantity` - Composite for branch and quantity
- `idx_inventory_store_quantity` - Composite for store and quantity
- `idx_inventory_create_date` - Sort by creation date
- `idx_inventory_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Inventory for product at branch
SELECT * FROM inventory WHERE product_id = ? AND branch_id = ?;

-- Low stock items
SELECT * FROM inventory WHERE quantity <= quantity_alert;

-- Inventory by branch
SELECT * FROM inventory WHERE branch_id = ? ORDER BY quantity ASC;
```

### Transaction Table (`transaction`)

**Purpose**: Inventory movement tracking and reporting.

**Indexes**:
- `idx_transaction_product` - Filter by product
- `idx_transaction_type` - Filter by transaction type
- `idx_transaction_date` - Filter by date
- `idx_transaction_financial_year` - Filter by financial year
- `idx_transaction_from_location` - Filter by source location
- `idx_transaction_to_location` - Filter by destination location
- `idx_transaction_product_type` - Composite for product and type
- `idx_transaction_type_date` - Composite for type and date
- `idx_transaction_from_to` - Composite for source and destination
- `idx_transaction_create_date` - Sort by creation date
- `idx_transaction_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Transactions for product
SELECT * FROM transaction WHERE product_id = ? ORDER BY transaction_date DESC;

-- Transactions by type and date range
SELECT * FROM transaction WHERE transaction_type = ? AND transaction_date BETWEEN ? AND ?;

-- Movement between locations
SELECT * FROM transaction WHERE from_location_id = ? AND to_location_id = ?;
```

### Payment Transaction Table (`payment_transaction`)

**Purpose**: Payment processing and tracking.

**Indexes**:
- `idx_payment_transaction_reference` - Lookup by reference ID
- `idx_payment_transaction_status` - Filter by payment status
- `idx_payment_transaction_gateway` - Filter by gateway transaction ID
- `idx_payment_transaction_gateway_status` - Filter by gateway status
- `idx_payment_transaction_amount` - Filter by amount
- `idx_payment_transaction_model` - Filter by model type and ID
- `idx_payment_transaction_requester` - Filter by requester
- `idx_payment_transaction_payment_gateway` - Filter by payment gateway
- `idx_payment_transaction_payment_type` - Filter by payment type
- `idx_payment_transaction_create_date` - Sort by creation date
- `idx_payment_transaction_last_modified` - Sort by last modification
- `idx_payment_transaction_retry` - Filter by retry count
- `idx_payment_transaction_is_online` - Filter by online status

**Common Queries**:
```sql
-- Payment by reference
SELECT * FROM payment_transaction WHERE reference_id = ?;

-- Failed payments
SELECT * FROM payment_transaction WHERE payment_status = 'failed';

-- Payments by gateway
SELECT * FROM payment_transaction WHERE payment_gateway = ? ORDER BY create_date DESC;
```

### Quotation Table (`quotation`)

**Purpose**: Quote management and tracking.

**Indexes**:
- `idx_quotation_customer` - Filter by customer
- `idx_quotation_status` - Filter by status
- `idx_quotation_valid_until` - Filter by validity date
- `idx_quotation_create_date` - Sort by creation date
- `idx_quotation_modified_date` - Sort by modification date
- `idx_quotation_customer_status` - Composite for customer and status
- `idx_quotation_status_date` - Composite for status and date
- `idx_quotation_total_amount` - Sort by total amount
- `idx_quotation_currency` - Filter by currency

**Common Queries**:
```sql
-- Quotations by customer
SELECT * FROM quotation WHERE customer_id = ? ORDER BY create_date DESC;

-- Valid quotations
SELECT * FROM quotation WHERE status = 'active' AND valid_until > NOW();

-- Quotations by amount range
SELECT * FROM quotation WHERE total_amount BETWEEN ? AND ?;
```

### Invoice Table (`invoice`)

**Purpose**: Invoice management and tracking.

**Indexes**:
- `idx_invoice_customer` - Filter by customer
- `idx_invoice_order` - Filter by order
- `idx_invoice_status` - Filter by status
- `idx_invoice_due_date` - Filter by due date
- `idx_invoice_create_date` - Sort by creation date
- `idx_invoice_modified_date` - Sort by modification date
- `idx_invoice_customer_status` - Composite for customer and status
- `idx_invoice_status_date` - Composite for status and date
- `idx_invoice_total_amount` - Sort by total amount
- `idx_invoice_currency` - Filter by currency
- `idx_invoice_invoice_number` - Lookup by invoice number

**Common Queries**:
```sql
-- Invoices by customer
SELECT * FROM invoice WHERE customer_id = ? ORDER BY create_date DESC;

-- Overdue invoices
SELECT * FROM invoice WHERE status = 'unpaid' AND due_date < NOW();

-- Invoices by amount
SELECT * FROM invoice WHERE total_amount > ? ORDER BY total_amount DESC;
```

### Branch Table (`branch`)

**Purpose**: Branch management and filtering.

**Indexes**:
- `idx_branch_company` - Filter by company
- `idx_branch_active` - Filter active branches
- `idx_branch_city` - Filter by city
- `idx_branch_country` - Filter by country
- `idx_branch_company_active` - Composite for company and active status
- `idx_branch_create_date` - Sort by creation date
- `idx_branch_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Active branches by company
SELECT * FROM branch WHERE company_id = ? AND is_active = 1;

-- Branches by city
SELECT * FROM branch WHERE city = ? ORDER BY name;
```

### Store Table (`store`)

**Purpose**: Store management and filtering.

**Indexes**:
- `idx_store_branch` - Filter by branch
- `idx_store_active` - Filter active stores
- `idx_store_city` - Filter by city
- `idx_store_country` - Filter by country
- `idx_store_branch_active` - Composite for branch and active status
- `idx_store_create_date` - Sort by creation date
- `idx_store_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Active stores by branch
SELECT * FROM store WHERE branch_id = ? AND is_active = 1;

-- Stores by city
SELECT * FROM store WHERE city = ? ORDER BY name;
```

### Company Table (`company`)

**Purpose**: Company management and filtering.

**Indexes**:
- `idx_company_active` - Filter active companies
- `idx_company_country` - Filter by country
- `idx_company_create_date` - Sort by creation date
- `idx_company_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Active companies
SELECT * FROM company WHERE is_active = 1;

-- Companies by country
SELECT * FROM company WHERE country = ? ORDER BY name;
```

### Expense Table (`expense`)

**Purpose**: Expense tracking and approval workflow.

**Indexes**:
- `idx_expense_category` - Filter by category
- `idx_expense_branch` - Filter by branch
- `idx_expense_status` - Filter by status
- `idx_expense_approver` - Filter by approver
- `idx_expense_create_date` - Sort by creation date
- `idx_expense_modified_date` - Sort by modification date
- `idx_expense_category_status` - Composite for category and status
- `idx_expense_branch_status` - Composite for branch and status
- `idx_expense_amount` - Sort by amount
- `idx_expense_currency` - Filter by currency
- `idx_expense_expense_date` - Filter by expense date

**Common Queries**:
```sql
-- Expenses by category and status
SELECT * FROM expense WHERE category_id = ? AND status = 'pending';

-- Expenses by amount range
SELECT * FROM expense WHERE amount BETWEEN ? AND ? ORDER BY amount DESC;

-- Expenses by branch
SELECT * FROM expense WHERE branch_id = ? ORDER BY expense_date DESC;
```

### Expense Category Table (`expense_category`)

**Purpose**: Expense category hierarchy.

**Indexes**:
- `idx_expense_category_active` - Filter active categories
- `idx_expense_category_parent` - Filter by parent category
- `idx_expense_category_parent_active` - Composite for parent and active status
- `idx_expense_category_create_date` - Sort by creation date
- `idx_expense_category_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Active categories by parent
SELECT * FROM expense_category WHERE parent_id = ? AND is_active = 1;

-- Top-level categories
SELECT * FROM expense_category WHERE parent_id IS NULL AND is_active = 1;
```

### Financial Year Table (`fiscal_year`)

**Purpose**: Financial year management.

**Indexes**:
- `idx_fiscal_year_active` - Filter active financial years
- `idx_fiscal_year_start_date` - Filter by start date
- `idx_fiscal_year_end_date` - Filter by end date
- `idx_fiscal_year_create_date` - Sort by creation date
- `idx_fiscal_year_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Active financial year
SELECT * FROM fiscal_year WHERE is_active = 1;

-- Financial year by date
SELECT * FROM fiscal_year WHERE ? BETWEEN start_date AND end_date;
```

### Fiscal Period Table (`fiscal_period`)

**Purpose**: Fiscal period management.

**Indexes**:
- `idx_fiscal_period_year` - Filter by financial year
- `idx_fiscal_period_start_date` - Filter by start date
- `idx_fiscal_period_end_date` - Filter by end date
- `idx_fiscal_period_create_date` - Sort by creation date
- `idx_fiscal_period_modified_date` - Sort by modification date
- `idx_fiscal_period_year_start` - Composite for year and start date

**Common Queries**:
```sql
-- Periods by financial year
SELECT * FROM fiscal_period WHERE fiscal_year_id = ? ORDER BY start_date;

-- Current period
SELECT * FROM fiscal_period WHERE ? BETWEEN start_date AND end_date;
```

### Rating Table (`rating`)

**Purpose**: Product and service ratings.

**Indexes**:
- `idx_rating_user` - Filter by user
- `idx_rating_product` - Filter by product
- `idx_rating_order` - Filter by order
- `idx_rating_rating` - Filter by rating value
- `idx_rating_create_date` - Sort by creation date
- `idx_rating_modified_date` - Sort by modification date
- `idx_rating_user_product` - Composite for user and product
- `idx_rating_product_rating` - Composite for product and rating

**Common Queries**:
```sql
-- Ratings by product
SELECT * FROM rating WHERE product_id = ? ORDER BY create_date DESC;

-- High ratings
SELECT * FROM rating WHERE rating >= 4 ORDER BY create_date DESC;

-- User's ratings
SELECT * FROM rating WHERE user_id = ? ORDER BY create_date DESC;
```

### Media Table (`media`)

**Purpose**: File and media management.

**Indexes**:
- `idx_media_model_type` - Filter by model type
- `idx_media_model_id` - Filter by model ID
- `idx_media_model` - Composite for model type and ID
- `idx_media_create_date` - Sort by creation date
- `idx_media_modified_date` - Sort by modification date
- `idx_media_last_modified` - Sort by last modification

**Common Queries**:
```sql
-- Media by model
SELECT * FROM media WHERE model_type = ? AND model_id = ?;

-- Recent media
SELECT * FROM media ORDER BY create_date DESC;
```

### Shipping Address Table (`shipping_address`)

**Purpose**: Customer shipping addresses.

**Indexes**:
- `idx_shipping_address_customer` - Filter by customer
- `idx_shipping_address_city` - Filter by city
- `idx_shipping_address_country` - Filter by country
- `idx_shipping_address_postal_code` - Filter by postal code
- `idx_shipping_address_is_default` - Filter default addresses
- `idx_shipping_address_customer_default` - Composite for customer and default
- `idx_shipping_address_create_date` - Sort by creation date
- `idx_shipping_address_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Customer's default address
SELECT * FROM shipping_address WHERE customer_id = ? AND is_default = 1;

-- Addresses by city
SELECT * FROM shipping_address WHERE city = ? ORDER BY customer_id;
```

### Staff Table (`staff`)

**Purpose**: Staff management and organization.

**Indexes**:
- `idx_staff_user` - Link to user account
- `idx_staff_branch` - Filter by branch
- `idx_staff_department` - Filter by department
- `idx_staff_position` - Filter by position
- `idx_staff_active` - Filter active staff
- `idx_staff_branch_active` - Composite for branch and active status
- `idx_staff_create_date` - Sort by creation date
- `idx_staff_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Staff by branch
SELECT * FROM staff WHERE branch_id = ? AND is_active = 1;

-- Staff by department
SELECT * FROM staff WHERE department = ? ORDER BY name;
```

### Role Table (`role`)

**Purpose**: Role management.

**Indexes**:
- `idx_role_active` - Filter active roles
- `idx_role_create_date` - Sort by creation date
- `idx_role_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Active roles
SELECT * FROM role WHERE is_active = 1 ORDER BY name;
```

### Permission Table (`permission`)

**Purpose**: Permission management.

**Indexes**:
- `idx_permission_resource` - Filter by resource
- `idx_permission_action` - Filter by action
- `idx_permission_resource_action` - Composite for resource and action
- `idx_permission_create_date` - Sort by creation date
- `idx_permission_modified_date` - Sort by modification date

**Common Queries**:
```sql
-- Permissions by resource
SELECT * FROM permission WHERE resource = ? ORDER BY action;

-- Specific permission
SELECT * FROM permission WHERE resource = ? AND action = ?;
```

### User Roles Table (`user_roles`)

**Purpose**: User-role assignments.

**Indexes**:
- `idx_user_roles_user` - Filter by user
- `idx_user_roles_role` - Filter by role
- `idx_user_roles_user_role` - Composite for user and role

**Common Queries**:
```sql
-- User's roles
SELECT * FROM user_roles WHERE user_id = ?;

-- Role assignments
SELECT * FROM user_roles WHERE role_id = ?;
```

### Role Permissions Table (`role_permissions`)

**Purpose**: Role-permission assignments.

**Indexes**:
- `idx_role_permissions_role` - Filter by role
- `idx_role_permissions_permission` - Filter by permission
- `idx_role_permissions_role_permission` - Composite for role and permission

**Common Queries**:
```sql
-- Role's permissions
SELECT * FROM role_permissions WHERE role_id = ?;

-- Permission assignments
SELECT * FROM role_permissions WHERE permission_id = ?;
```

### Tracking Table (`tracking`)

**Purpose**: Audit trail and activity tracking.

**Indexes**:
- `idx_tracking_user` - Filter by user
- `idx_tracking_action` - Filter by action
- `idx_tracking_model_type` - Filter by model type
- `idx_tracking_model_id` - Filter by model ID
- `idx_tracking_model` - Composite for model type and ID
- `idx_tracking_create_date` - Sort by creation date
- `idx_tracking_user_action` - Composite for user and action
- `idx_tracking_action_date` - Composite for action and date

**Common Queries**:
```sql
-- User activity
SELECT * FROM tracking WHERE user_id = ? ORDER BY create_date DESC;

-- Model history
SELECT * FROM tracking WHERE model_type = ? AND model_id = ? ORDER BY create_date DESC;

-- Action history
SELECT * FROM tracking WHERE action = ? ORDER BY create_date DESC;
```

## Index Maintenance

### Monitoring Index Usage

```sql
-- Check index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Check unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY tablename, indexname;
```

### Index Size Monitoring

```sql
-- Check index sizes
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Performance Impact

**Benefits**:
- Faster query execution
- Reduced CPU usage
- Better concurrency
- Improved user experience

**Costs**:
- Additional storage space
- Slower INSERT/UPDATE/DELETE operations
- Maintenance overhead

## Best Practices

### 1. Index Design Principles

- **Selectivity**: Index columns with high selectivity (many unique values)
- **Query Patterns**: Index columns frequently used in WHERE clauses
- **Composite Indexes**: Order columns by selectivity (most selective first)
- **Covering Indexes**: Include columns needed for SELECT in composite indexes

### 2. Index Maintenance

- **Regular Monitoring**: Check index usage and performance
- **Rebuilding**: Rebuild indexes periodically for optimal performance
- **Cleanup**: Remove unused indexes to reduce overhead

### 3. Query Optimization

- **Use EXPLAIN**: Analyze query execution plans
- **Index Hints**: Use appropriate index hints when needed
- **Avoid Functions**: Don't use functions on indexed columns in WHERE clauses

### 4. Monitoring and Alerts

- **Performance Metrics**: Monitor query execution times
- **Index Usage**: Track index utilization
- **Storage Growth**: Monitor index storage requirements

## Migration Strategy

### 1. Staged Rollout

1. **Development**: Test indexes in development environment
2. **Staging**: Validate performance improvements in staging
3. **Production**: Deploy during maintenance windows

### 2. Performance Testing

- **Before/After**: Compare query performance before and after indexing
- **Load Testing**: Test under realistic load conditions
- **Monitoring**: Continuous monitoring after deployment

### 3. Rollback Plan

- **Migration Scripts**: Include rollback scripts for all indexes
- **Testing**: Test rollback procedures in staging
- **Documentation**: Document rollback procedures

## Conclusion

This comprehensive indexing strategy provides optimal query performance for the 3D Store application. The indexes are designed based on common query patterns, business requirements, and performance considerations. Regular monitoring and maintenance ensure continued optimal performance as the application scales.

For more information on specific indexes or query optimization, refer to the individual table documentation or contact the database administration team.
