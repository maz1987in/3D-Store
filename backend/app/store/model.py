import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey


class Store(Translatable, Base):
    __tablename__ = 'store'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    location = sql.Column(sql.String(255), nullable=False)
    manager = sql.Column(sql.String(255), nullable=True)
    
    #category_id = sql.Column(UUIDType(binary=False), ForeignKey('Category.id',ondelete='SET NULL', name='fk_store_category_id'), nullable=True, index=True)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc),index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    #products = relationship('Product', back_populates='store')

    def json(self):
        data = {}
        data['id'] = self.id
        data['location'] = self.location
        data['manager'] = self.manager
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        name = {}
        for local in Config().AVAILABLE_LOCALES:
            name[local] = self.translations[local].name
        data['name'] = name
        return data

class StoreTranslation(translation_base(Store)):
    __tablename__ = 'store_translations'
    name = sql.Column(sql.String(255))