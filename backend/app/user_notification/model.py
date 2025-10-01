import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

from database import Base
from datetime import datetime, timezone

class UserNotification(Base):
    __tablename__ = 'user_notification'
 
    id = sql.Column(UUIDType(binary=False), primary_key=True)
    name = sql.Column(sql.String(128), nullable=False, server_default='system')
    user_id = sql.Column(UUIDType(binary=False), index=True, nullable=False)
    read = sql.Column(sql.Boolean(), nullable=False, server_default='0')
    timestamp = sql.Column(sql.DateTime, index=True, default=datetime)
    message = sql.Column(sql.JSON)

    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'user_id': str(self.user_id),
            'read': self.read,
            'timestamp': self.timestamp,
            'message': self.message
        }

   
