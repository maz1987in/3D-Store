from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from decimal import Decimal
import uuid

class SellerCreateSchema(Schema):
    business_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    contact_person = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    address = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    country = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    business_license = fields.Str(validate=validate.Length(max=100))
    tax_id = fields.Str(validate=validate.Length(max=100))
    bank_account = fields.Str(validate=validate.Length(max=100))
    commission_rate = fields.Decimal(validate=validate.Range(min=0, max=100))
    settlement_period = fields.Str(validate=validate.OneOf(['weekly', 'bi_weekly', 'monthly', 'quarterly']))
    is_active = fields.Bool(missing=True)
    
    @validates_schema
    def validate_commission_rate(self, data, **kwargs):
        commission_rate = data.get('commission_rate')
        if commission_rate is not None and (commission_rate < 0 or commission_rate > 100):
            raise ValidationError('Commission rate must be between 0 and 100', 'commission_rate')

class SellerUpdateSchema(Schema):
    business_name = fields.Str(validate=validate.Length(min=1, max=255))
    contact_person = fields.Str(validate=validate.Length(min=1, max=255))
    email = fields.Email()
    phone = fields.Str(validate=validate.Length(min=10, max=20))
    address = fields.Str(validate=validate.Length(min=1, max=500))
    city = fields.Str(validate=validate.Length(min=1, max=100))
    country = fields.Str(validate=validate.Length(min=1, max=100))
    business_license = fields.Str(validate=validate.Length(max=100))
    tax_id = fields.Str(validate=validate.Length(max=100))
    bank_account = fields.Str(validate=validate.Length(max=100))
    commission_rate = fields.Decimal(validate=validate.Range(min=0, max=100))
    settlement_period = fields.Str(validate=validate.OneOf(['weekly', 'bi_weekly', 'monthly', 'quarterly']))
    is_active = fields.Bool()

class SellerCommissionSchema(Schema):
    seller_id = fields.UUID(required=True)
    commission_rate = fields.Decimal(required=True, validate=validate.Range(min=0, max=100))
    effective_date = fields.Date(required=True)
    end_date = fields.Date(allow_none=True)
    is_active = fields.Bool(missing=True)

class SellerPaymentSchema(Schema):
    seller_id = fields.UUID(required=True)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    payment_method = fields.Str(required=True, validate=validate.OneOf(['bank_transfer', 'paypal', 'check']))
    payment_date = fields.Date(required=True)
    reference_number = fields.Str(validate=validate.Length(max=100))
    notes = fields.Str(validate=validate.Length(max=1000))

class SellerDocumentSchema(Schema):
    seller_id = fields.UUID(required=True)
    document_type = fields.Str(required=True, validate=validate.OneOf([
        'business_license', 'tax_certificate', 'bank_statement', 'identity_document', 'contract'
    ]))
    document_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    file = fields.Raw(required=True)  # For file uploads
    expiry_date = fields.Date(allow_none=True)
    is_verified = fields.Bool(missing=False)
