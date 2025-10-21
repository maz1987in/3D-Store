from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from decimal import Decimal
import uuid

class ExpenseCreateSchema(Schema):
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    category = fields.Str(required=True, validate=validate.OneOf([
        'equipment', 'maintenance', 'materials', 'utilities', 'software', 
        'marketing', 'professional_services', 'travel', 'office_supplies'
    ]))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    vendor = fields.Str(validate=validate.Length(max=255))
    project_id = fields.UUID(allow_none=True)
    expense_date = fields.DateTime(required=True)
    receipt = fields.Raw(allow_none=True)  # For file uploads
    is_billable = fields.Bool(load_default=False)
    
    @validates_schema
    def validate_amount(self, data, **kwargs):
        amount = data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError('Amount must be greater than 0', 'amount')

class ExpenseUpdateSchema(Schema):
    amount = fields.Decimal(validate=validate.Range(min=0.01))
    category = fields.Str(validate=validate.OneOf([
        'equipment', 'maintenance', 'materials', 'utilities', 'software', 
        'marketing', 'professional_services', 'travel', 'office_supplies'
    ]))
    description = fields.Str(validate=validate.Length(min=1, max=1000))
    vendor = fields.Str(validate=validate.Length(max=255))
    project_id = fields.UUID(allow_none=True)
    expense_date = fields.DateTime()
    receipt = fields.Raw(allow_none=True)
    is_billable = fields.Bool()

class ExpenseApprovalSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['approved', 'rejected', 'pending']))
    comments = fields.Str(validate=validate.Length(max=1000))
    approved_by = fields.UUID(required=True)
    
class ExpenseCategorySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    budget_limit = fields.Decimal(validate=validate.Range(min=0))
    is_active = fields.Bool(load_default=True)

class ExpenseBudgetSchema(Schema):
    category_id = fields.UUID(required=True)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0))
    period = fields.Str(required=True, validate=validate.OneOf(['monthly', 'quarterly', 'yearly']))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
