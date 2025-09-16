from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime, text
from typing import Optional

from .authz import Base


class Order(Base):
    __tablename__ = 'orders'
    # Lifecycle status constants
    STATUS_NEW = 'NEW'
    STATUS_APPROVED = 'APPROVED'
    STATUS_FULFILLED = 'FULFILLED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'
    ALL_STATUSES = (
        STATUS_NEW,
        STATUS_APPROVED,
        STATUS_FULFILLED,
        STATUS_COMPLETED,
        STATUS_CANCELLED
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_NEW)
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP'))
