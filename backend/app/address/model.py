import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

class ShippingAddress(Base):
    __tablename__ = 'shipping_addresses'

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    address_line1 = sql.Column(sql.String(255), nullable=False)
    address_line2 = sql.Column(sql.String(255), nullable=True)
    city = sql.Column(sql.String(100), nullable=False)
    state = sql.Column(sql.String(100), nullable=True)
    postal_code = sql.Column(sql.String(20), nullable=True)
    country = sql.Column(sql.String(100), nullable=False)
    phone = sql.Column(sql.String(30), nullable=True)
    label = sql.Column(sql.String(50), nullable=True)  # e.g. "Home", "Work"
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))


    user = relationship("User", back_populates="shipping_addresses")

    def json(self):
        data = {}
        data['id'] = self.id
        data['user_id'] = self.user_id
        data['address_line1'] = self.address_line1
        data['address_line2'] = self.address_line2
        data['city'] = self.city
        data['state'] = self.state
        data['postal_code'] = self.postal_code
        data['country'] = self.country
        data['phone'] = self.phone
        data['label'] = self.label
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data