from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.common.enums import UserRole


class UserCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=20)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole
    department_id: UUID
    manager_id: UUID | None = None


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    role: UserRole | None = None
    department_id: UUID | None = None
    manager_id: UUID | None = None
    is_active: bool | None = None


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    department_id: UUID
    manager_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginatedUserResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int