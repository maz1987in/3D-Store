from depot.fields.sqlalchemy import UploadedFileField
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import translation_base, Translatable
from app.common.enum import PlatformEnum
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey

#make_translatable(options={
#        'locales': list(current_app.config['AVAILABLE_LOCALES'].keys()),
#    })

class SliderType(Base):
    __tablename__ = 'slider_type'
    name = sql.Column(sql.String(50), primary_key=True)
    slider = relationship('Slider')

class Slider(Translatable, Base):
    __tablename__ = 'slider'
    __translatable__ = {
        'locales': Config().AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE
 
    id = sql.Column(UUIDType(binary=False), primary_key=True)
    enable = sql.Column(sql.Boolean(), nullable=False, server_default='0')
    from_date = sql.Column(sql.DateTime, index=True, default=datetime)
    to_date = sql.Column(sql.DateTime, index=True, default=datetime)
    order = sql.Column(sql.Integer)
    url = sql.Column(sql.String(255))
    slider_type = sql.Column(sql.String(length=255), sql.ForeignKey('slider_type.name', name='fk_slider_slider_type'), nullable=False)
    image = sql.Column(UploadedFileField(upload_storage ='slider'), nullable=False)

    platform = sql.Column('platform', sql.Enum(PlatformEnum),server_default='ALL')
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        data['enable'] = self.enable
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['order'] = self.order
        data['url'] = self.url
        data['slider_type'] = self.slider_type
        data['image'] = self.image.url if self.image else None
        data['platform'] = self.platform
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        title = {}
        content = {}
        for local in Config().AVAILABLE_LOCALES:
            title[local] = self.translations[local].title
            content[local] = self.translations[local].content
        data['content'] = content
        data['title'] = title



    
    

class SliderTranslation(translation_base(Slider)):
    __tablename__ = 'slider_translations'
    title = sql.Column(sql.Unicode(255))
    content = sql.Column(sql.UnicodeText)
   
