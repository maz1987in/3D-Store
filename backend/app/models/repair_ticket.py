from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func
from app.models.authz import Base

class RepairTicket(Base):
    __tablename__ = 'repair_tickets'
    # Status constants
    STATUS_NEW = 'NEW'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_CLOSED = 'CLOSED'
    ALL_STATUSES = (STATUS_NEW, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_CANCELLED, STATUS_CLOSED)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    device_type: Mapped[str] = mapped_column(String(80), nullable=False)
    issue_summary: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_NEW, index=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Status flow: NEW -> IN_PROGRESS -> COMPLETED -> CLOSED (CANCELLED as alternative terminal)
# MANAGE permission controls state transitions beyond creation.
