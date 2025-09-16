from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime, text
from typing import Optional

from .authz import Base


class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    # Status constants
    STATUS_DRAFT = 'DRAFT'
    STATUS_RECEIVED = 'RECEIVED'
    STATUS_CLOSED = 'CLOSED'
    ALL_STATUSES = (STATUS_DRAFT, STATUS_RECEIVED, STATUS_CLOSED)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_DRAFT, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP'))
