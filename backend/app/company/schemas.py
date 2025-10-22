"""
Company module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate


class CompanyCreateSchema(Schema):
    """Schema for creating a company"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'Company name is required'}
    )
    registration_number = fields.Str(
        validate=validate.Length(max=100)
    )
    tax_number = fields.Str(
        validate=validate.Length(max=50)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    website = fields.Url(
        validate=validate.Length(max=255)
    )
    address = fields.Str(
        validate=validate.Length(max=500)
    )
    city = fields.Str(
        validate=validate.Length(max=100)
    )
    state = fields.Str(
        validate=validate.Length(max=100)
    )
    country = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'Country is required'}
    )
    postal_code = fields.Str(
        validate=validate.Length(max=20)
    )
    industry = fields.Str(
        validate=validate.Length(max=100)
    )
    founded_year = fields.Int(
        validate=validate.Range(min=1800, max=2100)
    )
    employee_count = fields.Int(
        validate=validate.Range(min=1)
    )
    is_active = fields.Bool(load_default=True)


class CompanyUpdateSchema(Schema):
    """Schema for updating a company"""
    name = fields.Str(
        validate=validate.Length(min=2, max=255)
    )
    registration_number = fields.Str(
        validate=validate.Length(max=100)
    )
    tax_number = fields.Str(
        validate=validate.Length(max=50)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    website = fields.Url(
        validate=validate.Length(max=255)
    )
    address = fields.Str(
        validate=validate.Length(max=500)
    )
    city = fields.Str(
        validate=validate.Length(max=100)
    )
    state = fields.Str(
        validate=validate.Length(max=100)
    )
    country = fields.Str(
        validate=validate.Length(min=2, max=100)
    )
    postal_code = fields.Str(
        validate=validate.Length(max=20)
    )
    industry = fields.Str(
        validate=validate.Length(max=100)
    )
    founded_year = fields.Int(
        validate=validate.Range(min=1800, max=2100)
    )
    employee_count = fields.Int(
        validate=validate.Range(min=1)
    )
    is_active = fields.Bool()


class CompanyFilterSchema(Schema):
    """Schema for filtering companies"""
    name = fields.Str(
        validate=validate.Length(min=1, max=255)
    )
    country = fields.Str(
        validate=validate.Length(max=100)
    )
    industry = fields.Str(
        validate=validate.Length(max=100)
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

