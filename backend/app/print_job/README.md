# Print Job Module

The Print Job module manages 3D printing jobs, printer assignments, and print job tracking in the 3D Store application, providing comprehensive print job management capabilities.

## Overview

This module handles:
- Print job creation and management
- Printer assignment and scheduling
- Print job status tracking
- Print quality monitoring
- Print job optimization
- Real-time print job updates
- Print job analytics and reporting

## Module Structure

```
print_job/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
└── README.md           # This documentation
```

## Models

### PrintJob
Main print job entity with the following key attributes:
- **Basic Info**: `job_id`, `job_number`, `order_id`, `product_id`
- **Printer**: `printer_id`, `printer_name`, `printer_location`
- **File Info**: `model_file_url`, `gcode_file_url`, `file_size`
- **Settings**: `layer_height`, `infill_percentage`, `support_enabled`
- **Status**: `status`, `progress_percentage`, `estimated_duration`
- **Timestamps**: `created_at`, `started_at`, `completed_at`
- **Quality**: `quality_score`, `defects`, `reprint_required`
- **Metadata**: `created_at`, `updated_at`, `assigned_by`

### PrintJobStatus
Print job status tracking:
- **Status Info**: `job_id`, `status`, `status_message`
- **Progress**: `progress_percentage`, `current_layer`, `total_layers`
- **Timing**: `status_changed_at`, `estimated_completion`
- **User**: `changed_by`, `notes`
- **Metadata**: `created_at`

### PrintJobQuality
Print job quality assessment:
- **Quality Info**: `job_id`, `quality_score`, `defect_count`
- **Defects**: `defect_types`, `defect_locations`, `severity`
- **Measurements**: `dimensional_accuracy`, `surface_quality`
- **Assessment**: `assessed_by`, `assessment_notes`
- **Metadata**: `created_at`, `updated_at`

### PrinterAssignment
Printer assignment and scheduling:
- **Assignment Info**: `job_id`, `printer_id`, `assigned_at`
- **Scheduling**: `scheduled_start`, `estimated_duration`, `priority`
- **Status**: `assignment_status`, `assigned_by`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Print Job Management
- `GET /print-jobs` - List print jobs
- `GET /print-jobs/{id}` - Get print job details
- `POST /print-jobs` - Create print job
- `PUT /print-jobs/{id}` - Update print job
- `DELETE /print-jobs/{id}` - Cancel print job
- `POST /print-jobs/{id}/start` - Start print job
- `POST /print-jobs/{id}/pause` - Pause print job
- `POST /print-jobs/{id}/resume` - Resume print job
- `POST /print-jobs/{id}/complete` - Complete print job

### Print Job Status
- `GET /print-jobs/{id}/status` - Get print job status
- `PUT /print-jobs/{id}/status` - Update print job status
- `GET /print-jobs/{id}/progress` - Get print job progress
- `GET /print-jobs/status/active` - Get active print jobs
- `GET /print-jobs/status/queue` - Get print job queue

### Printer Assignment
- `GET /print-jobs/assignments` - List printer assignments
- `POST /print-jobs/{id}/assign` - Assign printer to job
- `PUT /print-jobs/{id}/reassign` - Reassign printer
- `GET /print-jobs/assignments/available` - Get available printers
- `POST /print-jobs/assignments/schedule` - Schedule print jobs

### Print Job Quality
- `GET /print-jobs/{id}/quality` - Get print job quality
- `POST /print-jobs/{id}/quality/assess` - Assess print quality
- `PUT /print-jobs/{id}/quality` - Update quality assessment
- `GET /print-jobs/quality/defects` - Get quality defects
- `POST /print-jobs/{id}/reprint` - Request reprint

### Print Job Analytics
- `GET /print-jobs/analytics/overview` - Get print job overview
- `GET /print-jobs/analytics/performance` - Get performance metrics
- `GET /print-jobs/analytics/quality` - Get quality metrics
- `GET /print-jobs/analytics/trends` - Get print job trends
- `GET /print-jobs/reports` - Generate print job reports

## Business Logic

### Print Job Creation
1. **Order Validation**: Validate order and product requirements
2. **File Processing**: Process 3D model file and generate G-code
3. **Printer Selection**: Select appropriate printer based on requirements
4. **Settings Optimization**: Optimize print settings for quality and speed
5. **Scheduling**: Schedule print job based on printer availability
6. **Quality Estimation**: Estimate print quality and duration
7. **Job Creation**: Create print job with all parameters

### Printer Assignment
1. **Printer Availability**: Check printer availability and capacity
2. **Requirement Matching**: Match job requirements with printer capabilities
3. **Load Balancing**: Balance load across available printers
4. **Priority Handling**: Handle job priorities and urgent orders
5. **Scheduling**: Schedule jobs to optimize printer utilization
6. **Conflict Resolution**: Resolve scheduling conflicts

### Print Job Monitoring
1. **Status Tracking**: Track print job status in real-time
2. **Progress Monitoring**: Monitor print progress and completion
3. **Quality Monitoring**: Monitor print quality during printing
4. **Error Detection**: Detect and handle print errors
5. **Alert Generation**: Generate alerts for issues
6. **Performance Tracking**: Track printer and job performance

### Quality Management
1. **Quality Assessment**: Assess print quality after completion
2. **Defect Detection**: Detect and categorize print defects
3. **Quality Scoring**: Score print quality based on criteria
4. **Reprint Decisions**: Decide on reprint requirements
5. **Quality Improvement**: Identify areas for quality improvement
6. **Quality Reporting**: Generate quality reports and analytics

## Validation Schemas

### PrintJobCreateSchema
```python
{
    "order_id": "uuid (required)",
    "product_id": "uuid (required)",
    "model_file_url": "string (required, valid URL)",
    "print_settings": {
        "layer_height": "float (required, min 0.1, max 0.5)",
        "infill_percentage": "integer (required, min 0, max 100)",
        "support_enabled": "boolean (required)",
        "print_speed": "float (optional, min 10, max 200)",
        "bed_temperature": "float (optional, min 0, max 150)",
        "nozzle_temperature": "float (optional, min 0, max 300)"
    },
    "material_id": "uuid (required)",
    "priority": "string (optional, enum: low|normal|high|urgent)",
    "estimated_duration": "integer (optional, minutes)",
    "notes": "string (optional, max 1000 chars)"
}
```

### PrintJobUpdateSchema
```python
{
    "status": "string (optional, enum: pending|assigned|printing|paused|completed|failed|cancelled)",
    "progress_percentage": "integer (optional, min 0, max 100)",
    "current_layer": "integer (optional, min 0)",
    "total_layers": "integer (optional, min 1)",
    "estimated_completion": "datetime (optional)",
    "notes": "string (optional, max 1000 chars)"
}
```

### PrinterAssignmentSchema
```python
{
    "job_id": "uuid (required)",
    "printer_id": "uuid (required)",
    "scheduled_start": "datetime (required)",
    "estimated_duration": "integer (required, minutes)",
    "priority": "string (required, enum: low|normal|high|urgent)",
    "assigned_by": "uuid (required)"
}
```

### QualityAssessmentSchema
```python
{
    "job_id": "uuid (required)",
    "quality_score": "integer (required, min 1, max 10)",
    "defect_count": "integer (required, min 0)",
    "defect_types": "array of strings (optional)",
    "defect_locations": "array of objects (optional)",
    "dimensional_accuracy": "float (optional, min 0, max 1)",
    "surface_quality": "float (optional, min 0, max 1)",
    "assessment_notes": "string (optional, max 1000 chars)",
    "reprint_required": "boolean (optional, default false)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When print job not found
- **BusinessLogicException**: For business rule violations
- **PrinterException**: For printer-related errors
- **QualityException**: For quality assessment errors

## Dependencies

- **Order Module**: For order information and processing
- **Product Module**: For product information and settings
- **Inventory Module**: For printer and material management
- **Media Module**: For 3D model file handling
- **Notification Module**: For print job notifications
- **Analytics Module**: For print job analytics

## Usage Examples

### Creating a Print Job
```python
from app.print_job.service import PrintJobService
from app.print_job.schemas import PrintJobCreateSchema

service = PrintJobService()
job_data = {
    "order_id": "order-uuid",
    "product_id": "product-uuid",
    "model_file_url": "https://storage.example.com/models/model.stl",
    "print_settings": {
        "layer_height": 0.2,
        "infill_percentage": 20,
        "support_enabled": True,
        "print_speed": 50.0,
        "bed_temperature": 60.0,
        "nozzle_temperature": 200.0
    },
    "material_id": "material-uuid",
    "priority": "normal",
    "estimated_duration": 180,
    "notes": "Custom phone case with logo"
}

print_job = service.create_print_job(job_data)
```

### Managing Print Job Status
```python
# Start print job
service.start_print_job(job_id)

# Update progress
service.update_print_job_progress(job_id, {
    "progress_percentage": 45,
    "current_layer": 90,
    "total_layers": 200,
    "estimated_completion": "2024-01-15T14:30:00Z"
})

# Pause print job
service.pause_print_job(job_id, "Maintenance required")

# Resume print job
service.resume_print_job(job_id)

# Complete print job
service.complete_print_job(job_id, {
    "quality_score": 8,
    "notes": "Print completed successfully"
})
```

### Printer Assignment
```python
# Assign printer to job
assignment_data = {
    "job_id": "job-uuid",
    "printer_id": "printer-uuid",
    "scheduled_start": "2024-01-15T10:00:00Z",
    "estimated_duration": 180,
    "priority": "normal",
    "assigned_by": "user-uuid"
}

assignment = service.assign_printer(assignment_data)

# Get available printers
available_printers = service.get_available_printers(
    start_time="2024-01-15T10:00:00Z",
    duration=180
)

# Reassign printer
service.reassign_printer(job_id, new_printer_id)
```

### Quality Assessment
```python
# Assess print quality
quality_data = {
    "job_id": "job-uuid",
    "quality_score": 8,
    "defect_count": 2,
    "defect_types": ["layer_shifting", "stringing"],
    "defect_locations": [
        {"x": 10, "y": 20, "z": 5, "severity": "minor"},
        {"x": 15, "y": 25, "z": 8, "severity": "minor"}
    ],
    "dimensional_accuracy": 0.95,
    "surface_quality": 0.88,
    "assessment_notes": "Good overall quality with minor defects",
    "reprint_required": False
}

quality_assessment = service.assess_print_quality(quality_data)

# Get quality metrics
quality_metrics = service.get_quality_metrics(start_date, end_date)
```

### Print Job Analytics
```python
# Get print job overview
overview = service.get_print_job_overview()

# Get performance metrics
performance = service.get_performance_metrics(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Get print job trends
trends = service.get_print_job_trends(period="monthly")

# Generate print job report
report = service.generate_print_job_report(
    report_type="performance",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Performance Considerations

- **Real-time Updates**: WebSocket for real-time status updates
- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Cache frequently accessed print job data
- **Background Processing**: Process print jobs in background
- **Load Balancing**: Distribute print jobs across printers

## Security

- **Access Control**: Role-based permissions for print job management
- **Data Validation**: Validate all print job inputs
- **Audit Logging**: Log all print job operations
- **File Security**: Secure 3D model file handling
- **Quality Control**: Ensure print quality standards

## Integration Points

- **Printer APIs**: Direct printer communication
- **File Storage**: 3D model and G-code storage
- **Notification Service**: Print job status notifications
- **Analytics Platform**: Print job analytics and reporting
- **Quality Control**: Automated quality assessment
- **Scheduling System**: Print job scheduling and optimization

## Future Enhancements

- **AI-Powered Optimization**: Machine learning print optimization
- **Predictive Maintenance**: Printer maintenance prediction
- **Real-time Monitoring**: Live print job monitoring dashboard
- **Automated Quality Control**: AI-powered quality assessment
- **Mobile App**: Mobile print job management
- **IoT Integration**: Smart printer integration and control
