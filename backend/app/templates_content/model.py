import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from app.common.enum import MediaTypeEnum
from config import Config

from database import Base
from datetime import datetime, timezone

class TemplatesContent(Translatable, Base):
    __tablename__ = 'templates_content'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    
    locale = Config.DEFAULT_LOCALE
    id = sql.Column(UUIDType(binary=False), primary_key=True)
    key = sql.Column(sql.String(length=20),index=True, unique=False, nullable=False)
    media_type = sql.Column(sql.Enum(MediaTypeEnum),index=True, unique=False, nullable=False, server_default='sms')
    model_type = sql.Column(sql.String(length=255))
    model_op = sql.Column(sql.String(length=255))
    model_id = sql.Column(UUIDType(binary=False))
    description = sql.Column(sql.UnicodeText)

    create_date = sql.Column(sql.DateTime, default=datetime)
    modified_date = sql.Column(sql.DateTime, default=datetime)

    __table_args__ = (sql.UniqueConstraint('key', 'media_type', name='_key_media_uc'),)

    def json(self):
        data = {}
        data['id'] = self.id
        data['key'] = self.key
        data['media_type'] = self.media_type.value
        data['model_type'] = self.model_type
        data['model_op'] = self.model_op
        data['model_id'] = self.model_id
        data['description'] = self.description
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        subject = {}
        content = {}
        for local in Config.AVAILABLE_LOCALES:
            subject[local] = self.translations[local].subject
            content[local] = self.translations[local].content
        data['subject'] = subject
        data['content'] = content
        return data


class TemplatesContentTranslation(translation_base(TemplatesContent)):
    __tablename__ = 'templates_content_translations'

    subject = sql.Column(sql.Unicode(255))
    content = sql.Column(sql.UnicodeText)

