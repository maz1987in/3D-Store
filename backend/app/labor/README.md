# Labor Module

The Labor module manages labor tracking, time management, and workforce analytics in the 3D Store application, providing comprehensive labor management capabilities.

## Overview

This module handles:
- Labor time tracking and management
- Employee scheduling and assignments
- Labor cost calculation and analysis
- Productivity monitoring and metrics
- Labor reporting and analytics
- Workforce planning and optimization
- Labor compliance and regulations

## Module Structure

```
labor/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### LaborRecord
Main labor record entity with the following key attributes:
- **Basic Info**: `labor_id`, `employee_id`, `project_id`, `task_id`
- **Time Tracking**: `start_time`, `end_time`, `duration`, `break_time`
- **Work Details**: `work_type`, `description`, `location`, `equipment_used`
- **Status**: `status`, `is_approved`, `approved_by`, `approved_at`
- **Cost**: `hourly_rate`, `total_cost`, `overtime_hours`, `overtime_rate`
- **Metadata**: `created_at`, `updated_at`, `submitted_by`

### LaborProject
Labor project management:
- **Project Info**: `project_id`, `name`, `description`, `project_type`
- **Timeline**: `start_date`, `end_date`, `estimated_hours`, `actual_hours`
- **Budget**: `budget_hours`, `budget_cost`, `actual_cost`
- **Status**: `status`, `priority`, `is_active`
- **Team**: `team_members`, `project_manager`
- **Metadata**: `created_at`, `updated_at`

### LaborTask
Labor task breakdown:
- **Task Info**: `task_id`, `project_id`, `name`, `description`
- **Requirements**: `skill_requirements`, `equipment_required`, `location`
- **Time**: `estimated_hours`, `actual_hours`, `deadline`
- **Status**: `status`, `priority`, `assigned_to`
- **Dependencies**: `dependencies`, `predecessors`
- **Metadata**: `created_at`, `updated_at`

### LaborSchedule
Employee scheduling and assignments:
- **Schedule Info**: `schedule_id`, `employee_id`, `date`, `shift_type`
- **Time**: `start_time`, `end_time`, `break_duration`
- **Assignment**: `project_id`, `task_id`, `location`
- **Status**: `status`, `is_confirmed`, `notes`
- **Metadata**: `created_at`, `updated_at`

### LaborCost
Labor cost tracking and analysis:
- **Cost Info**: `cost_id`, `employee_id`, `project_id`, `period`
- **Hours**: `regular_hours`, `overtime_hours`, `total_hours`
- **Rates**: `regular_rate`, `overtime_rate`, `total_cost`
- **Breakdown**: `base_cost`, `overtime_cost`, `benefits_cost`
- **Metadata**: `created_at`, `updated_at`

### LaborProductivity
Productivity tracking and metrics:
- **Productivity Info**: `employee_id`, `period`, `project_id`
- **Metrics**: `hours_worked`, `tasks_completed`, `efficiency_score`
- **Quality**: `quality_score`, `error_rate`, `rework_hours`
- **Performance**: `performance_rating`, `productivity_index`
- **Metadata**: `calculated_at`, `created_at`

## API Endpoints

### Labor Management
- `GET /labor/records` - List labor records
- `GET /labor/records/{id}` - Get labor record details
- `POST /labor/records` - Create labor record
- `PUT /labor/records/{id}` - Update labor record
- `DELETE /labor/records/{id}` - Delete labor record
- `POST /labor/records/{id}/approve` - Approve labor record

### Labor Projects
- `GET /labor/projects` - List labor projects
- `GET /labor/projects/{id}` - Get project details
- `POST /labor/projects` - Create project
- `PUT /labor/projects/{id}` - Update project
- `DELETE /labor/projects/{id}` - Delete project
- `GET /labor/projects/{id}/tasks` - Get project tasks

### Labor Tasks
- `GET /labor/tasks` - List labor tasks
- `GET /labor/tasks/{id}` - Get task details
- `POST /labor/tasks` - Create task
- `PUT /labor/tasks/{id}` - Update task
- `DELETE /labor/tasks/{id}` - Delete task
- `POST /labor/tasks/{id}/assign` - Assign task to employee

### Labor Scheduling
- `GET /labor/schedules` - List labor schedules
- `GET /labor/schedules/{id}` - Get schedule details
- `POST /labor/schedules` - Create schedule
- `PUT /labor/schedules/{id}` - Update schedule
- `DELETE /labor/schedules/{id}` - Delete schedule
- `GET /labor/schedules/employee/{id}` - Get employee schedule

### Labor Cost Management
- `GET /labor/costs` - List labor costs
- `GET /labor/costs/{id}` - Get cost details
- `POST /labor/costs` - Create cost record
- `PUT /labor/costs/{id}` - Update cost record
- `GET /labor/costs/analysis` - Get cost analysis
- `GET /labor/costs/reports` - Generate cost reports

### Labor Analytics
- `GET /labor/analytics/overview` - Get labor overview
- `GET /labor/analytics/productivity` - Get productivity metrics
- `GET /labor/analytics/costs` - Get cost analytics
- `GET /labor/analytics/performance` - Get performance metrics
- `GET /labor/reports` - Generate labor reports

## Business Logic

### Labor Time Tracking
1. **Clock In/Out**: Track employee clock in and out times
2. **Break Management**: Track break times and durations
3. **Project Assignment**: Assign labor to specific projects
4. **Task Tracking**: Track time spent on specific tasks
5. **Overtime Calculation**: Calculate overtime hours and rates
6. **Approval Workflow**: Route labor records for approval

### Labor Project Management
1. **Project Creation**: Create labor projects with timelines
2. **Task Breakdown**: Break down projects into tasks
3. **Resource Allocation**: Allocate labor resources to projects
4. **Progress Tracking**: Track project progress and completion
5. **Budget Management**: Manage project labor budgets
6. **Team Management**: Manage project teams and assignments

### Labor Scheduling
1. **Shift Planning**: Plan employee shifts and schedules
2. **Assignment Management**: Assign employees to projects and tasks
3. **Availability Tracking**: Track employee availability
4. **Conflict Resolution**: Resolve scheduling conflicts
5. **Overtime Planning**: Plan overtime assignments
6. **Schedule Optimization**: Optimize schedules for efficiency

### Labor Cost Management
1. **Cost Calculation**: Calculate labor costs based on hours and rates
2. **Rate Management**: Manage employee hourly rates
3. **Overtime Calculation**: Calculate overtime costs
4. **Benefits Calculation**: Calculate benefits costs
5. **Cost Analysis**: Analyze labor costs and trends
6. **Budget Tracking**: Track labor costs against budgets

### Labor Productivity
1. **Productivity Measurement**: Measure employee productivity
2. **Efficiency Tracking**: Track work efficiency and quality
3. **Performance Analysis**: Analyze employee performance
4. **Benchmarking**: Compare productivity against benchmarks
5. **Improvement Planning**: Plan productivity improvements
6. **Recognition Programs**: Implement productivity recognition

## Validation Schemas

### LaborRecordCreateSchema
```python
{
    "employee_id": "uuid (required)",
    "project_id": "uuid (optional)",
    "task_id": "uuid (optional)",
    "start_time": "datetime (required)",
    "end_time": "datetime (required)",
    "work_type": "string (required, enum: regular|overtime|break|training)",
    "description": "string (required, max 500 chars)",
    "location": "string (optional, max 255 chars)",
    "equipment_used": "array of strings (optional)",
    "hourly_rate": "decimal (required, min 0)",
    "overtime_hours": "decimal (optional, min 0)",
    "overtime_rate": "decimal (optional, min 0)"
}
```

### LaborProjectCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "description": "string (required, max 1000 chars)",
    "project_type": "string (required, enum: production|maintenance|development|training)",
    "start_date": "date (required)",
    "end_date": "date (required)",
    "estimated_hours": "decimal (required, min 0)",
    "budget_hours": "decimal (required, min 0)",
    "budget_cost": "decimal (required, min 0)",
    "priority": "string (required, enum: low|medium|high|urgent)",
    "project_manager": "uuid (required)",
    "team_members": "array of uuids (optional)"
}
```

### LaborTaskCreateSchema
```python
{
    "project_id": "uuid (required)",
    "name": "string (required, max 255 chars)",
    "description": "string (required, max 1000 chars)",
    "skill_requirements": "array of strings (optional)",
    "equipment_required": "array of strings (optional)",
    "location": "string (optional, max 255 chars)",
    "estimated_hours": "decimal (required, min 0)",
    "deadline": "datetime (optional)",
    "priority": "string (required, enum: low|medium|high|urgent)",
    "assigned_to": "uuid (optional)",
    "dependencies": "array of uuids (optional)"
}
```

### LaborScheduleCreateSchema
```python
{
    "employee_id": "uuid (required)",
    "date": "date (required)",
    "shift_type": "string (required, enum: morning|afternoon|night|full_day)",
    "start_time": "time (required)",
    "end_time": "time (required)",
    "break_duration": "integer (optional, minutes)",
    "project_id": "uuid (optional)",
    "task_id": "uuid (optional)",
    "location": "string (optional, max 255 chars)",
    "notes": "string (optional, max 500 chars)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When labor record not found
- **BusinessLogicException**: For business rule violations
- **SchedulingException**: For scheduling conflicts
- **CostException**: For cost calculation errors

## Dependencies

- **User Module**: For employee management
- **Project Module**: For project management
- **Financial Module**: For cost calculation
- **Analytics Module**: For labor analytics
- **Notification Module**: For labor notifications
- **Time Tracking**: For time management

## Usage Examples

### Creating Labor Record
```python
from app.labor.service import LaborService
from app.labor.schemas import LaborRecordCreateSchema

service = LaborService()
labor_data = {
    "employee_id": "employee-uuid",
    "project_id": "project-uuid",
    "task_id": "task-uuid",
    "start_time": "2024-01-15T09:00:00Z",
    "end_time": "2024-01-15T17:00:00Z",
    "work_type": "regular",
    "description": "3D printing production work",
    "location": "Production Floor A",
    "equipment_used": ["Printer-001", "Scanner-002"],
    "hourly_rate": 15.00,
    "overtime_hours": 0.0,
    "overtime_rate": 22.50
}

labor_record = service.create_labor_record(labor_data)
```

### Managing Labor Projects
```python
# Create labor project
project_data = {
    "name": "Q1 Production Project",
    "description": "First quarter production targets",
    "project_type": "production",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "estimated_hours": 2000.0,
    "budget_hours": 2000.0,
    "budget_cost": 30000.00,
    "priority": "high",
    "project_manager": "manager-uuid",
    "team_members": ["employee-1", "employee-2", "employee-3"]
}

project = service.create_labor_project(project_data)

# Add task to project
task_data = {
    "project_id": "project-uuid",
    "name": "Setup Production Line",
    "description": "Setup and configure production equipment",
    "skill_requirements": ["3D Printing", "Equipment Setup"],
    "equipment_required": ["Printer-001", "Scanner-002"],
    "location": "Production Floor A",
    "estimated_hours": 40.0,
    "deadline": "2024-01-20T17:00:00Z",
    "priority": "high",
    "assigned_to": "employee-uuid"
}

task = service.create_labor_task(task_data)
```

### Labor Scheduling
```python
# Create labor schedule
schedule_data = {
    "employee_id": "employee-uuid",
    "date": "2024-01-15",
    "shift_type": "full_day",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "break_duration": 60,
    "project_id": "project-uuid",
    "task_id": "task-uuid",
    "location": "Production Floor A",
    "notes": "Regular production shift"
}

schedule = service.create_labor_schedule(schedule_data)

# Get employee schedule
employee_schedule = service.get_employee_schedule(employee_id, start_date, end_date)
```

### Labor Cost Management
```python
# Calculate labor cost
cost_data = {
    "employee_id": "employee-uuid",
    "project_id": "project-uuid",
    "period": "2024-01",
    "regular_hours": 160.0,
    "overtime_hours": 20.0,
    "regular_rate": 15.00,
    "overtime_rate": 22.50
}

cost = service.calculate_labor_cost(cost_data)

# Get cost analysis
cost_analysis = service.get_labor_cost_analysis(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### Labor Analytics
```python
# Get labor overview
overview = service.get_labor_overview()

# Get productivity metrics
productivity = service.get_productivity_metrics(
    employee_id="employee-uuid",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Get performance metrics
performance = service.get_performance_metrics(period="monthly")

# Generate labor report
report = service.generate_labor_report(
    report_type="productivity",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Cache frequently accessed labor data
- **Batch Processing**: Process labor records in batches
- **Real-time Updates**: Efficient real-time labor tracking
- **Analytics Processing**: Process analytics in background

## Security

- **Access Control**: Role-based permissions for labor management
- **Data Privacy**: Protect employee personal information
- **Audit Logging**: Log all labor operations
- **Time Validation**: Validate time entries and prevent fraud
- **Compliance**: Ensure labor law compliance

## Integration Points

- **Time Tracking Systems**: Integration with time tracking devices
- **Payroll Systems**: Integration with payroll processing
- **Project Management**: Integration with project management tools
- **Analytics Platforms**: Labor analytics and reporting
- **Notification Systems**: Labor notifications and alerts
- **HR Systems**: Integration with human resources systems

## Future Enhancements

- **AI-Powered Scheduling**: Machine learning scheduling optimization
- **Predictive Analytics**: Labor demand prediction
- **Mobile Time Tracking**: Mobile app for time tracking
- **IoT Integration**: Smart device integration for time tracking
- **Advanced Analytics**: Advanced labor analytics and insights
- **Automated Compliance**: Automated labor law compliance checking
