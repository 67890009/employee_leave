from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin, get_current_user
from app.common.enums import UserRole
from app.db.session import get_db
from app.users.model import User
from app.users.schemas import (
    PaginatedUserResponse,
    UserCreate,
    UserProfileUpdate,
    UserResponse,
    UserUpdate,
)
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService.update_profile(db, current_user, data)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await UserService.create_user(db, data)


@router.get("", response_model=PaginatedUserResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: UserRole | None = None,
    department_id: UUID | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    users, total = await UserService.list_users(
        db, page, page_size, role, department_id, is_active
    )
    return PaginatedUserResponse(
        items=users, total=total, page=page, page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await UserService.get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await UserService.update_user(db, user_id, data)


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await UserService.deactivate_user(db, user_id)