from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_employee, require_roles
from app.common.enums import LeaveStatus, UserRole
from app.db.session import get_db
from app.reports.schema import (
    DepartmentReportResponse,
    EmployeeReportResponse,
    MonthlyReportResponse,
)
from app.reports.service import ReportService
from app.users.model import User

router = APIRouter(prefix="/reports", tags=["Reports"])
service = ReportService()


@router.get("/employees", response_model=list[EmployeeReportResponse])
async def get_employee_reports(
    department_id: UUID | None = None,
    manager_id: UUID | None = None,
    employee_id: UUID | None = None,
    status: LeaveStatus | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_employee_reports(
        db=db, current_user=current_user, department_id=department_id,
        manager_id=manager_id, employee_id=employee_id, status=status,
        page=page, page_size=page_size,
    )


@router.get("/departments", response_model=list[DepartmentReportResponse])
async def get_department_reports(
    department_id: UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_department_reports(
        db=db, current_user=current_user, department_id=department_id,
        page=page, page_size=page_size,
    )


@router.get("/monthly", response_model=MonthlyReportResponse)
async def get_monthly_report(
    month: int,
    year: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_monthly_report(db, month, year)