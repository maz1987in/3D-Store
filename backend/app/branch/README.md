# Branch Module

The Branch module manages printing facilities, branch locations, and operational management in the 3D Store application, providing comprehensive branch and facility management capabilities.

## Overview

This module handles:
- Branch location management
- Facility capacity and resource tracking
- Staff assignment and management
- Equipment and printer management
- Branch performance monitoring
- Operational scheduling and planning
- Multi-location support

## Module Structure

```
branch/
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

### Branch
Main branch entity with the following key attributes:
- **Basic Info**: `branch_id`, `branch_name`, `branch_code`, `branch_type`
- **Location**: `address`, `city`, `state`, `country`, `postal_code`
- **Contact**: `phone`, `email`, `manager_id`, `contact_person`
- **Operations**: `is_active`, `operating_hours`, `timezone`
- **Capacity**: `max_printers`, `max_staff`, `storage_capacity`
- **Metadata**: `created_at`, `updated_at`, `last_activity`

### BranchStaff
Staff assignment to branches:
- **Assignment Info**: `branch_id`, `staff_id`, `role`, `is_manager`
- **Schedule**: `work_schedule`, `shift_pattern`, `availability`
- **Performance**: `performance_rating`, `productivity_score`
- **Status**: `is_active`, `start_date`, `end_date`
- **Metadata**: `created_at`, `updated_at`

### BranchEquipment
Equipment and printer management:
- **Equipment Info**: `branch_id`, `equipment_id`, `equipment_type`
- **Printer Details**: `printer_model`, `printer_status`, `last_maintenance`
- **Specifications**: `max_build_volume`, `supported_materials`, `resolution`
- **Performance**: `print_speed`, `success_rate`, `utilization_rate`
- **Status**: `is_operational`, `is_available`, `maintenance_due`
- **Metadata**: `created_at`, `updated_at`

### BranchCapacity
Branch capacity and resource tracking:
- **Capacity Info**: `branch_id`, `date`, `max_capacity`, `current_load`
- **Resources**: `available_printers`, `available_staff`, `available_materials`
- **Utilization**: `printer_utilization`, `staff_utilization`, `storage_utilization`
- **Forecasting**: `predicted_load`, `capacity_alerts`
- **Metadata**: `created_at`, `updated_at`

### BranchSchedule
Branch operational scheduling:
- **Schedule Info**: `branch_id`, `schedule_date`, `shift_type`
- **Staffing**: `staff_count`, `manager_id`, `shift_leader`
- **Operations**: `operating_hours`, `break_times`, `maintenance_windows`
- **Capacity**: `max_orders`, `max_print_jobs`, `priority_orders`
- **Status**: `is_active`, `is_holiday`, `special_instructions`
- **Metadata**: `created_at`, `updated_at`

### BranchPerformance
Branch performance metrics:
- **Performance Info**: `branch_id`, `period`, `total_orders`, `completed_orders`
- **Metrics**: `order_fulfillment_rate`, `average_processing_time`
- **Quality**: `quality_score`, `defect_rate`, `customer_satisfaction`
- **Efficiency**: `throughput`, `utilization_rate`, `cost_per_order`
- **Ranking**: `performance_rank`, `efficiency_score`
- **Metadata**: `created_at`, `updated_at`

## Repository Layer

The `BranchRepository` class provides data access operations for the Branch module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Branch]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(branch_id)` - Get branch by ID
- `create(branch_data)` - Create new branch
- `update(branch_id, branch_data)` - Update existing branch
- `delete(branch_id)` - Delete branch
- `get_all(limit, offset)` - Get all branches with pagination

#### Advanced Query Methods
- `get_branch_by_location(location)` - Branch by location
- `get_branch_by_manager(manager)` - Branch by manager
- `search_branches(search_term)` - Search branches

#### Statistics and Analytics
- `get_branch_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.branch.repository import BranchRepository

# Initialize repository
branch_repo = BranchRepository()

# Get branch by ID
branch = branch_repo.get_by_id("branch-uuid")

# Get branch by location
branch = branch_repo.get_branch_by_location("Downtown Location")

# Search branches
search_results = branch_repo.search_branches("downtown")

# Get branch statistics
stats = branch_repo.get_branch_statistics()
```

## API Endpoints

### Branch Management
- `GET /branches` - List all branches
- `GET /branches/{id}` - Get branch details
- `POST /branches` - Create new branch
- `PUT /branches/{id}` - Update branch
- `DELETE /branches/{id}` - Deactivate branch
- `GET /branches/{id}/status` - Get branch status

### Branch Staff
- `GET /branches/{id}/staff` - List branch staff
- `POST /branches/{id}/staff` - Assign staff to branch
- `PUT /branches/{id}/staff/{staff_id}` - Update staff assignment
- `DELETE /branches/{id}/staff/{staff_id}` - Remove staff from branch
- `GET /branches/{id}/staff/schedule` - Get staff schedule

### Branch Equipment
- `GET /branches/{id}/equipment` - List branch equipment
- `POST /branches/{id}/equipment` - Add equipment to branch
- `PUT /branches/{id}/equipment/{equipment_id}` - Update equipment
- `DELETE /branches/{id}/equipment/{equipment_id}` - Remove equipment
- `GET /branches/{id}/equipment/status` - Get equipment status

### Branch Capacity
- `GET /branches/{id}/capacity` - Get branch capacity
- `PUT /branches/{id}/capacity` - Update branch capacity
- `GET /branches/{id}/capacity/forecast` - Get capacity forecast
- `GET /branches/{id}/capacity/alerts` - Get capacity alerts

### Branch Scheduling
- `GET /branches/{id}/schedule` - Get branch schedule
- `POST /branches/{id}/schedule` - Create schedule
- `PUT /branches/{id}/schedule/{schedule_id}` - Update schedule
- `DELETE /branches/{id}/schedule/{schedule_id}` - Delete schedule
- `GET /branches/{id}/schedule/availability` - Get availability

### Branch Performance
- `GET /branches/{id}/performance` - Get branch performance
- `GET /branches/{id}/performance/trends` - Get performance trends
- `GET /branches/performance/ranking` - Get branch rankings
- `GET /branches/performance/comparison` - Compare branch performance

### Branch Operations
- `POST /branches/{id}/orders/assign` - Assign order to branch
- `GET /branches/{id}/orders/queue` - Get order queue
- `POST /branches/{id}/maintenance` - Schedule maintenance
- `GET /branches/{id}/alerts` - Get branch alerts

## Business Logic

### Branch Creation
1. **Location Setup**: Set up branch location and address
2. **Capacity Planning**: Define branch capacity and resources
3. **Staff Assignment**: Assign initial staff and manager
4. **Equipment Setup**: Install and configure equipment
5. **Schedule Creation**: Create operational schedule
6. **System Integration**: Integrate with order and inventory systems

### Staff Management
1. **Staff Assignment**: Assign staff to branches
2. **Role Definition**: Define staff roles and responsibilities
3. **Schedule Management**: Manage staff schedules and shifts
4. **Performance Tracking**: Track staff performance
5. **Training Management**: Manage staff training and certification
6. **Workload Balancing**: Balance workload across staff

### Equipment Management
1. **Equipment Installation**: Install and configure equipment
2. **Maintenance Scheduling**: Schedule regular maintenance
3. **Performance Monitoring**: Monitor equipment performance
4. **Capacity Tracking**: Track equipment utilization
5. **Upgrade Planning**: Plan equipment upgrades
6. **Troubleshooting**: Handle equipment issues

### Capacity Management
1. **Capacity Planning**: Plan branch capacity
2. **Resource Allocation**: Allocate resources efficiently
3. **Load Balancing**: Balance load across branches
4. **Forecasting**: Forecast future capacity needs
5. **Alert Management**: Manage capacity alerts
6. **Optimization**: Optimize capacity utilization

### Performance Monitoring
1. **Metrics Collection**: Collect performance metrics
2. **Analysis**: Analyze performance data
3. **Reporting**: Generate performance reports
4. **Benchmarking**: Compare performance across branches
5. **Improvement Planning**: Plan performance improvements
6. **Best Practices**: Share best practices

## Validation Schemas

### BranchCreateSchema
```python
{
    "branch_name": "string (required, max 255 chars)",
    "branch_code": "string (required, max 50 chars, unique)",
    "branch_type": "string (required, enum: main|satellite|popup)",
    "address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "phone": "string (required, valid phone number)",
    "email": "string (required, valid email)",
    "manager_id": "uuid (required)",
    "operating_hours": {
        "monday": {"open": "09:00", "close": "18:00"},
        "tuesday": {"open": "09:00", "close": "18:00"},
        "wednesday": {"open": "09:00", "close": "18:00"},
        "thursday": {"open": "09:00", "close": "18:00"},
        "friday": {"open": "09:00", "close": "18:00"},
        "saturday": {"open": "10:00", "close": "16:00"},
        "sunday": {"open": "closed", "close": "closed"}
    },
    "timezone": "string (required, valid timezone)",
    "max_printers": "integer (required, min 1)",
    "max_staff": "integer (required, min 1)",
    "storage_capacity": "decimal (required, min 0)"
}
```

### BranchUpdateSchema
```python
{
    "branch_name": "string (optional, max 255 chars)",
    "branch_type": "string (optional, enum: main|satellite|popup)",
    "phone": "string (optional, valid phone number)",
    "email": "string (optional, valid email)",
    "manager_id": "uuid (optional)",
    "operating_hours": "object (optional)",
    "timezone": "string (optional, valid timezone)",
    "max_printers": "integer (optional, min 1)",
    "max_staff": "integer (optional, min 1)",
    "storage_capacity": "decimal (optional, min 0)",
    "is_active": "boolean (optional)"
}
```

### BranchStaffSchema
```python
{
    "branch_id": "uuid (required)",
    "staff_id": "uuid (required)",
    "role": "string (required, enum: manager|supervisor|operator|technician)",
    "is_manager": "boolean (optional, default false)",
    "work_schedule": {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": {"start": "10:00", "end": "16:00"},
        "sunday": {"start": "closed", "end": "closed"}
    },
    "shift_pattern": "string (optional, enum: day|night|rotating)",
    "start_date": "date (required)"
}
```

### BranchEquipmentSchema
```python
{
    "branch_id": "uuid (required)",
    "equipment_id": "uuid (required)",
    "equipment_type": "string (required, enum: printer|scanner|post_processor)",
    "printer_model": "string (required, max 255 chars)",
    "printer_status": "string (required, enum: operational|maintenance|offline)",
    "max_build_volume": {
        "x": "float (required, min 0)",
        "y": "float (required, min 0)",
        "z": "float (required, min 0)"
    },
    "supported_materials": "array of strings (required)",
    "resolution": "float (required, min 0)",
    "print_speed": "float (required, min 0)",
    "last_maintenance": "date (optional)",
    "maintenance_due": "date (optional)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When branch not found
- **BusinessLogicException**: For business rule violations
- **CapacityException**: For capacity-related errors
- **EquipmentException**: For equipment-related errors

## Dependencies

- **User Module**: For staff management
- **Order Module**: For order assignment
- **Inventory Module**: For equipment and materials
- **Notification Module**: For branch alerts
- **Analytics Module**: For performance tracking
- **Scheduling Module**: For operational scheduling

## Usage Examples

### Creating a Branch
```python
from app.branch.service import BranchService
from app.branch.schemas import BranchCreateSchema

service = BranchService()
branch_data = {
    "branch_name": "Muscat Main Branch",
    "branch_code": "MCT001",
    "branch_type": "main",
    "address": {
        "street": "123 Business Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "phone": "+96812345678",
    "email": "muscat@3dstore.com",
    "manager_id": "manager-uuid",
    "operating_hours": {
        "monday": {"open": "09:00", "close": "18:00"},
        "tuesday": {"open": "09:00", "close": "18:00"},
        "wednesday": {"open": "09:00", "close": "18:00"},
        "thursday": {"open": "09:00", "close": "18:00"},
        "friday": {"open": "09:00", "close": "18:00"},
        "saturday": {"open": "10:00", "close": "16:00"},
        "sunday": {"open": "closed", "close": "closed"}
    },
    "timezone": "Asia/Muscat",
    "max_printers": 10,
    "max_staff": 15,
    "storage_capacity": 1000.0
}

branch = service.create_branch(branch_data)
```

### Managing Branch Staff
```python
# Assign staff to branch
staff_data = {
    "branch_id": "branch-uuid",
    "staff_id": "staff-uuid",
    "role": "operator",
    "is_manager": False,
    "work_schedule": {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": {"start": "10:00", "end": "16:00"},
        "sunday": {"start": "closed", "end": "closed"}
    },
    "shift_pattern": "day",
    "start_date": "2024-01-15"
}

staff_assignment = service.assign_staff_to_branch(staff_data)

# Get branch staff
staff = service.get_branch_staff(branch_id)

# Update staff assignment
service.update_staff_assignment(branch_id, staff_id, {
    "role": "supervisor",
    "is_manager": True
})
```

### Managing Branch Equipment
```python
# Add equipment to branch
equipment_data = {
    "branch_id": "branch-uuid",
    "equipment_id": "equipment-uuid",
    "equipment_type": "printer",
    "printer_model": "Ultimaker S5",
    "printer_status": "operational",
    "max_build_volume": {
        "x": 330.0,
        "y": 240.0,
        "z": 300.0
    },
    "supported_materials": ["PLA", "ABS", "PETG"],
    "resolution": 0.2,
    "print_speed": 50.0,
    "last_maintenance": "2024-01-01",
    "maintenance_due": "2024-02-01"
}

equipment = service.add_equipment_to_branch(equipment_data)

# Get branch equipment
equipment_list = service.get_branch_equipment(branch_id)

# Update equipment status
service.update_equipment_status(branch_id, equipment_id, "maintenance")
```

### Branch Capacity Management
```python
# Get branch capacity
capacity = service.get_branch_capacity(branch_id)

# Update capacity
service.update_branch_capacity(branch_id, {
    "max_capacity": 100,
    "current_load": 75,
    "available_printers": 8,
    "available_staff": 12
})

# Get capacity forecast
forecast = service.get_capacity_forecast(branch_id, "2024-02-01", "2024-02-29")

# Get capacity alerts
alerts = service.get_capacity_alerts(branch_id)
```

### Branch Performance
```python
# Get branch performance
performance = service.get_branch_performance(branch_id, "2024-01-01", "2024-01-31")

# Get performance trends
trends = service.get_performance_trends(branch_id, period="monthly")

# Get branch rankings
rankings = service.get_branch_rankings()

# Compare branch performance
comparison = service.compare_branch_performance(branch_ids)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frequently accessed branch data cached
- **Load Balancing**: Efficient load distribution
- **Real-time Updates**: WebSocket for real-time updates
- **Batch Processing**: Efficient batch operations

## Security

- **Access Control**: Role-based permissions for branch management
- **Data Privacy**: Protect sensitive branch information
- **Audit Logging**: All branch operations logged
- **Equipment Security**: Secure equipment management
- **Staff Privacy**: Protect staff information

## Integration Points

- **Order Management**: Order assignment and processing
- **Inventory Management**: Equipment and material tracking
- **Staff Management**: Employee assignment and scheduling
- **Maintenance Systems**: Equipment maintenance tracking
- **Analytics Platforms**: Performance monitoring and reporting
- **Communication Systems**: Branch notifications and alerts

## Future Enhancements

- **IoT Integration**: Smart equipment monitoring
- **AI-Powered Scheduling**: Intelligent resource allocation
- **Predictive Maintenance**: Equipment failure prediction
- **Mobile Management**: Mobile branch management app
- **Real-time Monitoring**: Live branch operations dashboard
- **Automated Optimization**: Self-optimizing branch operations
