from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.leave_types.model import LeaveType


class LeaveTypeRepository:

    async def create(
        self,
        db: AsyncSession,
        leave_type: LeaveType
    ) -> LeaveType:
        db.add(leave_type)
        await db.commit()
        await db.refresh(leave_type)
        return leave_type

    async def get_by_id(
        self,
        db: AsyncSession,
        leave_type_id: UUID
    ) -> LeaveType | None:

        result = await db.execute(
            select(LeaveType).where(LeaveType.id == leave_type_id)
        )

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> LeaveType | None:

        result = await db.execute(
            select(LeaveType).where(LeaveType.name == name)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession
    ) -> list[LeaveType]:

        result = await db.execute(
            select(LeaveType).order_by(LeaveType.name)
        )

        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        leave_type: LeaveType
    ) -> LeaveType:

        await db.commit()
        await db.refresh(leave_type)
        return leave_type

    async def delete(
        self,
        db: AsyncSession,
        leave_type: LeaveType
    ) -> None:

        await db.delete(leave_type)
        await db.commit()