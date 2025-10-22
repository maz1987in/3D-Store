"""
User module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
import re


class UserCreateSchema(Schema):
    """Schema for creating a new user"""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=255),
        error_messages={'required': 'Username is required'}
    )
    phone = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=20),
        error_messages={'required': 'Phone number is required'}
    )
    email = fields.Email(
        allow_none=True,
        validate=validate.Length(max=255)
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=50),
        error_messages={'required': 'Password is required'},
        load_only=True  # Never include in output
    )
    name = fields.Str(
        allow_none=True,
        validate=validate.Length(max=255)
    )
    user_type = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['USER', 'ADMIN', 'SELLER', 'STAFF'])
    )
    language = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['ENGLISH', 'ARABIC'])
    )
    user_details = fields.Dict(allow_none=True)
    agree = fields.Bool(load_default=False)
    
    @validates('password')
    def validate_password(self, value):
        """Validate password strength"""
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', value):
            raise ValidationError(
                'Password must be at least 8 characters and contain only '
                'letters, numbers, and special characters (@#$%^&+=)'
            )
    
    @validates('phone')
    def validate_phone(self, value):
        """Validate phone number format"""
        # Remove common phone separators
        cleaned = value.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if not cleaned.replace('+', '').isdigit():
            raise ValidationError('Phone number must contain only digits and optional + prefix')


class UserUpdateSchema(Schema):
    """Schema for updating an existing user"""
    username = fields.Str(
        validate=validate.Length(min=3, max=255)
    )
    phone = fields.Str(
        validate=validate.Length(min=8, max=20)
    )
    email = fields.Email(
        validate=validate.Length(max=255)
    )
    name = fields.Str(
        validate=validate.Length(max=255)
    )
    user_type = fields.Str(
        validate=validate.OneOf(['USER', 'ADMIN', 'SELLER', 'STAFF'])
    )
    language = fields.Str(
        validate=validate.OneOf(['ENGLISH', 'ARABIC'])
    )
    user_details = fields.Dict()
    active = fields.Bool()


class PasswordChangeSchema(Schema):
    """Schema for changing password"""
    old_password = fields.Str(
        required=True,
        load_only=True,
        error_messages={'required': 'Old password is required'}
    )
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=50),
        load_only=True,
        error_messages={'required': 'New password is required'}
    )
    
    @validates('new_password')
    def validate_password(self, value):
        """Validate password strength"""
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', value):
            raise ValidationError(
                'Password must be at least 8 characters and contain only '
                'letters, numbers, and special characters (@#$%^&+=)'
            )
    
    @validates_schema
    def validate_passwords_different(self, data, **kwargs):
        """Ensure new password is different from old password"""
        if 'old_password' in data and 'new_password' in data:
            if data['old_password'] == data['new_password']:
                raise ValidationError(
                    'New password must be different from old password',
                    field_name='new_password'
                )


class RoleCreateSchema(Schema):
    """Schema for creating a role"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={'required': 'Role name is required'}
    )
    description = fields.Str(
        validate=validate.Length(max=255)
    )


class PermissionCreateSchema(Schema):
    """Schema for creating a permission"""
    model = fields.Str(
        validate=validate.Length(max=100)
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'Permission name is required'}
    )


class UserRoleAssignSchema(Schema):
    """Schema for assigning roles to users"""
    user_id = fields.UUID(required=True)
    role_ids = fields.List(
        fields.UUID(),
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'At least one role must be specified'}
    )
