"""
Transaction module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class TransactionCreateSchema(Schema):
    """Schema for creating a new transaction"""
    product_id = fields.UUID(
        required=True,
        error_messages={'required': 'Product ID is required'}
    )
    from_location_id = fields.UUID(
        allow_none=True
    )
    to_location_id = fields.UUID(
        allow_none=True
    )
    quantity = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01),
        error_messages={'required': 'Quantity is required'}
    )
    transaction_type = fields.Str(
        required=True,
        validate=validate.OneOf(['IN', 'OUT', 'TRANSFER', 'ADJUSTMENT']),
        error_messages={'required': 'Transaction type is required'}
    )
    reference_number = fields.Str(
        validate=validate.Length(max=255)
    )
    notes = fields.Str(
        validate=validate.Length(max=500)
    )
    transaction_date = fields.DateTime(
        load_default=lambda: datetime.now()
    )


class TransactionUpdateSchema(Schema):
    """Schema for updating a transaction"""
    quantity = fields.Decimal(
        places=2,
        validate=validate.Range(min=0.01)
    )
    reference_number = fields.Str(
        validate=validate.Length(max=255)
    )
    notes = fields.Str(
        validate=validate.Length(max=500)
    )
    status = fields.Str(
        validate=validate.OneOf(['PENDING', 'COMPLETED', 'CANCELLED'])
    )


class TransactionFilterSchema(Schema):
    """Schema for filtering transactions"""
    product_id = fields.UUID()
    location_id = fields.UUID()
    transaction_type = fields.Str(
        validate=validate.OneOf(['IN', 'OUT', 'TRANSFER', 'ADJUSTMENT'])
    )
    start_date = fields.Date()
    end_date = fields.Date()
    status = fields.Str(
        validate=validate.OneOf(['PENDING', 'COMPLETED', 'CANCELLED'])
    )
    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )

