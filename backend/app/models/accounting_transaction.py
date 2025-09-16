from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func
from .authz import Base


class AccountingTransaction(Base):
    __tablename__ = 'accounting_transactions'
    # Status lifecycle: NEW -> APPROVED -> PAID (terminal) | NEW -> REJECTED (terminal)
    STATUS_NEW = 'NEW'
    STATUS_APPROVED = 'APPROVED'
    STATUS_PAID = 'PAID'
    STATUS_REJECTED = 'REJECTED'
    ALL_STATUSES = (STATUS_NEW, STATUS_APPROVED, STATUS_PAID, STATUS_REJECTED)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_NEW, index=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

__all__ = ["AccountingTransaction"]
