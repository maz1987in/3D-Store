import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey
from enum import Enum


class PrintJobStatusEnum(Enum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PREPARING = "preparing"
    PRINTING = "printing"
    POST_PROCESSING = "post_processing"
    QUALITY_CHECK = "quality_check"
    PACKAGING = "packaging"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PrintJob(Base):
    """Individual print job with 3D model files and specifications"""
    __tablename__ = 'print_jobs'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    order_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('order.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 3D Model file
    model_file = sql.Column(UploadedFileField, nullable=False)
    model_file_name = sql.Column(sql.String(255), nullable=False)
    model_file_size = sql.Column(sql.BigInteger, nullable=False)
    model_file_type = sql.Column(sql.String(50), nullable=False)  # STL, OBJ, 3MF
    
    # Print specifications
    material_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_materials.id'), nullable=False, index=True)
    print_settings_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_settings.id'), nullable=False)
    packaging_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product_packaging.id'), nullable=True)
    
    # Print parameters
    quantity = sql.Column(sql.Integer, nullable=False, default=1)
    scale_x = sql.Column(sql.Numeric(6, 3), default=1.0)  # Scale factor for X axis
    scale_y = sql.Column(sql.Numeric(6, 3), default=1.0)  # Scale factor for Y axis
    scale_z = sql.Column(sql.Numeric(6, 3), default=1.0)  # Scale factor for Z axis
    
    # Cost calculation
    estimated_print_time = sql.Column(sql.Integer, nullable=True)  # Estimated time in minutes
    estimated_material_usage = sql.Column(sql.Numeric(10, 4), nullable=True)  # Estimated material in grams
    estimated_cost = sql.Column(sql.Numeric(10, 4), nullable=True)  # Estimated total cost
    
    # Status and tracking
    status = sql.Column(sql.Enum(PrintJobStatusEnum), default=PrintJobStatusEnum.UPLOADED, index=True)
    progress_percentage = sql.Column(sql.Integer, default=0)
    assigned_printer_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('printers.id'), nullable=True, index=True)
    assigned_user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    uploaded_at = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    queued_at = sql.Column(sql.DateTime, nullable=True)
    started_at = sql.Column(sql.DateTime, nullable=True)
    completed_at = sql.Column(sql.DateTime, nullable=True)
    failed_at = sql.Column(sql.DateTime, nullable=True)
    
    # Error handling
    error_message = sql.Column(sql.Text, nullable=True)
    retry_count = sql.Column(sql.Integer, default=0)
    
    # Quality control
    quality_approved = sql.Column(sql.Boolean, default=False)
    quality_notes = sql.Column(sql.Text, nullable=True)
    quality_approved_by = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id'), nullable=True)
    quality_approved_at = sql.Column(sql.DateTime, nullable=True)
    
    # Additional data
    custom_instructions = sql.Column(sql.Text, nullable=True)
    priority = sql.Column(sql.Integer, default=0)  # Higher number = higher priority
    
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Order", back_populates="print_jobs")
    # user = relationship("User", foreign_keys=[user_id])  # Commented out until User model is created
    material = relationship("PrintMaterial")
    print_settings = relationship("PrintSettings")
    packaging = relationship("ProductPackaging")
    # assigned_printer = relationship("Printer")  # Commented out until Printer model is created
    # assigned_user = relationship("User", foreign_keys=[assigned_user_id])  # Commented out until User model is created
    # quality_approver = relationship("User", foreign_keys=[quality_approved_by])  # Commented out until User model is created
    print_logs = relationship("PrintJobLog", back_populates="print_job", cascade="all, delete-orphan")

    def json(self):
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'user_id': str(self.user_id),
            'model_file_name': self.model_file_name,
            'model_file_size': self.model_file_size,
            'model_file_type': self.model_file_type,
            'material_id': str(self.material_id),
            'print_settings_id': str(self.print_settings_id),
            'packaging_id': str(self.packaging_id) if self.packaging_id else None,
            'quantity': self.quantity,
            'scale_x': float(self.scale_x),
            'scale_y': float(self.scale_y),
            'scale_z': float(self.scale_z),
            'estimated_print_time': self.estimated_print_time,
            'estimated_material_usage': float(self.estimated_material_usage) if self.estimated_material_usage else None,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'status': self.status.value,
            'progress_percentage': self.progress_percentage,
            'assigned_printer_id': str(self.assigned_printer_id) if self.assigned_printer_id else None,
            'assigned_user_id': str(self.assigned_user_id) if self.assigned_user_id else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'queued_at': self.queued_at.isoformat() if self.queued_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'quality_approved': self.quality_approved,
            'quality_notes': self.quality_notes,
            'quality_approved_by': str(self.quality_approved_by) if self.quality_approved_by else None,
            'quality_approved_at': self.quality_approved_at.isoformat() if self.quality_approved_at else None,
            'custom_instructions': self.custom_instructions,
            'priority': self.priority,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None,
            'material': self.material.json() if self.material else None,
            'print_settings': self.print_settings.json() if self.print_settings else None,
            'packaging': self.packaging.json() if self.packaging else None
        }


class PrintJobLog(Base):
    """Log entries for print job status changes and events"""
    __tablename__ = 'print_job_logs'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    print_job_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_jobs.id', ondelete='CASCADE'), nullable=False)
    user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id'), nullable=True)
    
    # Log details
    status_from = sql.Column(sql.String(50), nullable=True)
    status_to = sql.Column(sql.String(50), nullable=False)
    message = sql.Column(sql.Text, nullable=False)
    log_type = sql.Column(sql.String(50), nullable=False)  # status_change, error, info, warning
    
    # Additional data
    log_metadata = sql.Column(sql.JSON, nullable=True)  # Additional structured data
    
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    print_job = relationship("PrintJob", back_populates="print_logs")
    # user = relationship("User")  # Commented out until User model is created

    def json(self):
        return {
            'id': str(self.id),
            'print_job_id': str(self.print_job_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'status_from': self.status_from,
            'status_to': self.status_to,
            'message': self.message,
            'log_type': self.log_type,
            'log_metadata': self.log_metadata,
            'create_date': self.create_date.isoformat() if self.create_date else None
        }


class Printer(Base):
    """3D printer specifications and status"""
    __tablename__ = 'printers'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = sql.Column(sql.String(100), nullable=False)
    model = sql.Column(sql.String(100), nullable=False)
    manufacturer = sql.Column(sql.String(100), nullable=False)
    
    # Printer specifications
    build_volume_x = sql.Column(sql.Numeric(6, 2), nullable=False)  # Build volume X in mm
    build_volume_y = sql.Column(sql.Numeric(6, 2), nullable=False)  # Build volume Y in mm
    build_volume_z = sql.Column(sql.Numeric(6, 2), nullable=False)  # Build volume Z in mm
    layer_resolution = sql.Column(sql.Numeric(4, 3), nullable=False)  # Minimum layer height in mm
    nozzle_diameter = sql.Column(sql.Numeric(4, 2), nullable=False)  # Nozzle diameter in mm
    
    # Status and location
    status = sql.Column(sql.String(20), default='available', index=True)  # available, busy, maintenance, offline
    location = sql.Column(sql.String(100), nullable=True)
    branch_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('branch.id'), nullable=True, index=True)
    
    # Maintenance
    last_maintenance = sql.Column(sql.DateTime, nullable=True)
    maintenance_interval_days = sql.Column(sql.Integer, default=30)
    total_print_hours = sql.Column(sql.Numeric(10, 2), default=0)
    
    # Cost tracking
    hourly_rate = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)  # Cost per hour
    electricity_cost_per_hour = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)
    
    is_active = sql.Column(sql.Boolean, default=True, index=True)
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    branch = relationship("Branch")
    # print_jobs = relationship("PrintJob", back_populates="assigned_printer")  # Commented out until relationship is fixed
    printer_materials = relationship("PrinterMaterial", back_populates="printer", cascade="all, delete-orphan")

    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'build_volume_x': float(self.build_volume_x),
            'build_volume_y': float(self.build_volume_y),
            'build_volume_z': float(self.build_volume_z),
            'layer_resolution': float(self.layer_resolution),
            'nozzle_diameter': float(self.nozzle_diameter),
            'status': self.status,
            'location': self.location,
            'branch_id': str(self.branch_id) if self.branch_id else None,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'maintenance_interval_days': self.maintenance_interval_days,
            'total_print_hours': float(self.total_print_hours),
            'hourly_rate': float(self.hourly_rate),
            'electricity_cost_per_hour': float(self.electricity_cost_per_hour),
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }


class PrinterMaterial(Base):
    """Materials compatible with each printer"""
    __tablename__ = 'printer_materials'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    printer_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('printers.id', ondelete='CASCADE'), nullable=False)
    material_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_materials.id', ondelete='CASCADE'), nullable=False)
    
    # Printer-specific settings for this material
    recommended_print_temperature = sql.Column(sql.Integer, nullable=True)
    recommended_bed_temperature = sql.Column(sql.Integer, nullable=True)
    recommended_print_speed = sql.Column(sql.Integer, nullable=True)
    notes = sql.Column(sql.Text, nullable=True)
    
    is_active = sql.Column(sql.Boolean, default=True)
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    printer = relationship("Printer", back_populates="printer_materials")
    material = relationship("PrintMaterial")

    # Unique constraint
    __table_args__ = (sql.UniqueConstraint('printer_id', 'material_id', name='unique_printer_material'),)

    def json(self):
        return {
            'id': str(self.id),
            'printer_id': str(self.printer_id),
            'material_id': str(self.material_id),
            'recommended_print_temperature': self.recommended_print_temperature,
            'recommended_bed_temperature': self.recommended_bed_temperature,
            'recommended_print_speed': self.recommended_print_speed,
            'notes': self.notes,
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'material': self.material.json() if self.material else None
        }
