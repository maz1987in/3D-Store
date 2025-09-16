from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime, text
from typing import Optional
from .authz import Base


class PrintJob(Base):
    __tablename__ = 'print_jobs'
    # Status constants
    STATUS_QUEUED = 'QUEUED'
    STATUS_STARTED = 'STARTED'
    STATUS_COMPLETED = 'COMPLETED'
    ALL_STATUSES = (STATUS_QUEUED, STATUS_STARTED, STATUS_COMPLETED)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('products.id'), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_QUEUED, index=True)
    assigned_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP'))