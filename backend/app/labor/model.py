import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from config import Config
from sqlalchemy_i18n import translation_base, Translatable
from database import Base
from datetime import datetime, timezone
from app.common.enum import LaborStatusEnum, LaborUnitEnum


class LaborCategory(Translatable, Base):
    __tablename__ = 'labor_category'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    parent_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('labor_category.id', ondelete='SET NULL', name='fk_labor_category_parent_id'), nullable=True)
    order = sql.Column(sql.Integer)
    sub_category = sql.orm.relationship('LaborCategory', backref=sql.orm.backref('parent', remote_side='LaborCategory.id'))

    def json(self):
        data = {}
        data["id"] = self.id
        data["parent_id"] = self.parent_id
        data["order"] = self.order
        name = {}
        content = {}
        for local in Config().AVAILABLE_LOCALES:
            name[local] = self.translations[local].name
            content[local] = self.translations[local].content
        data["name"] = name
        data["content"] = content
        return data


class LaborCategoryTranslation(translation_base(LaborCategory)):
    __tablename__ = 'labor_category_translations'
    name = sql.Column(sql.Unicode(255))
    content = sql.Column(sql.UnicodeText)


class Labor(Base):
    __tablename__ = 'labor'

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    code = sql.Column(sql.String(255), nullable=False, index=True, unique=True)
    name = sql.Column(sql.String(255), nullable=False)
    category_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('labor_category.id', ondelete='SET NULL', name='fk_labor_category_id'), nullable=True, index=True)
    category = sql.orm.relationship('LaborCategory', backref='labors')
    unit = sql.Column(sql.Enum(LaborUnitEnum), nullable=False, default=LaborUnitEnum.HOUR)
    unit_price = sql.Column(sql.Float, nullable=False)
    description = sql.Column(sql.Text, nullable=True)
    status = sql.Column(sql.Enum(LaborStatusEnum), nullable=False, default=LaborStatusEnum.PENDING)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        data['code'] = self.code
        data['name'] = self.name
        data['category'] = self.category.json() if self.category else None
        data['unit'] = self.unit.value
        data['unit_price'] = self.unit_price
        data['description'] = self.description
        data['status'] = self.status.value
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        return data