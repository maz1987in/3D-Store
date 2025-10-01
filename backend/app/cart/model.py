import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config

from database import Base
from datetime import datetime, timezone, timezone, timezone
from sqlalchemy.sql.schema import ForeignKey



# add Cart with items

class Cart(Base):
    __tablename__ = 'cart'

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    total = sql.Column(sql.Float)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    items = relationship('Item')

    def json(self):
        data = {}
        data['id'] = self.id
        data['total'] = self.total
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        data['items'] = [item.json() for item in self.items]
        return data


class Item(Base):
    __tablename__ = 'cart_item'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    #name = sql.Column(sql.String(length=255))
    price = sql.Column(sql.Float)
    quantity = sql.Column(sql.Integer)
    service_id = sql.Column(UUIDType(binary=False))
    service_type = sql.Column(sql.String(length=255))
    cart_id = sql.Column(UUIDType(binary=False), ForeignKey('cart.id'))
    
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        #data['name'] = self.name
        data['price'] = self.price
        data['quantity'] = self.quantity
        data['service_id'] = self.service_id
        data['service_type'] = self.service_type
        data['cart_id'] = self.cart_id
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        title = {}
        for local in Config().AVAILABLE_LOCALES:
            title[local] = self.translations[local].title
        data['title'] = title
        return data

class ItemTranslation(translation_base(Item)):
    __tablename__ = 'Item_translations'
    title = sql.Column(sql.UnicodeText)