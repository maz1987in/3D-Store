import sqlalchemy as sql
from sqlalchemy.orm import relationship
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy_utils import UUIDType

from database import Base

class Media(Base): 
    __tablename__ = 'media'

    id = sql.Column(UUIDType(binary=False), primary_key=True)
    model_type = sql.Column(sql.String(length=255))
    model_id = sql.Column(sql.String(length=255))
    collection_name = sql.Column(sql.String(length=255))
    name = sql.Column(sql.String(length=255))
    mime_type = sql.Column(sql.String(length=255))
    disk = sql.Column(sql.String(length=255))
    size = sql.Column(sql.String(length=255))
    order_column = sql.Column(sql.Integer)
    file = sql.Column(UploadedFileField)
    custom_properties = sql.Column(sql.JSON)
    create_date = sql.Column(sql.DateTime)
    last_modified = sql.Column(sql.DateTime)