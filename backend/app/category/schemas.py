from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from marshmallow_enum import EnumField
import uuid

class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    parent_id = fields.UUID(allow_none=True)
    enable = fields.Bool(load_default=True)
    translations = fields.Dict(load_default={})
    icon = fields.Raw(allow_none=True)  # For file uploads
    
    @validates_schema
    def validate_name(self, data, **kwargs):
        if not data.get('name') or not data['name'].strip():
            raise ValidationError('Category name is required and cannot be empty', 'name')

class CategoryUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    parent_id = fields.UUID(allow_none=True)
    enable = fields.Bool()
    translations = fields.Dict()
    icon = fields.Raw(allow_none=True)
    
    @validates_schema
    def validate_name(self, data, **kwargs):
        if 'name' in data and (not data['name'] or not data['name'].strip()):
            raise ValidationError('Category name cannot be empty', 'name')

class CategoryTranslationSchema(Schema):
    language = fields.Str(required=True, validate=validate.Length(min=2, max=5))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(max=1000))
