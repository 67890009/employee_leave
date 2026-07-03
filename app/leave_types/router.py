from uuid import UUID

from  app.auth.dependencies import (
    get_current_employee,
    get_current_manager,
)
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.users.model import User
from app.leave_types.schema import (
    LeaveTypeCreate,
    LeaveTypeUpdate,
    LeaveTypeResponse,
)
from app.leave_types.service import LeaveTypeService

router = APIRouter(
    prefix="/leave-types",
    tags=["Leave Types"],
)

service = LeaveTypeService()


@router.post(
    "/",
    response_model=LeaveTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_leave_type(
    data: LeaveTypeCreate,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_leave_type(db, data)


@router.get(
    "/",
    response_model=list[LeaveTypeResponse],
)
async def get_leave_types(
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_all_leave_types(db)


@router.get(
    "/{leave_type_id}",
    response_model=LeaveTypeResponse,
)
async def get_leave_type(
    leave_type_id: UUID,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_leave_type(db, leave_type_id)


@router.put(
    "/{leave_type_id}",
    response_model=LeaveTypeResponse,
)
async def update_leave_type(
    leave_type_id: UUID,
    data: LeaveTypeUpdate,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_leave_type(
        db,
        leave_type_id,
        data,
    )


@router.delete(
    "/{leave_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_leave_type(
    leave_type_id: UUID,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_leave_type(
        db,
        leave_type_id,
    )