import sqlalchemy as sql
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.common.enum import QuoteStatusEnum
from sqlalchemy_utils import UUIDType
import uuid

from database import Base

class Quotation(Base):
    __tablename__ = 'quotations'
 
    id = sql.Column(UUIDType(binary=False), primary_key=True, nullable=False, default=uuid.uuid4)
    number = sql.Column(sql.String(length=255), nullable=False, index=True, unique=True)
    total_amount = sql.Column(sql.Numeric(10,3, asdecimal=False))
    discount = sql.Column(sql.Numeric(10,3, asdecimal=False))
    tax = sql.Column(sql.Numeric(10,3, asdecimal=False))
    grand_total = sql.Column(sql.Numeric(10,3, asdecimal=False))
    customer_id = sql.Column(UUIDType(binary=False), ForeignKey('customer.id', ondelete='SET NULL', name='fk_quotation_customer_id'), nullable=True, index=True)
    branch_id = sql.Column(UUIDType(binary=False), ForeignKey('branch.id', ondelete='SET NULL', name='fk_quotation_branch_id'), nullable=True, index=True)
    user_id = sql.Column(UUIDType(binary=False), ForeignKey('users.id', ondelete='SET NULL', name='fk_quotation_user_id'), nullable=True, index=True)
    # Note: Column name kept as 'qoute_status' to match existing database schema
    # Property accessor provides correct 'quote_status' name
    quote_status = sql.Column('qoute_status', sql.Enum(QuoteStatusEnum), default=QuoteStatusEnum.PENDING, index=True)
    date = sql.Column(sql.DATE)
    summary = sql.Column(sql.JSON)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    customer = relationship("Customer")
    branch = relationship("Branch")
    user = relationship("User")

    def json(self):
        data = {}
        data['id'] = self.id
        data['number'] = self.number
        data['total_amount'] = self.total_amount
        data['discount'] = self.discount
        data['tax'] = self.tax
        data['grand_total'] = self.grand_total
        data['customer_id'] = self.customer_id
        data['branch_id'] = self.branch_id
        data['user_id'] = self.user_id
        data['quote_status'] = self.quote_status.value  # Fixed typo
        data['date'] = self.date
        data['summary'] = self.summary
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data