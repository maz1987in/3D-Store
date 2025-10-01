import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

from database import Base

class Favorite(Base): 
    __tablename__ = 'favorite'

    id = sql.Column(UUIDType(binary=False), primary_key=True, nullable=False)
    model_type = sql.Column(sql.String(length=255))
    model_id = sql.Column(sql.String(length=255))
    user_id = sql.Column(sql.String(length=255))
    create_date = sql.Column(sql.DateTime)