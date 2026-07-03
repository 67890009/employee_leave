from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import LeaveStatus
from app.leave_types.repository import LeaveTypeRepository
from app.reports.repository import ReportRepository
from app.reports.schema import (
    DepartmentReportResponse,
    EmployeeReportResponse,
    LeaveTypeReport,
    MonthlyReportResponse,
)
from app.users.model import User


class ReportService:

    def __init__(self):

        self.repository = ReportRepository()

        self.leave_type_repository = LeaveTypeRepository()

    async def get_employee_reports(
        self,
        db: AsyncSession,
        current_user: User,
        department_id: UUID | None = None,
        manager_id: UUID | None = None,
        employee_id: UUID | None = None,
        status: LeaveStatus | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[EmployeeReportResponse]:

        employees = await self.repository.get_accessible_employees(
            db=db,
            current_user=current_user,
            department_id=department_id,
            manager_id=manager_id,
            employee_id=employee_id,
            page=page,
            page_size=page_size,
        )

        reports = []

        leave_types = await self.leave_type_repository.get_all(db)

        total_paid_days = sum(
            leave_type.max_days_per_year
            for leave_type in leave_types
        )

        for employee in employees:

            total_requests = await self.repository.get_total_leave_requests(
                db,
                employee.id,
                status,
            )

            paid_used = await self.repository.get_paid_leave_used(
                db,
                employee.id,
                status if status else LeaveStatus.APPROVED,
            )

            breakdown = await self.repository.get_leave_type_breakdown(
                db,
                employee.id,
                status,
            )

            leave_breakdown = [
                LeaveTypeReport(
                    leave_type=name,
                    applied_count=count,
                )
                for name, count in breakdown
            ]

            reports.append(
                EmployeeReportResponse(
                    employee_id=str(employee.id),
                    employee_code=employee.employee_code,
                    employee_name=f"{employee.first_name} {employee.last_name}",
                    department=employee.department.name,
                    manager_name=(
                        f"{employee.manager.first_name} {employee.manager.last_name}"
                        if employee.manager
                        else None
                    ),
                    total_leave_requests=total_requests,
                    paid_leave_used=paid_used,
                    paid_leave_remaining=max(
                        total_paid_days - paid_used,
                        0,
                    ),
                    leave_breakdown=leave_breakdown,
                )
            )

        return reports

    async def get_department_reports(
        self,
        db: AsyncSession,
        current_user: User,
        department_id: UUID | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[DepartmentReportResponse]:

        employees = await self.repository.get_accessible_employees(
            db=db,
            current_user=current_user,
            department_id=department_id,
            page=page,
            page_size=page_size,
        )

        department_map = {}

        for employee in employees:

            department = employee.department.name

            if department not in department_map:

                department_map[department] = {
                    "department_id": str(employee.department.id),
                    "department_name": department,
                    "total_employees": 0,
                    "total_leave_requests": 0,
                    "paid_leave_used": 0,
                }

            department_map[department]["total_employees"] += 1

            department_map[department]["total_leave_requests"] += (
                await self.repository.get_total_leave_requests(
                    db,
                    employee.id,
                )
            )

            department_map[department]["paid_leave_used"] += (
                await self.repository.get_paid_leave_used(
                    db,
                    employee.id,
                )
            )

        reports = []

        for department in department_map.values():

            reports.append(
                DepartmentReportResponse(
                    department_id=department["department_id"],
                    department_name=department["department_name"],
                    total_employees=department["total_employees"],
                    total_leave_requests=department["total_leave_requests"],
                    paid_leave_used=department["paid_leave_used"],
                )
            )

        return reports

    async def get_monthly_report(
        self,
        db: AsyncSession,
        month: int,
        year: int,
    ) -> MonthlyReportResponse:

        (
            total_requests,
            paid_used,
            approved,
            pending,
            rejected,
            cancelled,
        ) = await self.repository.get_monthly_statistics(
            db,
            month,
            year,
        )

        return MonthlyReportResponse(
            month=month,
            year=year,
            total_leave_requests=total_requests or 0,
            approved_requests=approved or 0,
            pending_requests=pending or 0,
            rejected_requests=rejected or 0,
            cancelled_requests=cancelled or 0,
            paid_leave_used=paid_used or 0,
        )