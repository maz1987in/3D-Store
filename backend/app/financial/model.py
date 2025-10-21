import uuid
import sqlalchemy as sql
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from config import Config
from app.common.enum import FiscalYearStatusEnum

from database import Base
from datetime import datetime, timezone


class FiscalYear(Base):
    __tablename__ = 'fiscal_year'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    company_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('company.id', ondelete='SET NULL', name='fk_fiscal_year_company_id'), nullable=True, index=True)
    start_date = sql.Column(sql.Date, nullable=False)
    end_date = sql.Column(sql.Date, nullable=False)
    status = sql.Column(sql.Enum(FiscalYearStatusEnum), nullable=False, default=FiscalYearStatusEnum.OPEN)
    locked = sql.Column(sql.Boolean, default=False)
    notes = sql.Column(sql.Text)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc),index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    company = relationship("Company")
    fiscal_periods = relationship("FiscalPeriod", back_populates="financial_year", cascade="all, delete-orphan")

    def json(self):
        data = {}
        data['id'] = self.id
        data['company_id'] = self.company_id
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['status'] = self.status.value
        data['locked'] = self.locked
        data['notes'] = self.notes
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data


class FiscalPeriod(Base):
    __tablename__ = 'fiscal_period'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    company_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('company.id', ondelete='CASCADE', name='fk_fiscal_period_company_id'), nullable=False, index=True)
    financial_year_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('fiscal_year.id', ondelete='CASCADE', name='fk_fiscal_period_financial_year_id'), nullable=False, index=True)
    period_name = sql.Column(sql.String(255), nullable=False)
    start_date = sql.Column(sql.Date, nullable=False)
    end_date = sql.Column(sql.Date, nullable=False)
    status = sql.Column(sql.Enum(FiscalYearStatusEnum), nullable=False, default=FiscalYearStatusEnum.OPEN)

    # Relationships
    company = relationship("Company")
    financial_year = relationship("FiscalYear", back_populates="fiscal_periods")

    def json(self):
        data = {}
        data['id'] = self.id
        data['company_id'] = self.company_id
        data['financial_year_id'] = self.financial_year_id
        data['period_name'] = self.period_name
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['status'] = self.status.value
        return data