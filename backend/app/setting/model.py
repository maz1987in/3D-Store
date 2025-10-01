import sqlalchemy as sql
from sqlalchemy.orm import relationship

from database import Base

class Setting(Base):
    __tablename__ = 'app_setting'
 
    key = sql.Column(sql.String(length=50), primary_key=True)
    category = sql.Column(sql.String(length=50))
    value = sql.Column(sql.UnicodeText, nullable=False)
    last_modified = sql.Column(sql.DateTime)

    def json(self):
        return {
            'key': self.key,
            'category': self.category,
            'value': self.value,
            'last_modified': self.last_modified
        }

   
