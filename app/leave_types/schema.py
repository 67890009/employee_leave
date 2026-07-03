from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LeaveTypeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    max_days_per_year: int = Field(..., gt=0)


class LeaveTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    max_days_per_year: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class LeaveTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    max_days_per_year: int
    is_active: bool