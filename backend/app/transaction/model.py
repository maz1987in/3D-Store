import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from app.common.enum import TransactionType
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey


class Transaction(Base):
    __tablename__ = 'transaction'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    product_id = sql.Column(UUIDType(binary=False), ForeignKey('product.id',ondelete='SET NULL', name='fk_transaction_product_id'), nullable=True, index=True)
    from_location_id = sql.Column(UUIDType(binary=False), ForeignKey('branch.id', ondelete='SET NULL', name='fk_transaction_from_location_id'), nullable=True, index=True)
    to_location_id = sql.Column(UUIDType(binary=False), ForeignKey('branch.id', ondelete='SET NULL', name='fk_transaction_to_location_id'), nullable=True, index=True)
    quantity = sql.Column(sql.Integer, nullable=False, default=0)
    transaction_type = sql.Column('transaction_type', sql.Enum(TransactionType), nullable=False)
    transaction_date = sql.Column(sql.DateTime, index=True, default=datetime.now(timezone.utc))
    financial_year_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('fiscal_year.id', ondelete='SET NULL', name='fk_transaction_fiscal_year_id'), nullable=True, index=True)
    
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc),index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product")
    from_location = relationship("Branch", foreign_keys=[from_location_id])
    to_location = relationship("Branch", foreign_keys=[to_location_id])
    financial_year = relationship("FiscalYear")

    def json(self):
        data = {}
        data['id'] = self.id
        data['product_id'] = self.product_id
        data['from_location_id'] = self.from_location_id
        data['to_location_id'] = self.to_location_id
        data['quantity'] = self.quantity
        data['transaction_type'] = self.transaction_type.value
        data['transaction_date'] = self.transaction_date
        data['financial_year_id'] = self.financial_year_id
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data
