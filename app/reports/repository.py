from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.enums import LeaveStatus
from app.leave_requests.model import LeaveRequest
from app.leave_types.model import LeaveType
from app.users.model import User


class ReportRepository:

    async def get_accessible_employees(
        self,
        db: AsyncSession,
        current_user: User,
        department_id: UUID | None = None,
        manager_id: UUID | None = None,
        employee_id: UUID | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[User]:

        stmt = (
            select(User)
            .options(
                selectinload(User.department),
                selectinload(User.manager),
            )
        )

        # -----------------------------
        # Role Based Access
        # -----------------------------

        if current_user.role.name in ["ADMIN", "HR"]:
            pass

        elif current_user.role.name == "MANAGER":
            stmt = stmt.where(
                User.manager_id == current_user.id
            )

        else:
            stmt = stmt.where(
                User.id == current_user.id
            )

        # -----------------------------
        # Filters
        # -----------------------------

        if department_id:
            stmt = stmt.where(
                User.department_id == department_id
            )

        if manager_id:
            stmt = stmt.where(
                User.manager_id == manager_id
            )

        if employee_id:
            stmt = stmt.where(
                User.id == employee_id
            )

        # -----------------------------
        # Pagination
        # -----------------------------

        stmt = (
            stmt
            .order_by(User.first_name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def get_leave_type_breakdown(
        self,
        db: AsyncSession,
        employee_id: UUID,
        status: LeaveStatus | None = None,
    ):

        stmt = (
            select(
                LeaveType.name,
                func.count(LeaveRequest.id),
            )
            .join(
                LeaveRequest,
                LeaveType.id == LeaveRequest.leave_type_id,
            )
            .where(
                LeaveRequest.employee_id == employee_id,
            )
        )

        if status:
            stmt = stmt.where(
                LeaveRequest.status == status
            )

        stmt = stmt.group_by(
            LeaveType.name,
        )

        result = await db.execute(stmt)

        return result.all()

    async def get_paid_leave_used(
        self,
        db: AsyncSession,
        employee_id: UUID,
        status: LeaveStatus = LeaveStatus.APPROVED,
    ):

        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (
                                LeaveRequest.status == status,
                                LeaveRequest.number_of_days,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                )
            )
            .where(
                LeaveRequest.employee_id == employee_id,
            )
        )

        result = await db.execute(stmt)

        return result.scalar() or 0

    async def get_total_leave_requests(
        self,
        db: AsyncSession,
        employee_id: UUID,
        status: LeaveStatus | None = None,
    ):

        stmt = (
            select(
                func.count(
                    LeaveRequest.id,
                )
            )
            .where(
                LeaveRequest.employee_id == employee_id,
            )
        )

        if status:
            stmt = stmt.where(
                LeaveRequest.status == status
            )

        result = await db.execute(stmt)

        return result.scalar() or 0

    async def get_monthly_statistics(
        self,
        db: AsyncSession,
        month: int,
        year: int,
    ):

        stmt = (
            select(

                func.count(
                    LeaveRequest.id,
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                LeaveRequest.status == LeaveStatus.APPROVED,
                                LeaveRequest.number_of_days,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                LeaveRequest.status == LeaveStatus.APPROVED,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                LeaveRequest.status == LeaveStatus.PENDING,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                LeaveRequest.status == LeaveStatus.REJECTED,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                LeaveRequest.status == LeaveStatus.CANCELLED,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),

            )
            .where(
                func.extract(
                    "month",
                    LeaveRequest.start_date,
                ) == month,
                func.extract(
                    "year",
                    LeaveRequest.start_date,
                ) == year,
            )
        )

        result = await db.execute(stmt)

        return result.first()