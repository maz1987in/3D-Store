import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from config import Config
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from database import Base
from datetime import datetime, timezone
from app.common.enum import ExpenseStatusEnum


class ExpenseCategory(Translatable, Base):
    __tablename__ = 'expense_category'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    parent_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('expense_category.id', ondelete='SET NULL', name='fk_expense_category_parent_id'), nullable=True)
    order = sql.Column(sql.Integer)
    sub_category = sql.orm.relationship('ExpenseCategory', backref=sql.orm.backref('parent', remote_side='ExpenseCategory.id'))

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

    def for_short(self):
        data = {}
        data["id"] = self.id
        name = {}
        content = {}
        for local in Config().AVAILABLE_LOCALES:
            name[local] = self.translations[local].name
            content[local] = self.translations[local].content
        data["name"] = name
        data["content"] = content
        return data

class ExpenseCategoryTranslation(translation_base(ExpenseCategory)):
    __tablename__ = 'expense_category_translations'
    name = sql.Column(sql.Unicode(255))
    content = sql.Column(sql.UnicodeText)


class Expense(Base):
    __tablename__ = 'expense'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = sql.Column(sql.String(500), nullable=False)
    category_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('expense_category.id', ondelete='SET NULL', name='fk_expense_category_id'), nullable=True, index=True)
    category = sql.orm.relationship('ExpenseCategory', backref='expenses')
    date = sql.Column(sql.DateTime, nullable=False)
    amount = sql.Column(sql.Float, nullable=False)
    description = sql.Column(sql.Text, nullable=True)
    status = sql.Column(sql.Enum(ExpenseStatusEnum), nullable=False, default=ExpenseStatusEnum.PENDING)
    attachments = sql.Column(sql.JSON, default=[])
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    fiscal_year_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('fiscal_year.id', ondelete='SET NULL', name='fk_expense_fiscal_year_id'), nullable=True, index=True)

    def json(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['category'] = self.category.json() if self.category else None
        data['date'] = self.date
        data['amount'] = self.amount
        data['description'] = self.description
        data['status'] = self.status.value
        data['attachments'] = self.attachments
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        data['fiscal_year_id'] = self.fiscal_year_id
        return data