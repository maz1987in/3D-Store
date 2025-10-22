"""
Supplier module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class SupplierCreateSchema(Schema):
    """Schema for creating a supplier"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'Supplier name is required'}
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    contact_person = fields.Str(
        validate=validate.Length(max=255)
    )
    address = fields.Str(
        validate=validate.Length(max=500)
    )
    city = fields.Str(
        validate=validate.Length(max=100)
    )
    country = fields.Str(
        validate=validate.Length(max=100)
    )
    tax_number = fields.Str(
        validate=validate.Length(max=50)
    )
    payment_terms = fields.Str(
        validate=validate.Length(max=255)
    )
    notes = fields.Str(
        validate=validate.Length(max=1000)
    )
    is_active = fields.Bool(load_default=True)


class SupplierUpdateSchema(Schema):
    """Schema for updating a supplier"""
    name = fields.Str(
        validate=validate.Length(min=2, max=255)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    contact_person = fields.Str(
        validate=validate.Length(max=255)
    )
    address = fields.Str(
        validate=validate.Length(max=500)
    )
    city = fields.Str(
        validate=validate.Length(max=100)
    )
    country = fields.Str(
        validate=validate.Length(max=100)
    )
    tax_number = fields.Str(
        validate=validate.Length(max=50)
    )
    payment_terms = fields.Str(
        validate=validate.Length(max=255)
    )
    notes = fields.Str(
        validate=validate.Length(max=1000)
    )
    is_active = fields.Bool()


class SupplierFilterSchema(Schema):
    """Schema for filtering suppliers"""
    name = fields.Str(
        validate=validate.Length(min=1, max=255)
    )
    city = fields.Str(
        validate=validate.Length(max=100)
    )
    country = fields.Str(
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

