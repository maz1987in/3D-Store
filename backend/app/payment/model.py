import sqlalchemy as sql
from datetime import datetime, timezone, timezone

from app.common.enum import PaymentOptionEnum
from sqlalchemy_utils import UUIDType
import uuid

from database import Base

class Payment(Base):
    __tablename__ = 'payments'
 
    id = sql.Column(UUIDType(binary=False), primary_key=True, nullable=False, default=uuid.uuid4)
    invoice_id = sql.Column(UUIDType(binary=False), nullable=False, default=uuid.uuid4, index=True)
    payment_method = sql.Column('payment_method', sql.Enum(PaymentOptionEnum), default=PaymentOptionEnum.cash)
    amount_paid = sql.Column(sql.Numeric(10,3, asdecimal=False))
    payment_date = sql.Column(sql.DATE)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        data['invoice_id'] = self.invoice_id
        data['payment_method'] = self.payment_method.value
        data['amount_paid'] = self.amount_paid
        data['payment_date'] = self.payment_date
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data