from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from database import Base

class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(UUIDType(binary=False), primary_key=True)
    product_id = Column(UUIDType(binary=False), ForeignKey('product.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUIDType(binary=False), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)  # <-- Add ForeignKey here
    score = Column(Float, nullable=False, index=True)
    comment = Column(Text, nullable=True)

    product = relationship("Product", back_populates="ratings")
    user = relationship("User", back_populates="ratings")