"""
Branch module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class BranchCreateSchema(Schema):
    """Schema for creating a branch"""
    company_id = fields.UUID(
        required=True,
        error_messages={'required': 'Company ID is required'}
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'Branch name is required'}
    )
    code = fields.Str(
        validate=validate.Length(min=2, max=50)
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
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    manager_name = fields.Str(
        validate=validate.Length(max=255)
    )
    is_active = fields.Bool(load_default=True)
    is_main_branch = fields.Bool(load_default=False)


class BranchUpdateSchema(Schema):
    """Schema for updating a branch"""
    name = fields.Str(
        validate=validate.Length(min=2, max=255)
    )
    code = fields.Str(
        validate=validate.Length(min=2, max=50)
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
    manager_name = fields.Str(
        validate=validate.Length(max=255)
    )
    is_active = fields.Bool()
    is_main_branch = fields.Bool()


class BranchFilterSchema(Schema):
    """Schema for filtering branches"""
    company_id = fields.UUID()
    city = fields.Str(
        validate=validate.Length(max=100)
    )
    country = fields.Str(
        validate=validate.Length(max=100)
    )
    is_active = fields.Bool()
    is_main_branch = fields.Bool()
    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )

