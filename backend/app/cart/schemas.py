"""
Cart module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class CartItemAddSchema(Schema):
    """Schema for adding item to cart"""
    product_id = fields.UUID(
        required=True,
        error_messages={'required': 'Product ID is required'}
    )
    quantity = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01, max=9999.99),
        error_messages={'required': 'Quantity is required'}
    )
    unit_price = fields.Decimal(
        places=2,
        validate=validate.Range(min=0)
    )
    options = fields.Dict()  # For product variants, customizations
    notes = fields.Str(
        validate=validate.Length(max=500)
    )


class CartItemUpdateSchema(Schema):
    """Schema for updating cart item"""
    quantity = fields.Decimal(
        places=2,
        validate=validate.Range(min=0.01, max=9999.99)
    )
    options = fields.Dict()
    notes = fields.Str(
        validate=validate.Length(max=500)
    )


class CartCheckoutSchema(Schema):
    """Schema for cart checkout"""
    shipping_address_id = fields.UUID()
    billing_address_id = fields.UUID()
    payment_method = fields.Str(
        required=True,
        validate=validate.OneOf([
            'credit_card',
            'debit_card',
            'cash',
            'bank_transfer',
            'thawani',
            'ompay'
        ]),
        error_messages={'required': 'Payment method is required'}
    )
    shipping_method = fields.Str(
        validate=validate.OneOf([
            'standard',
            'express',
            'overnight',
            'pickup'
        ]),
        load_default='standard'
    )
    notes = fields.Str(
        validate=validate.Length(max=1000)
    )
    coupon_code = fields.Str(
        validate=validate.Length(max=50)
    )


class CartApplyCouponSchema(Schema):
    """Schema for applying coupon to cart"""
    coupon_code = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        error_messages={'required': 'Coupon code is required'}
    )


class CartMergeSchema(Schema):
    """Schema for merging guest cart with user cart"""
    guest_cart_id = fields.UUID(
        required=True,
        error_messages={'required': 'Guest cart ID is required'}
    )
    merge_strategy = fields.Str(
        validate=validate.OneOf(['combine', 'replace', 'keep_user']),
        load_default='combine'
    )

