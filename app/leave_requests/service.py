from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.model import User
from app.common.enums import LeaveStatus, UserRole
from app.leave_requests.model import LeaveRequest
from app.leave_requests.repository import LeaveRequestRepository
from app.leave_requests.schema import LeaveRequestCreate, LeaveApprovalRequest
from app.leave_types.repository import LeaveTypeRepository


class LeaveRequestService:

    def __init__(self):
        self.repository = LeaveRequestRepository()
        self.leave_type_repository = LeaveTypeRepository()

    async def apply_leave(
        self, db: AsyncSession, current_user: User, data: LeaveRequestCreate,
    ) -> LeaveRequest:
        overlapping_leave = await self.repository.get_overlapping_leave(
            db, current_user.id, data.start_date, data.end_date,
        )
        if overlapping_leave:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request overlaps with an existing leave.",
            )

        leave_type = await self.leave_type_repository.get_by_id(db, data.leave_type_id)
        if leave_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave type not found.")

        if not leave_type.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This leave type is no longer active.",
            )

        if data.start_date > data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must not be after end date.",
            )

        if data.number_of_days > leave_type.max_days_per_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum allowed is {leave_type.max_days_per_year} days.",
            )

        used_days = await self.repository.get_used_leave_days(db, current_user.id, data.leave_type_id)
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
        return await self.repository.create(db, leave_request)

    async def get_leave_request(
        self, db: AsyncSession, leave_request_id: UUID, current_user: User,
    ) -> LeaveRequest:
        leave_request = await self.repository.get_by_id(db, leave_request_id)
        if leave_request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")

        self._check_view_permission(leave_request, current_user)
        return leave_request

    def _check_view_permission(self, leave_request: LeaveRequest, current_user: User) -> None:
        if current_user.role in (UserRole.ADMIN, UserRole.HR):
            return
        if leave_request.employee_id == current_user.id:
            return
        if current_user.role == UserRole.MANAGER and leave_request.employee.manager_id == current_user.id:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this leave request.",
        )

    async def get_all_leave_requests(self, db: AsyncSession, current_user: User) -> list[LeaveRequest]:
        if current_user.role in (UserRole.ADMIN, UserRole.HR):
            return await self.repository.get_all(db)
        return await self.repository.get_by_manager_team(db, current_user.id)

    async def get_employee_leave_requests(self, db: AsyncSession, employee_id: UUID) -> list[LeaveRequest]:
        return await self.repository.get_by_employee(db, employee_id)

    async def cancel_leave_request(
        self, db: AsyncSession, leave_request_id: UUID, current_user: User,
    ) -> LeaveRequest:
        leave_request = await self.repository.get_by_id(db, leave_request_id)
        if leave_request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")

        if leave_request.employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own leave requests.",
            )

        if leave_request.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be cancelled.",
            )

        leave_request.status = LeaveStatus.CANCELLED
        return await self.repository.update(db, leave_request)

    async def approve_leave(
        self, db: AsyncSession, leave_request_id: UUID, current_user: User, data: LeaveApprovalRequest,
    ) -> LeaveRequest:
        return await self._process_approval(db, leave_request_id, current_user, data, LeaveStatus.APPROVED)

    async def reject_leave(
        self, db: AsyncSession, leave_request_id: UUID, current_user: User, data: LeaveApprovalRequest,
    ) -> LeaveRequest:
        return await self._process_approval(db, leave_request_id, current_user, data, LeaveStatus.REJECTED)

    async def _process_approval(
        self,
        db: AsyncSession,
        leave_request_id: UUID,
        current_user: User,
        data: LeaveApprovalRequest,
        new_status: LeaveStatus,
    ) -> LeaveRequest:
        leave_request = await self.repository.get_by_id(db, leave_request_id)
        if leave_request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")

        if leave_request.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be processed.",
            )

        # Rule 7: nobody approves their own leave, regardless of role.
        if leave_request.employee_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot approve or reject your own leave request.",
            )

        target_role = leave_request.employee.role

        if target_role == UserRole.EMPLOYEE:
            # Rule 6: only the employee's own manager may act, no one else.
            if current_user.role != UserRole.MANAGER or leave_request.employee.manager_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only this employee's manager can approve or reject their leave.",
                )
        elif target_role == UserRole.MANAGER:
            # A manager's own leave escalates to Admin - no manager approves a peer.
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="A manager's leave request can only be approved by an Admin.",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This user's role does not support leave approval.",
            )

        leave_request.status = new_status
        leave_request.manager_comment = data.manager_comment
        leave_request.approved_by = current_user.id
        leave_request.approved_at = datetime.utcnow()

        return await self.repository.update(db, leave_request)