from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func
from .authz import Base


class Vendor(Base):
    __tablename__ = 'vendors'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_INACTIVE = 'INACTIVE'
    ALL_STATUSES = (STATUS_ACTIVE, STATUS_INACTIVE)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True, unique=True)
    contact_email: Mapped[str] = mapped_column(String(150), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_ACTIVE, index=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

__all__ = ["Vendor"]