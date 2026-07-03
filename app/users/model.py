from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import UserRole
from app.db.base import ActiveMixin, BaseModel

if TYPE_CHECKING:
    from app.departments.model import Department
    from app.leave_requests.model import LeaveRequest


class User(BaseModel, ActiveMixin):
    __tablename__ = "users"

    employee_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
    )

    department_id: Mapped[UUID] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
    )

    manager_id: Mapped[UUID]= mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    department: Mapped["Department"] = relationship(
        back_populates="users",
    )

    manager: Mapped["User | None"] = relationship(
        remote_side="User.id",
        back_populates="team_members",
    )

    team_members: Mapped[list["User"]] = relationship(
        back_populates="manager",
    )

    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        foreign_keys="LeaveRequest.employee_id",
        back_populates="employee",
    )

    approved_leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        foreign_keys="LeaveRequest.approved_by",
        back_populates="approver",
    )