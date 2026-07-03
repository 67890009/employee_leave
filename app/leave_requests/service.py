from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.model import User
from app.common.enums import LeaveStatus
from app.leave_requests.model import LeaveRequest
from app.leave_requests.repository import LeaveRequestRepository
from app.leave_requests.schema import (
    LeaveRequestCreate,
    LeaveApprovalRequest,
)
from app.leave_types.repository import LeaveTypeRepository


class LeaveRequestService:

    def __init__(self):
        self.repository = LeaveRequestRepository()
        self.leave_type_repository = LeaveTypeRepository()

    async def apply_leave(
        self,
        db: AsyncSession,
        current_user: User,
        data: LeaveRequestCreate,
    ) -> LeaveRequest:

        # Check overlapping leave
        overlapping_leave = await self.repository.get_overlapping_leave(
            db,
            current_user.id,
            data.start_date,
            data.end_date,
        )

        if overlapping_leave:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request overlaps with an existing leave.",
            )

        # Get leave type
        leave_type = await self.leave_type_repository.get_by_id(
            db,
            data.leave_type_id,
        )

        if leave_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave type not found.",
            )

        # Maximum leave validation
        if data.number_of_days > leave_type.max_days_per_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum allowed is {leave_type.max_days_per_year} days.",
            )

        # Remaining leave validation
        used_days = await self.repository.get_used_leave_days(
            db,
            current_user.id,
            data.leave_type_id,
        )

        remaining_days = leave_type.max_days_per_year - used_days

        if data.number_of_days > remaining_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {remaining_days} leave days remaining.",
            )

        leave_request = LeaveRequest(
            employee_id=current_user.id,
            leave_type_id=data.leave_type_id,
            start_date=data.start_date,
            end_date=data.end_date,
            number_of_days=data.number_of_days,
            reason=data.reason,
        )

        return await self.repository.create(
            db,
            leave_request,
        )

    async def get_leave_request(
        self,
        db: AsyncSession,
        leave_request_id: UUID,
    ) -> LeaveRequest:

        leave_request = await self.repository.get_by_id(
            db,
            leave_request_id,
        )

        if leave_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found.",
            )

        return leave_request

    async def get_all_leave_requests(
        self,
        db: AsyncSession,
    ) -> list[LeaveRequest]:

        return await self.repository.get_all(db)

    async def get_employee_leave_requests(
        self,
        db: AsyncSession,
        employee_id: UUID,
    ) -> list[LeaveRequest]:

        return await self.repository.get_by_employee(
            db,
            employee_id,
        )

    async def cancel_leave_request(
        self,
        db: AsyncSession,
        leave_request_id: UUID,
    ) -> LeaveRequest:

        leave_request = await self.repository.get_by_id(
            db,
            leave_request_id,
        )

        if leave_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found.",
            )

        leave_request.status = LeaveStatus.CANCELLED

        return await self.repository.update(
            db,
            leave_request,
        )

    async def approve_leave(
        self,
        db: AsyncSession,
        leave_request_id: UUID,
        current_manager: User,
        data: LeaveApprovalRequest,
    ) -> LeaveRequest:

        leave_request = await self.repository.get_by_id(
            db,
            leave_request_id,
        )

        if leave_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found.",
            )

        if leave_request.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be processed.",
            )

        leave_request.status = LeaveStatus.APPROVED
        leave_request.manager_comment = data.manager_comment
        leave_request.approved_by = current_manager.id
        leave_request.approved_at = datetime.utcnow()

        return await self.repository.update(
            db,
            leave_request,
        )

    async def reject_leave(
        self,
        db: AsyncSession,
        leave_request_id: UUID,
        current_manager: User,
        data: LeaveApprovalRequest,
    ) -> LeaveRequest:

        leave_request = await self.repository.get_by_id(
            db,
            leave_request_id,
        )

        if leave_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found.",
            )

        if leave_request.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be processed.",
            )

        leave_request.status = LeaveStatus.REJECTED
        leave_request.manager_comment = data.manager_comment
        leave_request.approved_by = current_manager.id
        leave_request.approved_at = datetime.utcnow()

        return await self.repository.update(
            db,
            leave_request,
        )