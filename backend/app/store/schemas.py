"""
Store module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate


class StoreCreateSchema(Schema):
    """Schema for creating a store"""
    branch_id = fields.UUID(
        required=True,
        error_messages={'required': 'Branch ID is required'}
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'Store name is required'}
    )
    code = fields.Str(
        validate=validate.Length(min=2, max=50)
    )
    store_type = fields.Str(
        validate=validate.OneOf(['retail', 'warehouse', 'showroom', 'online']),
        load_default='retail'
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
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    manager_id = fields.UUID()
    opening_hours = fields.Dict()
    is_active = fields.Bool(load_default=True)


class StoreUpdateSchema(Schema):
    """Schema for updating a store"""
    name = fields.Str(
        validate=validate.Length(min=2, max=255)
    )
    code = fields.Str(
        validate=validate.Length(min=2, max=50)
    )
    store_type = fields.Str(
        validate=validate.OneOf(['retail', 'warehouse', 'showroom', 'online'])
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
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    manager_id = fields.UUID()
    opening_hours = fields.Dict()
    is_active = fields.Bool()


class StoreFilterSchema(Schema):
    """Schema for filtering stores"""
    branch_id = fields.UUID()
    store_type = fields.Str(
        validate=validate.OneOf(['retail', 'warehouse', 'showroom', 'online'])
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

