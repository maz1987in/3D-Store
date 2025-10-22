"""
Address module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate


class AddressCreateSchema(Schema):
    """Schema for creating an address"""
    user_id = fields.UUID(
        required=True,
        error_messages={'required': 'User ID is required'}
    )
    address_type = fields.Str(
        validate=validate.OneOf(['shipping', 'billing', 'both']),
        load_default='shipping'
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
    company = fields.Str(
        validate=validate.Length(max=255)
    )
    address_line1 = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=255),
        error_messages={'required': 'Address line 1 is required'}
    )
    address_line2 = fields.Str(
        validate=validate.Length(max=255)
    )
    city = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'City is required'}
    )
    state = fields.Str(
        validate=validate.Length(max=100)
    )
    postal_code = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=20),
        error_messages={'required': 'Postal code is required'}
    )
    country = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'Country is required'}
    )
    phone = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=20),
        error_messages={'required': 'Phone number is required'}
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    is_default = fields.Bool(load_default=False)
    notes = fields.Str(
        validate=validate.Length(max=500)
    )


class AddressUpdateSchema(Schema):
    """Schema for updating an address"""
    address_type = fields.Str(
        validate=validate.OneOf(['shipping', 'billing', 'both'])
    )
    first_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    last_name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )
    company = fields.Str(
        validate=validate.Length(max=255)
    )
    address_line1 = fields.Str(
        validate=validate.Length(min=5, max=255)
    )
    address_line2 = fields.Str(
        validate=validate.Length(max=255)
    )
    city = fields.Str(
        validate=validate.Length(min=2, max=100)
    )
    state = fields.Str(
        validate=validate.Length(max=100)
    )
    postal_code = fields.Str(
        validate=validate.Length(min=3, max=20)
    )
    country = fields.Str(
        validate=validate.Length(min=2, max=100)
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    is_default = fields.Bool()
    notes = fields.Str(
        validate=validate.Length(max=500)
    )


class AddressFilterSchema(Schema):
    """Schema for filtering addresses"""
    user_id = fields.UUID()
    address_type = fields.Str(
        validate=validate.OneOf(['shipping', 'billing', 'both'])
    )
    city = fields.Str(
        validate=validate.Length(max=100)
    )
    country = fields.Str(
        validate=validate.Length(max=100)
    )
    is_default = fields.Bool()

