# Database Optimization Scripts

This directory contains scripts for database performance optimization, including index analysis, application, and monitoring.

## Scripts Overview

### 1. `analyze_indexes.py`
Analyzes existing database indexes and suggests optimizations.

**Features:**
- Identifies existing indexes
- Analyzes index usage statistics
- Suggests new indexes based on query patterns
- Identifies unused indexes
- Generates comprehensive reports

**Usage:**
```bash
# Run analysis
python scripts/analyze_indexes.py

# The script will generate:
# - Console output with summary
# - Detailed JSON report (index_analysis_YYYYMMDD_HHMMSS.json)
```

### 2. `apply_indexes.py`
Safely applies database indexes with monitoring and rollback capabilities.

**Features:**
- Creates indexes safely with error handling
- Estimates index sizes before creation
- Supports dry-run mode
- Provides rollback functionality
- Monitors creation progress

**Usage:**
```bash
# Dry run (show what would be done)
python scripts/apply_indexes.py --dry-run

# Apply indexes
python scripts/apply_indexes.py

# Rollback applied indexes
python scripts/apply_indexes.py --rollback
```

### 3. `monitor_performance.py`
Monitors database performance metrics in real-time.

**Features:**
- Query execution statistics
- Index usage monitoring
- Table statistics
- Database size tracking
- Connection monitoring
- System resource utilization
- Lock analysis
- Continuous monitoring mode

**Usage:**
```bash
# Single performance report
python scripts/monitor_performance.py

# Continuous monitoring (1 hour, every 60 seconds)
python scripts/monitor_performance.py --continuous --duration 3600 --interval 60

# Custom monitoring
python scripts/monitor_performance.py --continuous --duration 1800 --interval 30
```

## Prerequisites

### Required Python Packages
```bash
pip install sqlalchemy psutil
```

### Database Requirements
- PostgreSQL database
- `pg_stat_statements` extension enabled (for query statistics)
- Appropriate database permissions

### Enable pg_stat_statements
```sql
-- Connect to your database as superuser
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Add to postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
track_activity_query_size = 2048
pg_stat_statements.track = all
pg_stat_statements.max = 10000

-- Restart PostgreSQL
```

## Configuration

The scripts use the same database configuration as the main application. Ensure your `config.py` has the correct database settings:

```python
# Example configuration
DB_TYPE = 'postgresql'
DB_USERNAME = 'your_username'
DB_PASSWORD = 'your_password'
DB_DATABASE_NAME = 'store3d'
DB_HOST = 'localhost:5432'
```

## Index Strategy

### High Priority Indexes
These indexes provide the most performance benefit:

1. **User Authentication**
   - `idx_users_phone_email` - Fast user lookups
   - `idx_users_active_type` - Filter active users by type

2. **Product Catalog**
   - `idx_product_category_type` - Filter products by category and type
   - `idx_product_category_price` - Sort products by price within category

3. **Order Management**
   - `idx_order_customer_status` - Filter orders by customer and status
   - `idx_order_status_date` - Sort orders by status and date

4. **Inventory Management**
   - `idx_inventory_product_branch` - Track inventory by product and branch
   - `idx_inventory_quantity` - Low stock alerts

5. **Transaction Tracking**
   - `idx_transaction_product_type` - Filter transactions by product and type
   - `idx_transaction_type_date` - Sort transactions by type and date

### Medium Priority Indexes
These indexes improve specific query patterns:

1. **Search and Filtering**
   - `idx_product_price` - Price range filtering
   - `idx_customer_city` - Customer location filtering
   - `idx_order_total_amount` - Order value sorting

2. **Reporting**
   - `idx_transaction_date` - Transaction date filtering
   - `idx_payment_transaction_status` - Payment status filtering
   - `idx_invoice_due_date` - Invoice due date tracking

### Low Priority Indexes
These indexes provide minor performance improvements:

1. **Administrative**
   - `idx_users_language` - Language preference filtering
   - `idx_product_dynamic_pricing` - Dynamic pricing filtering
   - `idx_branch_city` - Branch location filtering

## Performance Monitoring

### Key Metrics to Monitor

1. **Query Performance**
   - Average execution time
   - Slow query identification
   - Query frequency

2. **Index Usage**
   - Index utilization rates
   - Unused index identification
   - Index efficiency

3. **Database Health**
   - Cache hit ratio
   - Connection count
   - Lock contention

4. **System Resources**
   - CPU usage
   - Memory utilization
   - Disk space

### Performance Thresholds

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Query execution time | < 100ms | 100-500ms | > 500ms |
| Cache hit ratio | > 95% | 90-95% | < 90% |
| Active connections | < 50 | 50-100 | > 100 |
| CPU usage | < 70% | 70-85% | > 85% |
| Memory usage | < 80% | 80-90% | > 90% |

## Best Practices

### Index Management

1. **Before Creating Indexes**
   - Run analysis script to identify needs
   - Test in development environment
   - Estimate storage requirements

2. **During Index Creation**
   - Use `CONCURRENTLY` for large tables
   - Monitor system resources
   - Apply during low-traffic periods

3. **After Creating Indexes**
   - Monitor query performance
   - Check index usage statistics
   - Remove unused indexes

### Performance Monitoring

1. **Regular Monitoring**
   - Run performance reports daily
   - Monitor slow queries weekly
   - Check index usage monthly

2. **Continuous Monitoring**
   - Use continuous mode during peak hours
   - Monitor during deployments
   - Track performance trends

3. **Alerting**
   - Set up alerts for critical metrics
   - Monitor error rates
   - Track resource utilization

## Troubleshooting

### Common Issues

1. **Index Creation Fails**
   - Check table locks
   - Verify column names
   - Ensure sufficient disk space

2. **Performance Degradation**
   - Check for missing indexes
   - Analyze slow queries
   - Monitor resource usage

3. **High Memory Usage**
   - Check connection count
   - Monitor query complexity
   - Review index usage

### Debugging Commands

```sql
-- Check index usage
SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan DESC;

-- Find slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Check table sizes
SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass))
FROM pg_tables WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;

-- Check locks
SELECT * FROM pg_locks WHERE NOT granted;
```

## Migration Integration

The index migration is integrated with Alembic:

```bash
# Apply the index migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Reporting

All scripts generate detailed JSON reports that can be used for:

- Performance analysis
- Capacity planning
- Optimization planning
- Historical tracking

## Security Considerations

- Scripts require database access
- Use read-only user for monitoring
- Secure report files
- Limit script execution permissions

## Support

For issues or questions:

1. Check the generated reports
2. Review database logs
3. Consult PostgreSQL documentation
4. Contact the database administration team

## Version History

- **v1.0** - Initial release with basic index analysis
- **v1.1** - Added performance monitoring
- **v1.2** - Added continuous monitoring mode
- **v1.3** - Enhanced reporting and error handling
