"""
Customer module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re


class CustomerCreateSchema(Schema):
    """Schema for creating a customer"""
    user_id = fields.UUID(allow_none=True)
    
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={'required': 'Email is required'}
    )
    mobile = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=20),
        error_messages={'required': 'Mobile number is required'}
    )
    first_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    last_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    customer_type = fields.Str(
        validate=validate.OneOf(['individual', 'business']),
        load_default='individual'
    )
    company_name = fields.Str(
        validate=validate.Length(max=255)
    )
    tax_number = fields.Str(
        validate=validate.Length(max=50)
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'suspended']),
        load_default='active'
    )
    notes = fields.Str(
        validate=validate.Length(max=1000)
    )
    
    @validates('mobile')
    def validate_mobile(self, value):
        """Validate mobile number format"""
        cleaned = value.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if not cleaned.replace('+', '').isdigit():
            raise ValidationError('Mobile number must contain only digits')


class CustomerUpdateSchema(Schema):
    """Schema for updating a customer"""
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    mobile = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    first_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    last_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    customer_type = fields.Str(
        validate=validate.OneOf(['individual', 'business'])
    )
    company_name = fields.Str(
        validate=validate.Length(max=255)
    )
    tax_number = fields.Str(
        validate=validate.Length(max=50)
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'suspended'])
    )
    notes = fields.Str(
        validate=validate.Length(max=1000)
    )


class CustomerSearchSchema(Schema):
    """Schema for searching customers"""
    query = fields.Str(
        validate=validate.Length(min=1, max=255)
    )
    customer_type = fields.Str(
        validate=validate.OneOf(['individual', 'business'])
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'suspended'])
    )
    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )

