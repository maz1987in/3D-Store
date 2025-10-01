from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from decimal import Decimal
import uuid

class OrderCreateSchema(Schema):
    items = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))
    shipping_address = fields.Dict(required=True)
    payment_method = fields.Str(validate=validate.OneOf(['credit_card', 'debit_card', 'paypal', 'bank_transfer']))
    notes = fields.Str(validate=validate.Length(max=1000))
    
    @validates_schema
    def validate_items(self, data, **kwargs):
        if not data.get('items'):
            raise ValidationError('At least one item is required', 'items')
        
        for item in data['items']:
            if 'type' not in item:
                raise ValidationError('Item type is required', 'items')
            if item['type'] not in ['print_job', 'ready_product']:
                raise ValidationError('Item type must be print_job or ready_product', 'items')
            if 'quantity' not in item or item['quantity'] < 1:
                raise ValidationError('Item quantity must be at least 1', 'items')

class OrderItemSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(['print_job', 'ready_product']))
    product_id = fields.UUID(required=True)
    print_job_id = fields.UUID(allow_none=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(validate=validate.Range(min=0))
    total_price = fields.Decimal(validate=validate.Range(min=0))

class OrderUpdateSchema(Schema):
    status = fields.Str(validate=validate.OneOf(['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']))
    notes = fields.Str(validate=validate.Length(max=1000))
    tracking_number = fields.Str(validate=validate.Length(max=100))

class PrintJobEstimateSchema(Schema):
    product_id = fields.UUID(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    material_id = fields.UUID(required=True)
    settings_id = fields.UUID(required=True)
    packaging_id = fields.UUID(allow_none=True)
    
    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        if not data.get('product_id'):
            raise ValidationError('Product ID is required', 'product_id')
        if not data.get('material_id'):
            raise ValidationError('Material ID is required', 'material_id')
        if not data.get('settings_id'):
            raise ValidationError('Settings ID is required', 'settings_id')
