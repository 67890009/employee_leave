from datetime import date
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import LeaveStatus
from app.leave_requests.model import LeaveRequest


class LeaveRequestRepository:

    async def create(
        self,
        db: AsyncSession,
        leave_request: LeaveRequest,
    ) -> LeaveRequest:

        db.add(leave_request)
        await db.commit()
        await db.refresh(leave_request)

        return leave_request

    async def get_by_id(
        self,
        db: AsyncSession,
        leave_request_id: UUID,
    ) -> LeaveRequest | None:

        result = await db.execute(
            select(LeaveRequest).where(
                LeaveRequest.id == leave_request_id
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
    ) -> list[LeaveRequest]:

        result = await db.execute(
            select(LeaveRequest).order_by(
                LeaveRequest.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_by_employee(
        self,
        db: AsyncSession,
        employee_id: UUID,
    ) -> list[LeaveRequest]:

        result = await db.execute(
            select(LeaveRequest)
            .where(
                LeaveRequest.employee_id == employee_id
            )
            .order_by(
                LeaveRequest.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        leave_request: LeaveRequest,
    ) -> LeaveRequest:

        await db.commit()
        await db.refresh(leave_request)

        return leave_request

    async def get_overlapping_leave(
        self,
        db: AsyncSession,
        employee_id: UUID,
        start_date: date,
        end_date: date,
    ) -> LeaveRequest | None:

        stmt = (
            select(LeaveRequest)
            .where(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status.in_(
                    [
                        LeaveStatus.PENDING,
                        LeaveStatus.APPROVED,
                    ]
                ),
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date,
            )
        )

        result = await db.execute(stmt)

        return result.scalars().first()

    async def get_used_leave_days(
        self,
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
    ) -> int:

        stmt = (
            select(func.sum(LeaveRequest.number_of_days))
            .where(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.leave_type_id == leave_type_id,
                LeaveRequest.status == LeaveStatus.APPROVED,
            )
        )

        result = await db.execute(stmt)

        return result.scalar() or 0