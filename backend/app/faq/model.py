import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config

from database import Base
from datetime import datetime, timezone


class FaqTopic(Translatable, Base):
    __tablename__ = 'faq_topic'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE
    id = sql.Column(UUIDType(binary=False), primary_key=True)
    create_date = sql.Column(sql.DateTime, default=datetime)
    modified_date = sql.Column(sql.DateTime, default=datetime)
    faqs = sql.orm.relationship("Faq", backref="faq_topic", lazy=True)

    def json(self):
        data = {}
        data['id'] = self.id
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        title = {}
        for local in Config().AVAILABLE_LOCALES:
            title[local] = self.translations[local].title
        data['title'] = title
        data['faqs'] = [faq.json() for faq in self.faqs]
        return data
    
    def for_short(self):
        data = {}
        data['id'] = self.id
        title = {}
        for local in Config().AVAILABLE_LOCALES:
            title[local] = self.translations[local].title
        data['title'] = title
        return data

class FaqTopicTranslation(translation_base(FaqTopic)):
    __tablename__ = 'faq_topic_translations'

    title = sql.Column(sql.UnicodeText)



class Faq(Translatable, Base):
    __tablename__ = 'faq'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE
    id = sql.Column(UUIDType(binary=False), primary_key=True)
    faq_topic_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('faq_topic.id', ondelete='CASCADE'))
    create_date = sql.Column(sql.DateTime, default=datetime)
    modified_date = sql.Column(sql.DateTime, default=datetime)

    def json(self):
        data = {}
        data['id'] = self.id
        data['faq_topic_id'] = self.faq_topic_id
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        content = {}
        question = {}
        for local in Config().AVAILABLE_LOCALES:
            content[local] = self.translations[local].content
            question[local] = self.translations[local].question
        data['content'] = content
        data['question'] = question
        return data

class FaqTranslation(translation_base(Faq)):
    __tablename__ = 'faq_translations'
    question = sql.Column(sql.UnicodeText)
    content = sql.Column(sql.UnicodeText)

