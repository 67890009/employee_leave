from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import ActiveMixin, BaseModel

if TYPE_CHECKING:
    from app.users.model import User


class Department(BaseModel, ActiveMixin):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="department"
    )