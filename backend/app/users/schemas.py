from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from marshmallow_enum import EnumField
import uuid
import re

class UserCreateSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    phone = fields.Str(validate=validate.Length(max=20))
    role_id = fields.UUID(allow_none=True)
    is_active = fields.Bool(missing=True)
    
    @validates_schema
    def validate_password(self, data, **kwargs):
        password = data.get('password', '')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long', 'password')
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Password must contain at least one letter', 'password')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number', 'password')

class UserUpdateSchema(Schema):
    email = fields.Email()
    name = fields.Str(validate=validate.Length(min=1, max=255))
    phone = fields.Str(validate=validate.Length(max=20))
    role_id = fields.UUID(allow_none=True)
    is_active = fields.Bool()

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))

class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError('New password and confirmation do not match', 'confirm_password')
        
        password = data.get('new_password', '')
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Password must contain at least one letter', 'new_password')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number', 'new_password')

class UserProfileSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    phone = fields.Str(validate=validate.Length(max=20))
    bio = fields.Str(validate=validate.Length(max=1000))
    avatar = fields.Raw(allow_none=True)  # For file uploads
