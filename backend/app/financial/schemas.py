"""
Financial module validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date


class FiscalYearCreateSchema(Schema):
    """Schema for creating a fiscal year"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'Fiscal year name is required'}
    )
    start_date = fields.Date(
        required=True,
        error_messages={'required': 'Start date is required'}
    )
    end_date = fields.Date(
        required=True,
        error_messages={'required': 'End date is required'}
    )
    description = fields.Str(
        validate=validate.Length(max=500)
    )
    is_active = fields.Bool(load_default=False)
    is_closed = fields.Bool(load_default=False)
    
    @validates('end_date')
    def validate_end_date(self, value):
        """Validate end date is after start date"""
        if hasattr(self, 'start_date') and value <= self.start_date:
            raise ValidationError('End date must be after start date')


class FiscalYearUpdateSchema(Schema):
    """Schema for updating a fiscal year"""
    name = fields.Str(
        validate=validate.Length(min=2, max=100)
    )
    start_date = fields.Date()
    end_date = fields.Date()
    description = fields.Str(
        validate=validate.Length(max=500)
    )
    is_active = fields.Bool()
    is_closed = fields.Bool()


class FiscalPeriodCreateSchema(Schema):
    """Schema for creating a fiscal period"""
    fiscal_year_id = fields.UUID(
        required=True,
        error_messages={'required': 'Fiscal year ID is required'}
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'Period name is required'}
    )
    period_number = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=12),
        error_messages={'required': 'Period number is required'}
    )
    start_date = fields.Date(
        required=True,
        error_messages={'required': 'Start date is required'}
    )
    end_date = fields.Date(
        required=True,
        error_messages={'required': 'End date is required'}
    )
    is_closed = fields.Bool(load_default=False)


class FiscalPeriodUpdateSchema(Schema):
    """Schema for updating a fiscal period"""
    name = fields.Str(
        validate=validate.Length(min=2, max=100)
    )
    period_number = fields.Int(
        validate=validate.Range(min=1, max=12)
    )
    start_date = fields.Date()
    end_date = fields.Date()
    is_closed = fields.Bool()


class FinancialReportFilterSchema(Schema):
    """Schema for filtering financial reports"""
    fiscal_year_id = fields.UUID()
    start_date = fields.Date()
    end_date = fields.Date()
    report_type = fields.Str(
        validate=validate.OneOf([
            'income_statement',
            'balance_sheet',
            'cash_flow',
            'profit_loss'
        ])
    )
    branch_id = fields.UUID()

