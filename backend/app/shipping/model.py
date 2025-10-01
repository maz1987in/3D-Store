import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable

from app.common.enum import ShippingStatusEnum
from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric



class Shipping(Base):
    __tablename__ = 'shipping'

    id = Column(UUIDType(binary=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey('order.id'), nullable=False, unique=True)
    carrier = Column(String(100))
    tracking_number = Column(String(100), index=True)
    shipping_cost = Column(Numeric(10, 3), nullable=True)
    shipping_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False, index=True)
    status = Column(sql.Enum(ShippingStatusEnum), default=ShippingStatusEnum.PENDING)
    create_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modified_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="shipping_info")

    def json(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'carrier': self.carrier,
            'tracking_number': self.tracking_number,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost is not None else None,
            'shipping_date': self.shipping_date.isoformat() if self.shipping_date else None,
            'status': self.status.value,  
            'create_date': self.create_date.isoformat(),
            'modified_date': self.modified_date.isoformat()
        }