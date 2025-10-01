# Database-Agnostic Admin User Migration

This document explains the database-agnostic admin user migration that works with any SQLAlchemy-supported database.

## Migration File

**Location**: `backend/alembic/versions/add_admin_user.py`

## Key Features

### 🗄️ **Database Agnostic**
- Uses pure SQLAlchemy models instead of raw SQL
- Works with PostgreSQL, MySQL, SQLite, Oracle, and other SQLAlchemy-supported databases
- No database-specific SQL queries

### 🛡️ **Conflict Handling**
- Safe to run multiple times
- Uses `on_conflict_do_nothing()` for insert operations
- Gracefully handles existing data

### 🔄 **Rollback Support**
- Complete downgrade functionality
- Removes all created data in reverse order
- Safe rollback without data corruption

### 📊 **Data Types**
- UUID support for primary keys
- JSON support for user details
- Proper datetime handling with timezone support
- Boolean and string types

## Migration Structure

### Upgrade Function
1. **Define Tables**: Creates SQLAlchemy table definitions
2. **Create Admin Role**: Inserts admin role with conflict handling
3. **Create Admin User**: Inserts admin user with all required fields
4. **Create Association**: Links admin user to admin role

### Downgrade Function
1. **Remove Associations**: Deletes user-role relationships
2. **Remove User**: Deletes admin user
3. **Remove Role**: Deletes admin role

## Admin User Details

### Credentials
- **Username**: `admin`
- **Email**: `admin@store3d.com`
- **Phone**: `+1234567890`
- **Password**: `admin123`
- **Role**: `admin`

### User Information
- **Name**: System Administrator
- **User Type**: admin
- **Language**: ENGLISH
- **Status**: Active
- **Agreement**: Accepted

### User Details (JSON)
```json
{
  "first_name": "System",
  "last_name": "Administrator",
  "department": "IT",
  "position": "System Administrator",
  "created_by": "system"
}
```

## Database Support

### Supported Databases
- ✅ PostgreSQL
- ✅ MySQL
- ✅ SQLite
- ✅ Oracle
- ✅ Microsoft SQL Server
- ✅ Any SQLAlchemy-supported database

### Database-Specific Features
- **UUID**: Uses `postgresql.UUID` for PostgreSQL, adapts to other databases
- **JSON**: Uses `sa.JSON` for JSON columns
- **Conflict Handling**: Uses `on_conflict_do_nothing()` (PostgreSQL/MySQL)

## Usage

### Run Migration
```bash
cd backend
alembic upgrade head
```

### Rollback Migration
```bash
cd backend
alembic downgrade -1
```

### Check Migration Status
```bash
cd backend
alembic current
```

### View Migration History
```bash
cd backend
alembic history --verbose
```

## Testing

### Test Migration Syntax
```bash
cd backend
python scripts/test_admin_migration_db_agnostic.py
```

### Test Migration Execution
```bash
cd backend
python scripts/test_admin_migration.py
```

## Technical Details

### SQLAlchemy Features Used
- `sa.table()` - Table definitions
- `sa.column()` - Column definitions
- `insert().values()` - Insert operations
- `select().where()` - Select operations
- `delete().where()` - Delete operations
- `on_conflict_do_nothing()` - Conflict handling

### Data Types
- `postgresql.UUID(as_uuid=True)` - UUID primary keys
- `sa.String(length)` - String columns with length limits
- `sa.Boolean` - Boolean columns
- `sa.DateTime` - DateTime columns
- `sa.JSON` - JSON columns

### Error Handling
- Try-catch blocks for conflict handling
- Graceful fallback for existing data
- Proper transaction management

## Benefits

1. **Portability**: Works with any SQLAlchemy-supported database
2. **Maintainability**: Easy to read and modify
3. **Safety**: Conflict handling prevents data corruption
4. **Reliability**: Proper error handling and rollback support
5. **Standards**: Follows SQLAlchemy best practices

## Migration Dependencies

- **Previous Migration**: `add_performance_indexes`
- **Required Tables**: `roles`, `users`, `user_roles`
- **Required Columns**: All columns must exist in target tables

## Troubleshooting

### Common Issues
1. **Missing Tables**: Ensure previous migrations have run
2. **Column Mismatches**: Check table schema matches migration
3. **Permission Issues**: Ensure database user has INSERT/DELETE permissions
4. **UUID Support**: Some databases may need UUID extension

### Debug Mode
```bash
cd backend
alembic upgrade head --sql
```

This shows the SQL that would be executed without running it.
