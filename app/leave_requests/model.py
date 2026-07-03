from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import LeaveStatus
from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.leave_types.model import LeaveType
    from app.users.model import User


class LeaveRequest(BaseModel):
    __tablename__ = "leave_requests"

    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    leave_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("leave_types.id"),
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        nullable=False,
    )

    number_of_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus),
        default=LeaveStatus.PENDING,
        nullable=False,
    )

    manager_comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    approved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    employee: Mapped["User"] = relationship(
        foreign_keys=[employee_id],
        back_populates="leave_requests",
    )

    leave_type: Mapped["LeaveType"] = relationship(
        back_populates="leave_requests",
    )

    approver: Mapped["User | None"] = relationship(
        foreign_keys=[approved_by],
        back_populates="approved_leave_requests",
    )