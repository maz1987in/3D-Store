import sqlalchemy as sql
from datetime import datetime, timezone, timezone

from app.common.enum import PaymentStatusEnum
from sqlalchemy_utils import UUIDType
import uuid

from database import Base

class InvoiceCounter(Base):
    __tablename__ = "invoice_counter"
    id = sql.Column(sql.Integer, primary_key=True)
    last_number = sql.Column(sql.Integer, default=0)

class Invoice(Base):
    __tablename__ = 'invoices'
 
    id = sql.Column(UUIDType(binary=False), primary_key=True, nullable=False, default=uuid.uuid4)
    number = sql.Column(sql.String(length=255), nullable=False, index=True, unique=True)
    total_amount = sql.Column(sql.Numeric(10,3, asdecimal=False))
    discount = sql.Column(sql.Numeric(10,3, asdecimal=False))
    tax = sql.Column(sql.Numeric(10,3, asdecimal=False))
    delivery_amount = sql.Column(sql.Numeric(10,3, asdecimal=False))
    grand_total = sql.Column(sql.Numeric(10,3, asdecimal=False))
    customer_id = sql.Column(UUIDType(binary=False))
    branch_id = sql.Column(UUIDType(binary=False), index=True)
    user_id =  sql.Column(UUIDType(binary=False), index=True)
    payment_status = sql.Column('payment_status', sql.Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending, index=True)
    date = sql.Column(sql.DATE, index=True)
    summary = sql.Column(sql.JSON)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        data['number'] = self.number
        data['total_amount'] = self.total_amount
        data['discount'] = self.discount
        data['tax'] = self.tax
        data['delivery_amount'] = self.delivery_amount
        data['grand_total'] = self.grand_total
        data['customer_id'] = self.customer_id
        data['branch_id'] = self.branch_id
        data['user_id'] = self.user_id
        data['payment_status'] = self.payment_status.value
        data['date'] = self.date
        data['summary'] = self.summary
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data