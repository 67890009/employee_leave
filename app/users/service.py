from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.common.enums import UserRole
from app.users.model import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserProfileUpdate, UserUpdate


class UserService:

    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate) -> User:
        if await UserRepository.get_by_email(db, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered.",
            )

        if await UserRepository.get_by_employee_code(db, data.employee_code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee code already in use.",
            )

        if data.manager_id is not None:
            await UserService._validate_manager(db, data.manager_id)

        user = User(
            employee_code=data.employee_code,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
            department_id=data.department_id,
            manager_id=data.manager_id,
        )

        return await UserRepository.create(db, user)

    @staticmethod
    async def _validate_manager(db: AsyncSession, manager_id: UUID) -> User:
        manager = await UserRepository.get_by_id(db, manager_id)

        if manager is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned manager does not exist.",
            )

        if manager.role != UserRole.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned manager must have the MANAGER role.",
            )

        if not manager.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned manager is not active.",
            )

        return manager

    @staticmethod
    async def get_user(db: AsyncSession, user_id: UUID) -> User:
        user = await UserRepository.get_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, data: UserUpdate) -> User:
        user = await UserService.get_user(db, user_id)

        update_data = data.model_dump(exclude_unset=True)

        if "manager_id" in update_data and update_data["manager_id"] is not None:
            if update_data["manager_id"] == user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user cannot be their own manager.",
                )
            await UserService._validate_manager(db, update_data["manager_id"])

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_profile(db: AsyncSession, user: User, data: UserProfileUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: UUID) -> User:
        user = await UserService.get_user(db, user_id)

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already inactive.",
            )

        return await UserRepository.deactivate(db, user)

    @staticmethod
    async def list_users(
        db: AsyncSession,
        page: int,
        page_size: int,
        role: UserRole | None = None,
        department_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        return await UserRepository.list_users(
            db, page, page_size, role, department_id, is_active
        )