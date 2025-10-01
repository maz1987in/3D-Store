import sqlalchemy as sql
from sqlalchemy_utils import UUIDType

from database import Base
from datetime import datetime, timezone


class Staff(Base):
    __tablename__ = 'staff'

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    nationality = sql.Column(sql.String(255), nullable=False)
    name = sql.Column(sql.String(255), nullable=False)
    id_card_number = sql.Column(sql.String(255), nullable=False, unique=True)
    expiry_date = sql.Column(sql.DateTime, nullable=False)
    salary = sql.Column(sql.Float, nullable=False)
    details = sql.Column(sql.JSON, nullable=True)
    attachments = sql.Column(sql.JSON, nullable=True)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        data['nationality'] = self.nationality
        data['id_card_number'] = self.id_card_number
        data['expiry_date'] = self.expiry_date
        data['salary'] = self.salary
        data['details'] = self.details
        data['attachments'] = self.attachments
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        data['name'] = self.name

        return data