"""
Staff module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date


class StaffCreateSchema(Schema):
    """Schema for creating a staff member"""
    user_id = fields.UUID(
        required=True,
        error_messages={'required': 'User ID is required'}
    )
    branch_id = fields.UUID()
    employee_number = fields.Str(
        validate=validate.Length(min=2, max=50)
    )
    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'First name is required'}
    )
    last_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Last name is required'}
    )
    position = fields.Str(
        validate=validate.Length(max=100)
    )
    department = fields.Str(
        validate=validate.Length(max=100)
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={'required': 'Email is required'}
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    hire_date = fields.Date()
    employment_type = fields.Str(
        validate=validate.OneOf(['full_time', 'part_time', 'contract', 'temporary']),
        load_default='full_time'
    )
    salary = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    hourly_rate = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'on_leave', 'terminated']),
        load_default='active'
    )
    is_active = fields.Bool(load_default=True)
    
    @validates('hire_date')
    def validate_hire_date(self, value):
        """Validate hire date is not in the future"""
        if value and value > date.today():
            raise ValidationError('Hire date cannot be in the future')


class StaffUpdateSchema(Schema):
    """Schema for updating a staff member"""
    branch_id = fields.UUID()
    employee_number = fields.Str(
        validate=validate.Length(min=2, max=50)
    )
    first_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    last_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    position = fields.Str(
        validate=validate.Length(max=100)
    )
    department = fields.Str(
        validate=validate.Length(max=100)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    hire_date = fields.Date()
    employment_type = fields.Str(
        validate=validate.OneOf(['full_time', 'part_time', 'contract', 'temporary'])
    )
    salary = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    hourly_rate = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'on_leave', 'terminated'])
    )
    is_active = fields.Bool()


class StaffFilterSchema(Schema):
    """Schema for filtering staff"""
    branch_id = fields.UUID()
    department = fields.Str(
        validate=validate.Length(max=100)
    )
    position = fields.Str(
        validate=validate.Length(max=100)
    )
    employment_type = fields.Str(
        validate=validate.OneOf(['full_time', 'part_time', 'contract', 'temporary'])
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'on_leave', 'terminated'])
    )
    is_active = fields.Bool()
    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )

