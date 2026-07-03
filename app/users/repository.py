from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import UserRole
from app.users.model import User


class UserRepository:

    @staticmethod
    async def create(db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_employee_code(db: AsyncSession, employee_code: str) -> User | None:
        result = await db.execute(
            select(User).where(User.employee_code == employee_code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_users(
        db: AsyncSession,
        page: int,
        page_size: int,
        role: UserRole | None = None,
        department_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        query = select(User)
        count_query = select(func.count()).select_from(User)

        if role is not None:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)

        if department_id is not None:
            query = query.where(User.department_id == department_id)
            count_query = count_query.where(User.department_id == department_id)

        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)

        total = (await db.execute(count_query)).scalar_one()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)

        return list(result.scalars().all()), total

    @staticmethod
    async def deactivate(db: AsyncSession, user: User) -> User:
        user.is_active = False
        await db.flush()
        await db.refresh(user)
        return user