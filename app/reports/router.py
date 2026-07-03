from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_employee
from app.db.session import get_db
from app.reports.schema import (
    DepartmentReportResponse,
    EmployeeReportResponse,
    MonthlyReportResponse,
)
from app.reports.service import ReportService
from app.users.model import User

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

service = ReportService()


@router.get(
    "/employees",
    response_model=list[EmployeeReportResponse],
)
async def get_employee_reports(
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):

    return await service.get_employee_reports(
        db,
        current_user,
    )


@router.get(
    "/departments",
    response_model=list[DepartmentReportResponse],
)
async def get_department_reports(
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):

    return await service.get_department_reports(
        db,
        current_user,
    )


@router.get(
    "/monthly",
    response_model=MonthlyReportResponse,
)
async def get_monthly_report(
    month: int,
    year: int,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):

    return await service.get_monthly_report(
        db,
        month,
        year,
    )