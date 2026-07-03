from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_current_employee,
    get_current_manager,
)
from app.db.session import get_db
from app.users.model import User

from app.leave_requests.schema import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveApprovalRequest,
)
from app.leave_requests.service import LeaveRequestService


router = APIRouter(
    prefix="/leave-requests",
    tags=["Leave Requests"],
)

service = LeaveRequestService()


@router.post(
    "/",
    response_model=LeaveRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def apply_leave(
    data: LeaveRequestCreate,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.apply_leave(
        db,
        current_user,
        data,
    )


@router.get(
    "/",
    response_model=list[LeaveRequestResponse],
)
async def get_all_leave_requests(
    current_manager: User = Depends(get_current_manager),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_all_leave_requests(
        db,
    )


@router.get(
    "/my-leaves",
    response_model=list[LeaveRequestResponse],
)
async def get_my_leave_requests(
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_employee_leave_requests(
        db,
        current_user.id,
    )


@router.get(
    "/{leave_request_id}",
    response_model=LeaveRequestResponse,
)
async def get_leave_request(
    leave_request_id: UUID,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_leave_request(
        db,
        leave_request_id,
    )


@router.patch(
    "/{leave_request_id}/cancel",
    response_model=LeaveRequestResponse,
)
async def cancel_leave_request(
    leave_request_id: UUID,
    current_user: User = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db),
):
    return await service.cancel_leave_request(
        db,
        leave_request_id,
    )


@router.patch(
    "/{leave_request_id}/approve",
    response_model=LeaveRequestResponse,
)
async def approve_leave(
    leave_request_id: UUID,
    data: LeaveApprovalRequest,
    current_manager: User = Depends(get_current_manager),
    db: AsyncSession = Depends(get_db),
):
    return await service.approve_leave(
        db,
        leave_request_id,
        current_manager,
        data,
    )


@router.patch(
    "/{leave_request_id}/reject",
    response_model=LeaveRequestResponse,
)
async def reject_leave(
    leave_request_id: UUID,
    data: LeaveApprovalRequest,
    current_manager: User = Depends(get_current_manager),
    db: AsyncSession = Depends(get_db),
):
    return await service.reject_leave(
        db,
        leave_request_id,
        current_manager,
        data,
    )