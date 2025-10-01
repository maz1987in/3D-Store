from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from decimal import Decimal
import uuid

class ProductCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(max=2000))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    category_id = fields.UUID(required=True)
    material_id = fields.UUID(allow_none=True)
    settings_id = fields.UUID(allow_none=True)
    packaging_id = fields.UUID(allow_none=True)
    enable = fields.Bool(missing=True)
    translations = fields.Dict(missing={})
    base_price = fields.Decimal(validate=validate.Range(min=0))
    material_usage_grams = fields.Decimal(validate=validate.Range(min=0))
    print_time_hours = fields.Decimal(validate=validate.Range(min=0))
    is_ready_made = fields.Bool(missing=False)
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    
    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        if not data.get('name') or not data['name'].strip():
            raise ValidationError('Product name is required and cannot be empty', 'name')
        
        if data.get('price') is not None and data['price'] < 0:
            raise ValidationError('Price must be non-negative', 'price')

class ProductUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(max=2000))
    price = fields.Decimal(validate=validate.Range(min=0))
    category_id = fields.UUID()
    material_id = fields.UUID(allow_none=True)
    settings_id = fields.UUID(allow_none=True)
    packaging_id = fields.UUID(allow_none=True)
    enable = fields.Bool()
    translations = fields.Dict()
    base_price = fields.Decimal(validate=validate.Range(min=0))
    material_usage_grams = fields.Decimal(validate=validate.Range(min=0))
    print_time_hours = fields.Decimal(validate=validate.Range(min=0))
    is_ready_made = fields.Bool()
    stock_quantity = fields.Int(validate=validate.Range(min=0))

class PrintMaterialSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(required=True, validate=validate.OneOf(['PLA', 'ABS', 'PETG', 'TPU', 'Wood-filled', 'Metal-filled']))
    color = fields.Str(validate=validate.Length(max=50))
    cost_per_gram = fields.Decimal(required=True, validate=validate.Range(min=0))
    density = fields.Decimal(required=True, validate=validate.Range(min=0))
    print_temperature = fields.Int(validate=validate.Range(min=150, max=300))
    bed_temperature = fields.Int(validate=validate.Range(min=20, max=120))
    is_active = fields.Bool(missing=True)

class PrintSettingsSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    quality = fields.Str(required=True, validate=validate.OneOf(['draft', 'standard', 'high', 'ultra_high']))
    layer_height = fields.Decimal(required=True, validate=validate.Range(min=0.05, max=0.5))
    infill_percentage = fields.Int(required=True, validate=validate.Range(min=0, max=100))
    print_speed = fields.Int(required=True, validate=validate.Range(min=10, max=200))
    support_enabled = fields.Bool(missing=False)
    raft_enabled = fields.Bool(missing=False)
    brim_enabled = fields.Bool(missing=False)
    estimated_time_multiplier = fields.Decimal(validate=validate.Range(min=0.1, max=5.0))
    is_active = fields.Bool(missing=True)

class ProductPackagingSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(required=True, validate=validate.OneOf(['keychain', 'wrapper', 'tag', 'box', 'custom']))
    cost = fields.Decimal(required=True, validate=validate.Range(min=0))
    description = fields.Str(validate=validate.Length(max=500))
    is_active = fields.Bool(missing=True)

class ProductShippingCitySchema(Schema):
    city_ids = fields.List(fields.UUID(), required=True, validate=validate.Length(min=1))
    
    @validates_schema
    def validate_city_ids(self, data, **kwargs):
        if not data.get('city_ids'):
            raise ValidationError('At least one city ID is required', 'city_ids')
