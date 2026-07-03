from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import LeaveStatus


class LeaveRequestCreate(BaseModel):

    leave_type_id: UUID

    start_date: date

    end_date: date

    number_of_days: int = Field(
        ...,
        gt=0,
    )

    reason: str = Field(
        ...,
        min_length=5,
        max_length=500,
    )


class LeaveRequestUpdate(BaseModel):

    start_date: date | None = None

    end_date: date | None = None

    number_of_days: int | None = Field(
        default=None,
        gt=0,
    )

    reason: str | None = Field(
        default=None,
        min_length=5,
        max_length=500,
    )


class LeaveApprovalRequest(BaseModel):

    manager_comment: str | None = Field(
        default=None,
        max_length=500,
    )


class LeaveRequestResponse(BaseModel):

    id: UUID

    employee_id: UUID

    leave_type_id: UUID

    start_date: date

    end_date: date

    number_of_days: int

    reason: str

    status: LeaveStatus

    manager_comment: str | None

    approved_by: UUID | None

    approved_at: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )