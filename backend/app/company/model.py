import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config

from database import Base
from datetime import datetime, timezone


class Company(Translatable, Base):
    __tablename__ = 'company'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    location = sql.Column(sql.String(255), nullable=False)
    manager = sql.Column(sql.String(255), nullable=True)
    cr_number = sql.Column(sql.String(255), nullable=False, unique=True)
    tax_id = sql.Column(sql.String(255), nullable=False, unique=True)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        data['location'] = self.location
        data['manager'] = self.manager
        data['cr_number'] = self.cr_number
        data['tax_id'] = self.tax_id
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        name = {}
        for local in Config().AVAILABLE_LOCALES:
            name[local] = self.translations[local].name
        data['name'] = name
        return data

class CompanyTranslation(translation_base(Company)):
    __tablename__ = 'company_translations'
    name = sql.Column(sql.String(255))