import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey


class Inventory(Base):
    __tablename__ = 'inventory'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    product_id = sql.Column(UUIDType(binary=False), ForeignKey('product.id',ondelete='SET NULL', name='fk_inventory_product_id'), nullable=True, index=True)
    branch_id = sql.Column(UUIDType(binary=False), ForeignKey('branch.id',ondelete='SET NULL', name='fk_inventory_branch_id'), nullable=True, index=True)
    store_id = sql.Column(UUIDType(binary=False), ForeignKey('store.id',ondelete='SET NULL', name='fk_inventory_store_id'), nullable=True, index=True)
    quantity = sql.Column(sql.Integer, nullable=False, default=0)
    quantity_alert = sql.Column(sql.Integer, nullable=True)
    
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc),index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product")
    branch = relationship("Branch")
    store = relationship("Store")

    def json(self):
        data = {}
        data['id'] = self.id
        data['product_id'] = self.product_id
        data['branch_id'] = self.branch_id
        data['store_id'] = self.store_id
        data['quantity'] = self.quantity
        data['quantity_alert'] = self.quantity_alert
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data