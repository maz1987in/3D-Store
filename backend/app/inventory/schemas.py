"""
Inventory module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema


class InventoryCreateSchema(Schema):
    """Schema for creating inventory record"""
    product_id = fields.UUID(
        required=True,
        error_messages={'required': 'Product ID is required'}
    )
    branch_id = fields.UUID(
        required=True,
        error_messages={'required': 'Branch ID is required'}
    )
    quantity = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0),
        error_messages={'required': 'Quantity is required'}
    )
    quantity_alert = fields.Decimal(
        places=2,
        validate=validate.Range(min=0),
        load_default=0
    )
    location = fields.Str(
        validate=validate.Length(max=255)
    )
    notes = fields.Str(
        validate=validate.Length(max=500)
    )


class InventoryUpdateSchema(Schema):
    """Schema for updating inventory record"""
    quantity = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    quantity_alert = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    location = fields.Str(
        validate=validate.Length(max=255)
    )
    notes = fields.Str(
        validate=validate.Length(max=500)
    )
    is_active = fields.Bool()


class InventoryAdjustmentSchema(Schema):
    """Schema for inventory adjustment"""
    adjustment_type = fields.Str(
        required=True,
        validate=validate.OneOf(['ADD', 'SUBTRACT', 'SET']),
        error_messages={'required': 'Adjustment type is required'}
    )
    quantity = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01),
        error_messages={'required': 'Quantity is required'}
    )
    reason = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=500),
        error_messages={'required': 'Reason is required'}
    )
    reference_number = fields.Str(
        validate=validate.Length(max=255)
    )
    
    @validates_schema
    def validate_adjustment(self, data, **kwargs):
        """Validate adjustment values"""
        if data.get('adjustment_type') == 'SET' and data.get('quantity', 0) < 0:
            raise ValidationError(
                'SET adjustment cannot have negative quantity',
                field_name='quantity'
            )


class InventoryTransferSchema(Schema):
    """Schema for inventory transfer between locations"""
    from_branch_id = fields.UUID(
        required=True,
        error_messages={'required': 'Source branch ID is required'}
    )
    to_branch_id = fields.UUID(
        required=True,
        error_messages={'required': 'Destination branch ID is required'}
    )
    product_id = fields.UUID(
        required=True,
        error_messages={'required': 'Product ID is required'}
    )
    quantity = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01),
        error_messages={'required': 'Quantity is required'}
    )
    notes = fields.Str(
        validate=validate.Length(max=500)
    )
    transfer_date = fields.DateTime()
    
    @validates_schema
    def validate_transfer(self, data, **kwargs):
        """Validate transfer between different branches"""
        if data.get('from_branch_id') == data.get('to_branch_id'):
            raise ValidationError(
                'Cannot transfer to the same branch',
                field_name='to_branch_id'
            )

