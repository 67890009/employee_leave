from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import ActiveMixin, BaseModel

if TYPE_CHECKING:
    from app.leave_requests.model import LeaveRequest


class LeaveType(BaseModel, ActiveMixin):
    __tablename__ = "leave_types"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    max_days_per_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="leave_type",
    )