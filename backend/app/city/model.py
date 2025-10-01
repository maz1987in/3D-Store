import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config
from database import Base
from datetime import datetime, timezone
import uuid

class City(Translatable, Base):
    __tablename__ = 'city'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    code = sql.Column(sql.String(50), nullable=False, unique=True)
    country = sql.Column(sql.String(100), nullable=False, default='Oman')
    is_active = sql.Column(sql.Boolean, default=True)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    product_shipping_cities = relationship("ProductShippingCity", back_populates="city")

    def json(self):
        data = {}
        data['id'] = self.id
        data['code'] = self.code
        data['country'] = self.country
        data['is_active'] = self.is_active
        data['create_date'] = self.create_date.isoformat() if self.create_date else None
        data['modified_date'] = self.modified_date.isoformat() if self.modified_date else None
        
        # Add translated names
        name = {}
        for locale in Config.AVAILABLE_LOCALES:
            name[locale] = self.translations[locale].name
        data['name'] = name
        
        return data

class CityTranslation(translation_base(City)):
    __tablename__ = 'city_translations'
    name = sql.Column(sql.String(255), nullable=False)