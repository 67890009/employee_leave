from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin, get_current_user
from app.db.session import get_db
from app.departments.schema import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    PaginatedDepartmentResponse,
)
from app.departments.service import DepartmentService
from app.users.model import User

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await DepartmentService.create_department(db, data)


@router.get("", response_model=PaginatedDepartmentResponse)
async def list_departments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    departments, total = await DepartmentService.list_departments(
        db, page, page_size, is_active
    )
    return PaginatedDepartmentResponse(
        items=departments, total=total, page=page, page_size=page_size
    )


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await DepartmentService.get_department(db, department_id)


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: UUID,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await DepartmentService.update_department(db, department_id, data)


@router.delete("/{department_id}", response_model=DepartmentResponse)
async def deactivate_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await DepartmentService.deactivate_department(db, department_id)